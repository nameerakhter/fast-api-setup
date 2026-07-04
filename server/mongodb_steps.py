"""
Step-by-step MongoDB tutorial — like mongoose.js in the JS course.

Run ONE step at a time: uncomment a single line at the bottom, then:
  python mongodb_steps.py
"""

import os

from dotenv import load_dotenv
from pymongo import MongoClient, ReturnDocument

from models import COURSES_COLLECTION, USERS_COLLECTION, doc_to_json

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017/course_store")


def step1_connect() -> None:
    print("Step 1: connecting to MongoDB...")
    print("Using URI:", MONGODB_URI)

    client = MongoClient(MONGODB_URI)
    db = client.get_default_database()
    print("Connected to database:", db.name)

    client.close()
    print("Disconnected from MongoDB")


def step2_insert_user() -> None:
    print("Step 2: connecting to MongoDB...")
    client = MongoClient(MONGODB_URI)
    db = client.get_default_database()
    users = db[USERS_COLLECTION]
    print("Connected to database:", db.name)

    user = {"name": "Alice", "email": "alice@example.com", "role": "student"}
    result = users.insert_one(user)
    inserted = users.find_one({"_id": result.inserted_id})
    print("Inserted user:", doc_to_json(inserted))

    client.close()
    print("Disconnected from MongoDB")


def step3_read_users() -> None:
    print("Step 3: connecting to MongoDB...")
    client = MongoClient(MONGODB_URI)
    db = client.get_default_database()
    users = db[USERS_COLLECTION]
    print("Connected to database:", db.name)

    all_users = [doc_to_json(doc) for doc in users.find()]
    print("All users:", all_users)

    client.close()
    print("Disconnected from MongoDB")


def step4_update_user() -> None:
    print("Step 4: connecting to MongoDB...")
    client = MongoClient(MONGODB_URI)
    db = client.get_default_database()
    users = db[USERS_COLLECTION]
    print("Connected to database:", db.name)

    updated = users.find_one_and_update(
        {"email": "alice@example.com"},
        {"$set": {"name": "Alice Johnson"}},
        return_document=ReturnDocument.AFTER,
    )
    print("Updated user:", doc_to_json(updated))

    client.close()
    print("Disconnected from MongoDB")


def step5_delete_user() -> None:
    print("Step 5: connecting to MongoDB...")
    client = MongoClient(MONGODB_URI)
    db = client.get_default_database()
    users = db[USERS_COLLECTION]
    print("Connected to database:", db.name)

    deleted = users.find_one_and_delete({"email": "alice@example.com"})
    print("Deleted user:", doc_to_json(deleted))

    client.close()
    print("Disconnected from MongoDB")


def step6_insert_course() -> None:
    print("Step 6: connecting to MongoDB...")
    client = MongoClient(MONGODB_URI)
    db = client.get_default_database()
    courses = db[COURSES_COLLECTION]
    print("Connected to database:", db.name)

    course = {
        "title": "React Fundamentals",
        "description": "Learn React from scratch.",
        "price": 49.99,
        "instructor": "Bob",
        "published": True,
    }
    result = courses.insert_one(course)
    inserted = courses.find_one({"_id": result.inserted_id})
    print("Inserted course:", doc_to_json(inserted))

    client.close()
    print("Disconnected from MongoDB")


def step7_update_course() -> None:
    print("Step 7: connecting to MongoDB...")
    client = MongoClient(MONGODB_URI)
    db = client.get_default_database()
    courses = db[COURSES_COLLECTION]
    print("Connected to database:", db.name)

    updated = courses.find_one_and_update(
        {"title": "React Fundamentals"},
        {"$set": {"price": 39.99}},
        return_document=ReturnDocument.AFTER,
    )
    print("Updated course:", doc_to_json(updated))

    client.close()
    print("Disconnected from MongoDB")


def step8_delete_course() -> None:
    print("Step 8: connecting to MongoDB...")
    client = MongoClient(MONGODB_URI)
    db = client.get_default_database()
    courses = db[COURSES_COLLECTION]
    print("Connected to database:", db.name)

    deleted = courses.find_one_and_delete({"title": "React Fundamentals"})
    print("Deleted course:", doc_to_json(deleted))

    client.close()
    print("Disconnected from MongoDB")


# =============================================================================
# Run ONE step at a time — comment/uncomment the line you want
# =============================================================================

if __name__ == "__main__":
    # step1_connect()
    # step2_insert_user()
    # step3_read_users()
    # step4_update_user()
    # step5_delete_user()
    # step6_insert_course()
    # step7_update_course()
    # step8_delete_course()
    pass
