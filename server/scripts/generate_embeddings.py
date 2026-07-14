"""
Index NATA FAQ + website markdown into Qdrant with Gemini embeddings.

Usage (venv active, from project root):
  cd server
  python scripts/generate_embeddings.py
  python scripts/generate_embeddings.py --reset
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import uuid
from pathlib import Path

# Allow `python scripts/generate_embeddings.py` from server/
SERVER_DIR = Path(__file__).resolve().parent.parent
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from config import get_settings
from gemini_client import embed_text

DATA_DIR = SERVER_DIR / "data"
WEBSITE_DIR = DATA_DIR / "nata-website-data"
FAQ_PATH = DATA_DIR / "nata_faqs.json"
UPSERT_BATCH_SIZE = 16
UPSERT_MAX_ATTEMPTS = 5


def get_website_chunks() -> list[dict[str, str]]:
    chunks: list[dict[str, str]] = []
    if not WEBSITE_DIR.exists():
        return chunks

    for path in sorted(WEBSITE_DIR.glob("*.md")):
        content = path.read_text(encoding="utf-8")
        sections = re.split(r"^(?=#{2,3} )", content, flags=re.MULTILINE)
        for section in sections:
            section = section.strip()
            if not section:
                continue
            lines = section.split("\n")
            heading = re.sub(r"^#+\s*", "", lines[0]).strip()
            body = "\n".join(lines[1:]).strip()
            chunks.append({"text": f"{heading}\n\n{body}", "source": "website"})
    return chunks


def get_faq_chunks() -> list[dict[str, str]]:
    data = json.loads(FAQ_PATH.read_text(encoding="utf-8"))
    chunks: list[dict[str, str]] = []
    for faq in data.get("faqs", []):
        question = faq.get("question", "").strip()
        answer = faq.get("answer", "").strip()
        if question and answer:
            chunks.append({"text": f"{question}\n{answer}", "source": "faqs"})
    return chunks


def ensure_collection(client: QdrantClient, name: str, dimensions: int) -> None:
    try:
        client.create_collection(
            collection_name=name,
            vectors_config=qmodels.VectorParams(
                size=dimensions,
                distance=qmodels.Distance.COSINE,
            ),
        )
        print(f'[Qdrant] Collection "{name}" created.')
    except Exception as exc:
        msg = str(exc).lower()
        if "already" in msg or "conflict" in msg or "409" in msg:
            print(f'[Qdrant] Collection "{name}" already exists, skipping creation.')
        else:
            raise


def upsert_in_batches(
    client: QdrantClient,
    collection: str,
    points: list[qmodels.PointStruct],
    batch_size: int = UPSERT_BATCH_SIZE,
) -> None:
    total = len(points)
    for start in range(0, total, batch_size):
        batch = points[start : start + batch_size]
        end = start + len(batch)
        last_error: Exception | None = None
        for attempt in range(1, UPSERT_MAX_ATTEMPTS + 1):
            try:
                client.upsert(collection_name=collection, points=batch, wait=True)
                print(f"  [Qdrant] upserted {end}/{total}")
                last_error = None
                break
            except Exception as exc:
                last_error = exc
                wait_s = min(2 ** attempt, 20)
                print(
                    f"  [Qdrant] upsert {start + 1}-{end} failed "
                    f"(attempt {attempt}/{UPSERT_MAX_ATTEMPTS}): {exc}"
                )
                if attempt < UPSERT_MAX_ATTEMPTS:
                    print(f"  retrying in {wait_s}s...")
                    time.sleep(wait_s)
        if last_error is not None:
            raise last_error


def main() -> None:
    parser = argparse.ArgumentParser(description="Embed NATA knowledge into Qdrant")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete and recreate the Qdrant collection before indexing",
    )
    args = parser.parse_args()

    settings = get_settings()
    if not settings["google_api_key"]:
        raise SystemExit("GOOGLE_GENERATIVE_AI_API_KEY is required")
    if not settings["qdrant_url"]:
        raise SystemExit("QDRANT_URL is required")

    client = QdrantClient(
        url=settings["qdrant_url"],
        api_key=settings["qdrant_api_key"] or None,
        timeout=120,
    )
    collection = settings["qdrant_collection_name"]
    dims = settings["embedding_dimensions"]

    if args.reset:
        try:
            client.delete_collection(collection)
            print(f'[Qdrant] Collection "{collection}" deleted.')
        except Exception:
            print("[Qdrant] Collection did not exist, skipping delete.")

    ensure_collection(client, collection, dims)

    all_chunks = get_website_chunks() + get_faq_chunks()
    if not all_chunks:
        raise SystemExit(f"No chunks found under {DATA_DIR}")

    print(f"Embedding {len(all_chunks)} chunks...")
    points: list[qmodels.PointStruct] = []
    for i, chunk in enumerate(all_chunks, start=1):
        vector = embed_text(chunk["text"])
        points.append(
            qmodels.PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={"text": chunk["text"], "source": chunk["source"]},
            )
        )
        print(f"  [{i}/{len(all_chunks)}] embedded ({chunk['source']})")

    print(f"Upserting {len(points)} points in batches of {UPSERT_BATCH_SIZE}...")
    upsert_in_batches(client, collection, points)
    print(f"[Qdrant] Upserted {len(points)} points into '{collection}'. Done.")


if __name__ == "__main__":
    main()
