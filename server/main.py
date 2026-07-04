"""
WHY THIS FILE EXISTS (read this first)
======================================

mongodb_steps.py runs once on your laptop, talks to MongoDB, prints a result, and exits.
That is great for learning PyMongo — but it is NOT a website backend.

A course-selling site needs a program that:
  - stays running and waits for HTTP requests (GET, POST, PATCH, DELETE)
  - lets a React app (in the browser) fetch and change data safely
  - keeps the MongoDB password on the server — never in the browser

FastAPI is that long-running server:
  React  →  HTTP  →  FastAPI  →  PyMongo  →  MongoDB  →  JSON back

Compare with mongodb_steps.py when teaching. Use main.step_by_step.example.py
to build this file one route at a time.
"""

import os
from contextlib import asynccontextmanager
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient, ReturnDocument

from models import (
    COURSES_COLLECTION,
    USERS_COLLECTION,
    doc_to_json,
    parse_object_id,
)

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017/course_store")

client: MongoClient | None = None
db: Any = None


# --- Request bodies (field names + types only) ---


class UserCreate(BaseModel):
    name: str
    email: str
    role: str


class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    role: str | None = None


class CourseCreate(BaseModel):
    title: str
    description: str
    price: float
    instructor: str
    published: bool


class CourseUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    price: float | None = None
    instructor: str | None = None
    published: bool | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global client, db
    client = MongoClient(MONGODB_URI)
    db = client.get_default_database()
    print("Connected to MongoDB:", db.name)
    yield
    client.close()
    print("Disconnected from MongoDB")


app = FastAPI(title="Course Store API", lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "Course store API — see README for routes"}


# --- Users ---


@app.get("/users")
def list_users():
    users = [doc_to_json(doc) for doc in db[USERS_COLLECTION].find()]
    return users


@app.post("/users", status_code=201)
def create_user(body: UserCreate):
    result = db[USERS_COLLECTION].insert_one(body.model_dump())
    created = db[USERS_COLLECTION].find_one({"_id": result.inserted_id})
    return doc_to_json(created)


@app.patch("/users/{id}")
def update_user(id: str, body: UserUpdate):
    oid = parse_object_id(id)
    if oid is None:
        raise HTTPException(status_code=404, detail="User not found")

    updates = body.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    updated = db[USERS_COLLECTION].find_one_and_update(
        {"_id": oid},
        {"$set": updates},
        return_document=ReturnDocument.AFTER,
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="User not found")
    return doc_to_json(updated)


@app.delete("/users/{id}")
def delete_user(id: str):
    oid = parse_object_id(id)
    if oid is None:
        raise HTTPException(status_code=404, detail="User not found")

    deleted = db[USERS_COLLECTION].find_one_and_delete({"_id": oid})
    if deleted is None:
        raise HTTPException(status_code=404, detail="User not found")
    return doc_to_json(deleted)


# --- Courses ---


@app.get("/courses")
def list_courses():
    courses = [doc_to_json(doc) for doc in db[COURSES_COLLECTION].find()]
    return courses


@app.post("/courses", status_code=201)
def create_course(body: CourseCreate):
    result = db[COURSES_COLLECTION].insert_one(body.model_dump())
    created = db[COURSES_COLLECTION].find_one({"_id": result.inserted_id})
    return doc_to_json(created)


@app.patch("/courses/{id}")
def update_course(id: str, body: CourseUpdate):
    oid = parse_object_id(id)
    if oid is None:
        raise HTTPException(status_code=404, detail="Course not found")

    updates = body.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    updated = db[COURSES_COLLECTION].find_one_and_update(
        {"_id": oid},
        {"$set": updates},
        return_document=ReturnDocument.AFTER,
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return doc_to_json(updated)


@app.delete("/courses/{id}")
def delete_course(id: str):
    oid = parse_object_id(id)
    if oid is None:
        raise HTTPException(status_code=404, detail="Course not found")

    deleted = db[COURSES_COLLECTION].find_one_and_delete({"_id": oid})
    if deleted is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return doc_to_json(deleted)
