"""Qdrant RAG retrieve (+ optional one-shot answer) for NATA knowledge."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse

from agent.prompts import HINDI_SEARCH_REWRITE_PROMPT, RAG_BASE_PROMPT
from config import get_settings
from gemini_client import embed_text, generate_text


@dataclass
class RetrievedChunk:
    text: str
    score: float


class RAGService:
    def __init__(
        self,
        *,
        language_preference: str = "english",
        limit: int = 5,
        score_threshold: float = 0.6,
    ) -> None:
        settings = get_settings()
        self.language_preference = language_preference
        self.limit = limit
        self.score_threshold = score_threshold
        self.collection = settings["qdrant_collection_name"]
        self._client = QdrantClient(
            url=settings["qdrant_url"],
            api_key=settings["qdrant_api_key"] or None,
        )

    def _search_query_for_embedding(self, raw_query: str) -> str:
        if self.language_preference != "hindi":
            return raw_query
        prompt = HINDI_SEARCH_REWRITE_PROMPT.format(raw_query=raw_query)
        try:
            rewritten = generate_text(contents=prompt, temperature=0.0)
            return rewritten or raw_query
        except Exception:
            return raw_query

    def _retrieve_chunks(self, query: str) -> list[RetrievedChunk]:
        vector = embed_text(query)
        try:
            # Prefer query_points (newer qdrant-client); fall back to search.
            if hasattr(self._client, "query_points"):
                response = self._client.query_points(
                    collection_name=self.collection,
                    query=vector,
                    limit=self.limit,
                    score_threshold=self.score_threshold,
                    with_payload=True,
                )
                results = response.points
            else:
                results = self._client.search(
                    collection_name=self.collection,
                    query_vector=vector,
                    limit=self.limit,
                    score_threshold=self.score_threshold,
                    with_payload=True,
                )
        except UnexpectedResponse as exc:
            raise RuntimeError(
                f"Qdrant search failed for collection '{self.collection}': {exc}"
            ) from exc

        chunks: list[RetrievedChunk] = []
        for result in results:
            payload = result.payload or {}
            text = payload.get("text")
            if isinstance(text, str) and text.strip():
                chunks.append(
                    RetrievedChunk(text=text, score=float(result.score or 0.0))
                )
        return chunks

    def retrieve(self, query: str) -> list[RetrievedChunk]:
        query_for_rag = self._search_query_for_embedding(query)
        return self._retrieve_chunks(query_for_rag)

    def query(self, user_query: str) -> str:
        is_hindi = self.language_preference == "hindi"
        query_for_rag = self._search_query_for_embedding(user_query)
        chunks = self._retrieve_chunks(query_for_rag)

        if not chunks:
            return (
                "मुझे आपके प्रश्न का उत्तर देने के लिए कोई प्रासंगिक जानकारी नहीं मिली।"
                if is_hindi
                else "I could not find any relevant information to answer your question."
            )

        context = "\n\n".join(
            f"[{i}] {chunk.text}" for i, chunk in enumerate(chunks, start=1)
        )
        prompt = (
            f"{RAG_BASE_PROMPT}\n\n"
            f"RETRIEVED CONTEXT:\n{context}\n\n"
            f"USER QUESTION: {user_query}\n"
            f"{'- Answer in Hindi' if is_hindi else '- Answer in English'}"
        )
        return generate_text(contents=prompt, temperature=0.0)


@lru_cache(maxsize=8)
def create_rag_service(
    language_preference: str = "english",
    limit: int = 5,
    score_threshold: float = 0.6,
) -> RAGService:
    return RAGService(
        language_preference=language_preference,
        limit=limit,
        score_threshold=score_threshold,
    )
