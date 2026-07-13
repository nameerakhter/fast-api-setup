"""HTTP helpers for the Streamlit NATA chatbot client → FastAPI."""

from __future__ import annotations

from collections.abc import Iterator

import httpx

BASE_URL = "http://localhost:8000"
SESSION_COOKIE = "public-chat-session-id"
TIMEOUT = httpx.Timeout(120.0, connect=10.0)


def _cookie_header(session_id: str | None) -> dict[str, str]:
    if not session_id:
        return {}
    return {"Cookie": f"{SESSION_COOKIE}={session_id}"}


def get_messages(
    lang: str = "en",
    session_id: str | None = None,
) -> tuple[list[dict], str | None]:
    with httpx.Client(timeout=TIMEOUT) as client:
        response = client.get(
            f"{BASE_URL}/public-chat",
            params={"lang": lang},
            headers=_cookie_header(session_id),
        )
        response.raise_for_status()
        data = response.json()
        new_session = response.cookies.get(SESSION_COOKIE) or data.get("sessionId")
        return data.get("messages", []), new_session or session_id


def stream_chat(
    messages: list[dict],
    *,
    lang: str = "en",
    session_id: str | None = None,
    session_out: dict | None = None,
) -> Iterator[str]:
    """Yield plain-text tokens from POST /public-chat."""
    payload = {"messages": messages}
    with httpx.Client(timeout=TIMEOUT) as client:
        with client.stream(
            "POST",
            f"{BASE_URL}/public-chat",
            params={"lang": lang},
            json=payload,
            headers=_cookie_header(session_id),
        ) as response:
            response.raise_for_status()
            new_session = response.cookies.get(SESSION_COOKIE)
            if session_out is not None and new_session:
                session_out["session_id"] = new_session
            for chunk in response.iter_text():
                if chunk:
                    yield chunk
