"""
NATA 2026 public chatbot API (FastAPI).

Flow:
  Streamlit  →  HTTP  →  FastAPI  →  Gemini + Qdrant RAG + MongoDB

Run (from project root, venv active):
  cd server
  uvicorn main:app --reload
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import asynccontextmanager
from typing import Any, Literal

from fastapi import Cookie, Depends, FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from pymongo import MongoClient

from agent.public_chatbot import stream_public_chat_reply
from chat_store import create_session, get_session, list_messages, save_message
from config import get_settings
from models import get_db_name_from_uri
from rate_limit import rate_limiter

SESSION_COOKIE = "public-chat-session-id"

client: MongoClient | None = None
db: Any = None


class ChatMessagePart(BaseModel):
    type: Literal["text"] = "text"
    text: str = ""


class ChatMessage(BaseModel):
    id: str | None = None
    role: Literal["user", "assistant", "system"]
    parts: list[ChatMessagePart] | None = None
    content: str | None = None


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(default_factory=list)


def _message_text(message: ChatMessage) -> str:
    if message.content:
        return message.content.strip()
    if message.parts:
        return "\n".join(part.text for part in message.parts if part.text).strip()
    return ""


@asynccontextmanager
async def lifespan(app: FastAPI):
    global client, db
    settings = get_settings()
    client = MongoClient(settings["mongodb_uri"])
    db = client[get_db_name_from_uri()]
    print("Connected to MongoDB:", db.name)
    yield
    client.close()
    print("Disconnected from MongoDB")


app = FastAPI(title="NATA Chatbot API", lifespan=lifespan)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings["cors_origin"], "http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def resolve_lang(lang: str = Query("en")) -> str:
    if lang not in {"en", "hi"}:
        raise HTTPException(status_code=400, detail="invalid lang")
    return lang


def resolve_session(
    response: Response,
    lang: str = Depends(resolve_lang),
    session_id: str | None = Cookie(default=None, alias=SESSION_COOKIE),
) -> str:
    if session_id:
        existing = get_session(db, session_id)
        if existing:
            return str(existing["_id"])

    created = create_session(db, language=lang)
    new_id = str(created["_id"])
    response.set_cookie(
        key=SESSION_COOKIE,
        value=new_id,
        httponly=True,
        samesite="lax",
        secure=False,
    )
    return new_id


@app.get("/")
def root():
    return {
        "message": "NATA 2026 chatbot API",
        "routes": {
            "GET /public-chat?lang=en|hi": "Load session messages",
            "POST /public-chat?lang=en|hi": "Stream assistant reply (text/plain)",
        },
    }


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/public-chat")
def get_public_chat(
    session_id: str = Depends(resolve_session),
    lang: str = Depends(resolve_lang),
):
    _ = lang
    return {"messages": list_messages(db, session_id), "sessionId": session_id}


@app.post("/public-chat")
def post_public_chat(
    body: ChatRequest,
    request: Request,
    session_id: str = Depends(resolve_session),
    lang: str = Depends(resolve_lang),
):
    client_ip = request.client.host if request.client else "unknown"
    if not rate_limiter.allow(client_ip):
        raise HTTPException(status_code=429, detail="rate limit exceeded")

    if not body.messages:
        raise HTTPException(status_code=400, detail="messages required")

    last = body.messages[-1]
    if last.role != "user":
        raise HTTPException(status_code=400, detail="last message must be from user")

    user_text = _message_text(last)
    if not user_text:
        raise HTTPException(status_code=400, detail="empty user message")

    save_message(db, session_id=session_id, role="user", text=user_text)

    language_preference = "hindi" if lang == "hi" else "english"
    payload = [
        {
            "role": m.role,
            "content": _message_text(m),
            "parts": [{"type": "text", "text": _message_text(m)}],
        }
        for m in body.messages
        if _message_text(m)
    ]

    collected: list[str] = []

    def token_stream() -> Iterator[str]:
        try:
            for chunk in stream_public_chat_reply(
                payload, language_preference=language_preference
            ):
                collected.append(chunk)
                yield chunk
        finally:
            full = "".join(collected).strip()
            if full:
                save_message(
                    db, session_id=session_id, role="assistant", text=full
                )

    return StreamingResponse(token_stream(), media_type="text/plain; charset=utf-8")
