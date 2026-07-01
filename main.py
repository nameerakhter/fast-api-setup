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
