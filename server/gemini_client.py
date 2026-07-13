"""Thin Gemini client helpers used by router, RAG, and chat agents."""

from __future__ import annotations

import json
import re
from collections.abc import Iterator
from typing import Any

from google import genai
from google.genai import types

from config import get_settings

_client: genai.Client | None = None


def get_genai_client() -> genai.Client:
    global _client
    if _client is None:
        settings = get_settings()
        api_key = settings["google_api_key"]
        if not api_key:
            raise RuntimeError(
                "GOOGLE_GENERATIVE_AI_API_KEY is missing. Add it to the root .env file."
            )
        _client = genai.Client(api_key=api_key)
    return _client


def generate_text(
    *,
    system: str | None = None,
    contents: str | list[types.Content],
    temperature: float = 0.0,
    max_output_tokens: int | None = None,
    model: str | None = None,
) -> str:
    settings = get_settings()
    client = get_genai_client()
    config_kwargs: dict[str, Any] = {"temperature": temperature}
    if system:
        config_kwargs["system_instruction"] = system
    if max_output_tokens is not None:
        config_kwargs["max_output_tokens"] = max_output_tokens

    response = client.models.generate_content(
        model=model or settings["chat_model"],
        contents=contents,
        config=types.GenerateContentConfig(**config_kwargs),
    )
    return (response.text or "").strip()


def stream_text(
    *,
    system: str | None = None,
    contents: str | list[types.Content],
    temperature: float = 0.0,
    max_output_tokens: int | None = None,
    model: str | None = None,
) -> Iterator[str]:
    settings = get_settings()
    client = get_genai_client()
    config_kwargs: dict[str, Any] = {"temperature": temperature}
    if system:
        config_kwargs["system_instruction"] = system
    if max_output_tokens is not None:
        config_kwargs["max_output_tokens"] = max_output_tokens

    stream = client.models.generate_content_stream(
        model=model or settings["chat_model"],
        contents=contents,
        config=types.GenerateContentConfig(**config_kwargs),
    )
    for chunk in stream:
        text = getattr(chunk, "text", None)
        if text:
            yield text


def embed_text(text: str) -> list[float]:
    settings = get_settings()
    client = get_genai_client()
    result = client.models.embed_content(
        model=settings["embedding_model"],
        contents=text,
        config=types.EmbedContentConfig(
            output_dimensionality=settings["embedding_dimensions"],
        ),
    )
    # google-genai returns embeddings list
    embedding = result.embeddings[0].values
    return list(embedding)


def parse_json_object(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned)
