# =============================================================================
# WHY THIS FILE EXISTS (read this first)
# =============================================================================
#
# Before this, we used main.py — a script you run with "python main.py".
# That is fine for LEARNING. It is NOT how a real website works.
#
# Problem with scripts only:
#   - Script runs once on YOUR laptop, then stops.
#   - Only you can run it. A user on your website cannot.
#   - Your Streamlit app CANNOT talk to MongoDB directly (and should not).
#   - You would expose your DB password to everyone (very unsafe).
#
# What FastAPI does:
#   - FastAPI is a web server. It listens for HTTP requests (GET, POST, etc.).
#   - Your Streamlit app sends a request → FastAPI receives it → PyMongo saves to DB.
#   - The server stays ON all the time. Many users can use it at once.
#   - DB password stays on the server. Users never see it.
#
# Flow:
#   Streamlit button (app/app.py)
#         ↓
#   HTTP client (app/api.py)  →  GET/POST/DELETE http://localhost:8000/...
#         ↓
#   This file (server.py) handles the route
#         ↓
#   PyMongo reads/writes MongoDB
#
# Run with: uvicorn server:app --reload
# API docs: http://localhost:8000/docs
# =============================================================================

import os
from typing import List

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient

from models.course import Course, CourseCreate
from models.user import User, UserRole

# Same database as main.py — read connection string from env if set
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017")
DATABASE_NAME = "course_store"

# Connect once when the server starts — stays open while uvicorn runs
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
users_collection = db["users"]
courses_collection = db["courses"]

app = FastAPI(title="Course Store API")

# Streamlit runs on a different port (8501). Browsers block cross-origin requests
# unless the server says it's OK. This middleware adds those headers.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _course_from_doc(doc: dict) -> Course:
    # MongoDB stores _id as ObjectId; the API returns it as a string for JSON
    return Course(
        id=str(doc["_id"]),
        title=doc["title"],
        description=doc.get("description", ""),
        instructor_email=doc.get("instructor_email", ""),
        price=doc.get("price", 0.0),
    )


def _user_from_doc(doc: dict) -> User:
    # Raw MongoDB dict → validated Pydantic model (same idea as User(**doc) in main.py)
    return User(
        email=doc["email"],
        name=doc["name"],
        role=UserRole(doc["role"]),
        enrolled_courses=doc.get("enrolled_courses", []),
    )


# --- routes ---

@app.get("/")
def read_root() -> dict:
    return {"message": "Course Store API"}


# users
@app.get("/users", response_model=List[User])
def list_users() -> List[User]:
    return [_user_from_doc(doc) for doc in users_collection.find()]


@app.post("/users", response_model=User, status_code=201)
def create_user(user: User) -> User:
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=409, detail="User with this email already exists")
    users_collection.insert_one(user.model_dump(mode="json"))
    return user


@app.delete("/users/{email}")
def delete_user(email: str) -> dict:
    result = users_collection.delete_one({"email": email})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted", "email": email}


# courses
@app.get("/courses", response_model=List[Course])
def list_courses() -> List[Course]:
    return [_course_from_doc(doc) for doc in courses_collection.find()]


@app.post("/courses", response_model=Course, status_code=201)
def create_course(course: CourseCreate) -> Course:
    result = courses_collection.insert_one(course.model_dump(mode="json"))
    doc = courses_collection.find_one({"_id": result.inserted_id})
    if doc is None:
        raise HTTPException(status_code=500, detail="Failed to create course")
    return _course_from_doc(doc)


@app.delete("/courses/{course_id}")
def delete_course(course_id: str) -> dict:
    try:
        object_id = ObjectId(course_id)
    except InvalidId as exc:
        raise HTTPException(status_code=400, detail="Invalid course id") from exc

    result = courses_collection.delete_one({"_id": object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Course not found")
    return {"message": "Course deleted", "id": course_id}
