"""Relevance router gate before the public NATA chatbot answers."""

from __future__ import annotations

import re
from typing import Any

from google.genai import types

from agent.prompts import ROUTER_SYSTEM_PROMPT
from config import get_settings
from gemini_client import get_genai_client, parse_json_object


def _history_to_text(messages: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for message in messages:
        role = message.get("role", "user")
        content = message.get("content", "")
        if isinstance(content, list):
            parts = []
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    parts.append(str(part.get("text", "")))
                elif isinstance(part, str):
                    parts.append(part)
            content = "\n".join(parts)
        lines.append(f"{role.upper()}: {content}")
    return "\n\n".join(lines)


def _parse_relevance(raw: str) -> bool | None:
    try:
        parsed = parse_json_object(raw)
        value = parsed.get("isRelevant")
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in {"true", "1", "yes"}
    except Exception:
        pass
    # Fallback when the model truncates or wraps the JSON oddly.
    match = re.search(r'"?isRelevant"?\s*[:=]\s*(true|false)', raw, re.IGNORECASE)
    if match:
        return match.group(1).lower() == "true"
    return None


def router_agent(messages: list[dict[str, Any]]) -> dict[str, bool]:
    """Return ``{"isRelevant": bool}`` for the latest conversation turn."""
    settings = get_settings()
    transcript = _history_to_text(messages)
    prompt = (
        "Decide isRelevant for the latest user intent given this conversation.\n"
        "Respond with ONLY a JSON object of the form "
        '{"isRelevant": true} or {"isRelevant": false}.\n\n'
        f"CONVERSATION:\n{transcript}"
    )
    # Force JSON + disable thinking so gemini-2.5 doesn't eat the reply in thoughts.
    response = get_genai_client().models.generate_content(
        model=settings["chat_model"],
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=ROUTER_SYSTEM_PROMPT,
            temperature=0.0,
            response_mime_type="application/json",
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
    )
    raw = (response.text or "").strip()
    parsed = _parse_relevance(raw)
    if parsed is not None:
        return {"isRelevant": parsed}
    # Fail closed on parse errors
    return {"isRelevant": False}
