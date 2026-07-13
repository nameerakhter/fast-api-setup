"""MongoDB helpers and collection names for chat sessions / messages."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from bson.errors import InvalidId

from config import get_settings

SESSIONS_COLLECTION = "chat_sessions"
MESSAGES_COLLECTION = "chat_messages"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def doc_to_json(doc: dict[str, Any] | None) -> dict[str, Any] | None:
    if doc is None:
        return None
    out = dict(doc)
    if "_id" in out:
        out["id"] = str(out.pop("_id"))
    for key, value in list(out.items()):
        if isinstance(value, ObjectId):
            out[key] = str(value)
        elif isinstance(value, datetime):
            out[key] = value.isoformat()
    return out


def parse_object_id(value: str) -> ObjectId | None:
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        return None


def get_db_name_from_uri() -> str:
    settings = get_settings()
    uri = settings["mongodb_uri"]
    # mongodb://host:port/dbname
    if "/" in uri.rsplit("@", 1)[-1]:
        path = uri.rsplit("/", 1)[-1]
        db_name = path.split("?")[0]
        if db_name:
            return db_name
    return "nata_chatbot"
