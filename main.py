import os

from pymongo import MongoClient, ReturnDocument

from models.course import Course
from models.user import User, UserRole

# =============================================================================
# Connection string
# =============================================================================
# This tells PyMongo WHERE your database lives.
#
# Local MongoDB:  mongodb://127.0.0.1:27017/course_store
#                 └─ host          └─ port  └─ database name (created on first save)
#
# Atlas (cloud):  put your URI in .env as MONGODB_URI=...

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017/course_store")

USERS_COLLECTION = "users"
COURSES_COLLECTION = "courses"


def _doc_without_id(doc: dict | None) -> dict | None:
    if doc is None:
        return None
    return {key: value for key, value in doc.items() if key != "_id"}


# =============================================================================
# STEP 1 — Connect to MongoDB
# =============================================================================

def step1_connect() -> None:
    print("Step 1: connecting to MongoDB...")
    print("Using URI:", MONGODB_URI)

    client = MongoClient(MONGODB_URI)
    db = client.get_default_database()
    print("Connected to database:", db.name)

    client.close()
    print("Disconnected from MongoDB")


# =============================================================================
# STEP 2 — User schema + insert one user
# =============================================================================
# Goal: define a model and save a document to the "users" collection.
# Comment out step 1 above, uncomment step 2 below. Run: python main.py

def step2_insert_user() -> None:
    print("Step 2: connecting to MongoDB...")
    client = MongoClient(MONGODB_URI)
    db = client.get_default_database()
    users = db[USERS_COLLECTION]
    print("Connected to database:", db.name)

    user = User(
        name="Alice",
        email="alice@example.com",
        role=UserRole.STUDENT,
    )
    result = users.insert_one(user.model_dump(mode="json"))
    inserted = users.find_one({"_id": result.inserted_id})

    print("Inserted user:", _doc_without_id(inserted))

    client.close()
    print("Disconnected from MongoDB")


# =============================================================================
# STEP 3 — Read users from the database
# =============================================================================
# Goal: fetch documents you saved earlier.
# Comment out previous step, uncomment step 3 below. Run: python main.py

def step3_read_users() -> None:
    print("Step 3: connecting to MongoDB...")
    client = MongoClient(MONGODB_URI)
    db = client.get_default_database()
    users = db[USERS_COLLECTION]
    print("Connected to database:", db.name)

    all_users = [_doc_without_id(doc) for doc in users.find()]
    print("All users:", all_users)

    client.close()
    print("Disconnected from MongoDB")


# =============================================================================
# STEP 4 — Update a user
# =============================================================================
# Goal: change a document that already exists.
# Comment out previous step, uncomment step 4 below. Run: python main.py

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

    print("Updated user:", _doc_without_id(updated))

    client.close()
    print("Disconnected from MongoDB")


# =============================================================================
# STEP 5 — Delete a user
# =============================================================================
# Goal: remove a document from the collection.
# Comment out previous step, uncomment step 5 below. Run: python main.py

def step5_delete_user() -> None:
    print("Step 5: connecting to MongoDB...")
    client = MongoClient(MONGODB_URI)
    db = client.get_default_database()
    users = db[USERS_COLLECTION]
    print("Connected to database:", db.name)

    deleted = users.find_one_and_delete({"email": "alice@example.com"})
    print("Deleted user:", _doc_without_id(deleted))

    client.close()
    print("Disconnected from MongoDB")


# =============================================================================
# STEP 6 — Course schema + insert one course
# =============================================================================
# Goal: second model for the course-selling site.
# Comment out previous step, uncomment step 6 below. Run: python main.py

def step6_insert_course() -> None:
    print("Step 6: connecting to MongoDB...")
    client = MongoClient(MONGODB_URI)
    db = client.get_default_database()
    courses = db[COURSES_COLLECTION]
    print("Connected to database:", db.name)

    course = Course(
        title="React Fundamentals",
        description="Learn React from scratch.",
        price=49.99,
        instructor="Bob",
        published=True,
    )
    result = courses.insert_one(course.model_dump(mode="json"))
    inserted = courses.find_one({"_id": result.inserted_id})

    print("Inserted course:", _doc_without_id(inserted))

    client.close()
    print("Disconnected from MongoDB")


# =============================================================================
# STEP 7 — Update a course
# =============================================================================
# Comment out previous step, uncomment step 7 below. Run: python main.py

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

    print("Updated course:", _doc_without_id(updated))

    client.close()
    print("Disconnected from MongoDB")


# =============================================================================
# STEP 8 — Delete a course
# =============================================================================
# Comment out previous step, uncomment step 8 below. Run: python main.py

def step8_delete_course() -> None:
    print("Step 8: connecting to MongoDB...")
    client = MongoClient(MONGODB_URI)
    db = client.get_default_database()
    courses = db[COURSES_COLLECTION]
    print("Connected to database:", db.name)

    deleted = courses.find_one_and_delete({"title": "React Fundamentals"})
    print("Deleted course:", _doc_without_id(deleted))

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
