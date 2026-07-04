"""
Step-by-step FastAPI tutorial — like the Hono learning file in the JS course.

Uncomment exactly ONE build_stepN() at the bottom, then run:
  uvicorn main.step_by_step.example:app --reload

Compare each step with main.py (the full app with all routes at once).
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


# =============================================================================
# STEP 1 — Basic FastAPI server (no database)
# =============================================================================
# Goal: prove the server runs and responds to HTTP.
# Try: curl http://127.0.0.1:8000/

def build_step1() -> FastAPI:
    app = FastAPI(title="Step 1 — hello")

    @app.get("/")
    def root():
        return {"message": "Hello from FastAPI (no database yet)"}

    return app


# =============================================================================
# STEP 2 — Connect MongoDB on startup
# =============================================================================
# Goal: same as step 1, but connect to MongoDB when the server starts.
# Watch the terminal for "Connected to MongoDB: course_store"

def build_step2() -> FastAPI:
    client: MongoClient | None = None

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        nonlocal client
        client = MongoClient(MONGODB_URI)
        database = client.get_default_database()
        print("Connected to MongoDB:", database.name)
        yield
        client.close()
        print("Disconnected from MongoDB")

    app = FastAPI(title="Step 2 — MongoDB on startup", lifespan=lifespan)

    @app.get("/")
    def root():
        return {"message": "MongoDB connected on startup — no routes yet"}

    return app


# =============================================================================
# STEP 3 — GET /users
# =============================================================================
# Goal: read users from MongoDB and return JSON.
# Try: curl http://127.0.0.1:8000/users
# (Run mongodb_steps.py step 2 first if the collection is empty)

def build_step3() -> FastAPI:
    client: MongoClient | None = None
    db: Any = None

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        nonlocal client, db
        client = MongoClient(MONGODB_URI)
        db = client.get_default_database()
        print("Connected to MongoDB:", db.name)
        yield
        client.close()
        print("Disconnected from MongoDB")

    app = FastAPI(title="Step 3 — GET /users", lifespan=lifespan)

    @app.get("/")
    def root():
        return {"message": "Try GET /users"}

    @app.get("/users")
    def list_users():
        users = [doc_to_json(doc) for doc in db[USERS_COLLECTION].find()]
        return users

    return app


# =============================================================================
# STEP 4 — POST /users
# =============================================================================
# Goal: create a user from JSON in the request body.
# Try:
#   curl -X POST http://127.0.0.1:8000/users \
#     -H "Content-Type: application/json" \
#     -d "{\"name\":\"Alice\",\"email\":\"alice@example.com\",\"role\":\"student\"}"

def build_step4() -> FastAPI:
    client: MongoClient | None = None
    db: Any = None

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        nonlocal client, db
        client = MongoClient(MONGODB_URI)
        db = client.get_default_database()
        print("Connected to MongoDB:", db.name)
        yield
        client.close()
        print("Disconnected from MongoDB")

    app = FastAPI(title="Step 4 — GET + POST /users", lifespan=lifespan)

    @app.get("/users")
    def list_users():
        users = [doc_to_json(doc) for doc in db[USERS_COLLECTION].find()]
        return users

    @app.post("/users", status_code=201)
    def create_user(body: UserCreate):
        result = db[USERS_COLLECTION].insert_one(body.model_dump())
        created = db[USERS_COLLECTION].find_one({"_id": result.inserted_id})
        return doc_to_json(created)

    return app


# =============================================================================
# STEP 5 — PATCH + DELETE /users/{id}
# =============================================================================
# Goal: update and remove one user by id.
# Try (replace USER_ID):
#   curl -X PATCH http://127.0.0.1:8000/users/USER_ID \
#     -H "Content-Type: application/json" -d "{\"name\":\"Alice Johnson\"}"
#   curl -X DELETE http://127.0.0.1:8000/users/USER_ID

def build_step5() -> FastAPI:
    client: MongoClient | None = None
    db: Any = None

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        nonlocal client, db
        client = MongoClient(MONGODB_URI)
        db = client.get_default_database()
        print("Connected to MongoDB:", db.name)
        yield
        client.close()
        print("Disconnected from MongoDB")

    app = FastAPI(title="Step 5 — user CRUD", lifespan=lifespan)

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

    return app


# =============================================================================
# STEP 6 — Full /courses CRUD (+ all user routes)
# =============================================================================
# Goal: same as main.py — both collections, all routes.
# Compare this with main.py side by side.

def build_step6() -> FastAPI:
    client: MongoClient | None = None
    db: Any = None

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        nonlocal client, db
        client = MongoClient(MONGODB_URI)
        db = client.get_default_database()
        print("Connected to MongoDB:", db.name)
        yield
        client.close()
        print("Disconnected from MongoDB")

    app = FastAPI(title="Step 6 — full API", lifespan=lifespan)

    @app.get("/")
    def root():
        return {"message": "Full course store API"}

    @app.get("/users")
    def list_users():
        return [doc_to_json(doc) for doc in db[USERS_COLLECTION].find()]

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

    @app.get("/courses")
    def list_courses():
        return [doc_to_json(doc) for doc in db[COURSES_COLLECTION].find()]

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

    return app


# =============================================================================
# Run ONE step at a time — uncomment the step you are teaching, comment the rest
# =============================================================================

app = build_step1()
# app = build_step2()
# app = build_step3()
# app = build_step4()
# app = build_step5()
# app = build_step6()
