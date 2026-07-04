"""Collection names and helpers for the course store."""

from bson import ObjectId
from bson.errors import InvalidId

USERS_COLLECTION = "users"
COURSES_COLLECTION = "courses"

# Document shapes (plain dicts in MongoDB):
#   User:   { name, email, role }
#   Course: { title, description, price, instructor, published }


def doc_to_json(doc: dict | None) -> dict | None:
    """Turn a MongoDB document into JSON-friendly dict (ObjectId → string id)."""
    if doc is None:
        return None
    out = dict(doc)
    if "_id" in out:
        out["id"] = str(out.pop("_id"))
    return out


def parse_object_id(id_str: str) -> ObjectId | None:
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError):
        return None
