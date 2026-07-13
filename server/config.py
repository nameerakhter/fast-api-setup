"""Load and validate environment variables for the NATA chatbot server."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


@lru_cache
def get_settings() -> dict:
    mongodb_uri = os.getenv("MONGODB_URI") or os.getenv(
        "DATABASE_URL", "mongodb://127.0.0.1:27017/nata_chatbot"
    )
    cors_origin = os.getenv("CORS_ORIGIN", "http://localhost:8501")
    embedding_dims = int(os.getenv("EMBEDDING_DIMENSIONS", "768"))
    rate_window = int(os.getenv("RATE_LIMIT_WINDOW_MS", "3600000"))
    rate_max = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "25"))

    return {
        "app_env": os.getenv("APP_ENV", "development"),
        "mongodb_uri": mongodb_uri,
        "google_api_key": os.getenv("GOOGLE_GENERATIVE_AI_API_KEY", ""),
        "qdrant_url": os.getenv("QDRANT_URL", ""),
        "qdrant_api_key": os.getenv("QDRANT_API_KEY", ""),
        "qdrant_collection_name": os.getenv(
            "QDRANT_COLLECTION_NAME", "nata_knowledge"
        ),
        "embedding_model": os.getenv("EMBEDDING_MODEL", "gemini-embedding-001"),
        "embedding_dimensions": embedding_dims,
        "chat_model": os.getenv("CHAT_MODEL", "gemini-2.5-flash"),
        "cors_origin": cors_origin,
        "redis_url": os.getenv("REDIS_URL", ""),
        "rate_limit_window_ms": rate_window,
        "rate_limit_max_requests": rate_max,
    }
