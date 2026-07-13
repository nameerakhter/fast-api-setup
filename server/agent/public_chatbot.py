"""Public NATA chatbot: router gate → RAG retrieve → streamed answer."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from agent.prompts import (
    PUBLIC_CHATBOT_SYSTEM_PROMPT,
    REFUSAL_SYSTEM_PROMPT,
    REFUSAL_USER_PROMPT_EN,
    REFUSAL_USER_PROMPT_HI,
)
from agent.router import router_agent
from gemini_client import stream_text
from rag import create_rag_service


def _extract_text(message: dict[str, Any]) -> str:
    content = message.get("content")
    if isinstance(content, str):
        return content
    parts = message.get("parts")
    if isinstance(parts, list):
        texts = []
        for part in parts:
            if isinstance(part, dict) and part.get("type") == "text":
                texts.append(str(part.get("text", "")))
            elif isinstance(part, str):
                texts.append(part)
        return "\n".join(texts)
    if isinstance(content, list):
        texts = []
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                texts.append(str(part.get("text", "")))
            elif isinstance(part, str):
                texts.append(part)
        return "\n".join(texts)
    return str(content or "")


def _normalize_messages(messages: list[dict[str, Any]]) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for message in messages:
        role = message.get("role", "user")
        if role not in {"user", "assistant", "system"}:
            continue
        text = _extract_text(message).strip()
        if not text:
            continue
        normalized.append({"role": role, "content": text})
    return normalized


def _search_knowledge_base(query: str, language_preference: str) -> str:
    rag = create_rag_service(language_preference=language_preference)
    chunks = rag.retrieve(query)
    return "\n\n".join(chunk.text for chunk in chunks)


def stream_public_chat_reply(
    messages: list[dict[str, Any]],
    *,
    language_preference: str = "english",
) -> Iterator[str]:
    """Yield assistant text tokens (plain UTF-8 chunks)."""
    normalized = _normalize_messages(messages)
    if not normalized:
        yield (
            "कृपया NATA 2026 से जुड़ा प्रश्न लिखें।"
            if language_preference == "hindi"
            else "Please ask a question about NATA 2026."
        )
        return

    routed = router_agent(normalized)
    if not routed.get("isRelevant"):
        refusal_user = (
            REFUSAL_USER_PROMPT_HI
            if language_preference == "hindi"
            else REFUSAL_USER_PROMPT_EN
        )
        yield from stream_text(
            system=REFUSAL_SYSTEM_PROMPT,
            contents=refusal_user,
            temperature=0.0,
            max_output_tokens=180,
        )
        return

    latest_user = next(
        (m["content"] for m in reversed(normalized) if m["role"] == "user"),
        "",
    )
    context = _search_knowledge_base(latest_user, language_preference)
    language_line = (
        "Answer in Hindi."
        if language_preference == "hindi"
        else "Answer in English."
    )

    history_block = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in normalized[-8:]
    )
    user_prompt = (
        f"{language_line}\n\n"
        f"KNOWLEDGE LOOKUP RESULTS:\n{context or '(no matching material)'}\n\n"
        f"CONVERSATION:\n{history_block}\n\n"
        "Write the help-desk reply now. Use only the lookup results above."
    )

    yield from stream_text(
        system=PUBLIC_CHATBOT_SYSTEM_PROMPT,
        contents=user_prompt,
        temperature=0.2,
    )


def generate_public_chat_reply(
    messages: list[dict[str, Any]],
    *,
    language_preference: str = "english",
) -> str:
    return "".join(
        stream_public_chat_reply(messages, language_preference=language_preference)
    )
