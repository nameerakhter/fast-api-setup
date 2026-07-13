"""Chat session + message persistence in MongoDB."""

from __future__ import annotations

from typing import Any

from bson import ObjectId

from models import MESSAGES_COLLECTION, SESSIONS_COLLECTION, utc_now


def create_session(db, *, language: str) -> dict[str, Any]:
    lang_pref = "ENGLISH" if language == "en" else "HINDI"
    doc = {
        "type": "PUBLIC",
        "languagePreference": lang_pref,
        "userId": None,
        "userMetadata": None,
        "createdAt": utc_now(),
        "updatedAt": utc_now(),
    }
    result = db[SESSIONS_COLLECTION].insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


def get_session(db, session_id: str) -> dict[str, Any] | None:
    try:
        oid = ObjectId(session_id)
    except Exception:
        return None
    return db[SESSIONS_COLLECTION].find_one({"_id": oid, "type": "PUBLIC"})


def list_messages(db, session_id: str) -> list[dict[str, Any]]:
    try:
        oid = ObjectId(session_id)
    except Exception:
        return []
    cursor = db[MESSAGES_COLLECTION].find({"sessionId": oid}).sort("createdAt", 1)
    messages: list[dict[str, Any]] = []
    for doc in cursor:
        role = "user" if doc.get("role") == "USER" else "assistant"
        messages.append(
            {
                "id": str(doc["_id"]),
                "role": role,
                "parts": doc.get("contentParts")
                or [{"type": "text", "text": doc.get("contentText", "")}],
                "content": doc.get("contentText", ""),
            }
        )
    return messages


def save_message(
    db,
    *,
    session_id: str,
    role: str,
    text: str,
) -> dict[str, Any]:
    oid = ObjectId(session_id)
    parts = [{"type": "text", "text": text}]
    doc = {
        "sessionId": oid,
        "role": "USER" if role == "user" else "ASSISTANT",
        "contentParts": parts,
        "contentText": text,
        "userId": None,
        "createdAt": utc_now(),
        "updatedAt": utc_now(),
    }
    result = db[MESSAGES_COLLECTION].insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc
