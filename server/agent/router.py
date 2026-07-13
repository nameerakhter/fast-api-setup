"""Relevance router gate before the public NATA chatbot answers."""

from __future__ import annotations

from typing import Any

from agent.prompts import ROUTER_SYSTEM_PROMPT
from gemini_client import generate_text, parse_json_object


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


def router_agent(messages: list[dict[str, Any]]) -> dict[str, bool]:
    """Return ``{"isRelevant": bool}`` for the latest conversation turn."""
    transcript = _history_to_text(messages)
    prompt = (
        "Decide isRelevant for the latest user intent given this conversation.\n"
        "Respond with ONLY a JSON object of the form "
        '{"isRelevant": true} or {"isRelevant": false}.\n\n'
        f"CONVERSATION:\n{transcript}"
    )
    raw = generate_text(
        system=ROUTER_SYSTEM_PROMPT,
        contents=prompt,
        temperature=0.0,
        max_output_tokens=64,
    )
    try:
        parsed = parse_json_object(raw)
        value = parsed.get("isRelevant")
        if isinstance(value, bool):
            return {"isRelevant": value}
        if isinstance(value, str):
            return {"isRelevant": value.strip().lower() in {"true", "1", "yes"}}
    except Exception:
        pass
    # Fail closed on parse errors
    return {"isRelevant": False}
