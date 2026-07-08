# =============================================================================
# WHY THIS FILE EXISTS (read this first)
# =============================================================================
#
# This is a LEARNING script — not a web server.
# Run it with: python main.py
#
# It connects to MongoDB directly with PyMongo, inserts a user, prints results,
# then exits. Good for understanding how PyMongo works.
#
# For a real app (Streamlit + API), use:
#   - server.py        → FastAPI listens for HTTP requests
#   - app/app.py       → Streamlit UI calls the API over HTTP
#
# Scripts vs servers:
#   main.py   → runs once, talks to DB directly, then stops
#   server.py → stays running, waits for HTTP requests from Streamlit
# =============================================================================

import os

from pymongo import MongoClient

from models.user import User, UserRole

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017")
DATABASE_NAME = "course_store"
COLLECTION_NAME = "users"


def main() -> None:
    client = MongoClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    users = db[COLLECTION_NAME]

    print("Connected to MongoDB")

    student = User(
        email="akhtarnameer@gmail.com",
        name="Nameer",
        role=UserRole.STUDENT,
        enrolled_courses=[],
    )
    result = users.insert_one(student.model_dump(mode="json"))
    print(f"Created user with id: {result.inserted_id}")

    for doc in users.find({"role": UserRole.STUDENT.value}):
        user = User(**doc)
        print(f"Student: {user.name} ({user.email})")

    client.close()
    print("Disconnected")


if __name__ == "__main__":
    main()
