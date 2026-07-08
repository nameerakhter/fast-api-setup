# =============================================================================
# HOW STREAMLIT TALKS TO THE SERVER
# =============================================================================
#
# Streamlit runs in your browser. It cannot connect to MongoDB directly.
# Instead it sends HTTP requests to your FastAPI server (server/main.py).
#
# Flow:
#   User clicks "Load courses" in Streamlit (client/app.py)
#         ↓
#   get_courses() below runs httpx GET http://localhost:8000/courses
#         ↓
#   FastAPI receives the request → PyMongo reads MongoDB → JSON response
#         ↓
#   Streamlit gets the JSON and updates the screen
#
# This file is the Python equivalent of src/api.js in the React refresher project.
# Streamlit never imports PyMongo — only HTTP.
# =============================================================================

from typing import Any

import httpx

# FastAPI default when you run: cd server && uvicorn main:app --reload
BASE_URL = "http://localhost:8000"
TIMEOUT = 10.0


def _request(method: str, path: str, **kwargs: Any) -> httpx.Response:
    # Shared helper — same idea as request() in React's api.js
    with httpx.Client(base_url=BASE_URL, timeout=TIMEOUT) as client:
        return client.request(method, path, **kwargs)


# --- courses ---

def get_courses() -> list[dict[str, Any]]:
    response = _request("GET", "/courses")
    response.raise_for_status()
    return response.json()


def create_course(
    title: str,
    description: str = "",
    instructor: str = "",
    price: float = 0.0,
    published: bool = True,
) -> dict[str, Any]:
    payload = {
        "title": title,
        "description": description,
        "instructor": instructor,
        "price": price,
        "published": published,
    }
    response = _request("POST", "/courses", json=payload)
    response.raise_for_status()
    return response.json()


def delete_course(course_id: str) -> dict[str, Any]:
    response = _request("DELETE", f"/courses/{course_id}")
    response.raise_for_status()
    return response.json()


# --- users (same pattern as courses) ---

def get_users() -> list[dict[str, Any]]:
    response = _request("GET", "/users")
    response.raise_for_status()
    return response.json()


def create_user(name: str, email: str, role: str = "student") -> dict[str, Any]:
    payload = {"name": name, "email": email, "role": role}
    response = _request("POST", "/users", json=payload)
    response.raise_for_status()
    return response.json()


def delete_user(user_id: str) -> dict[str, Any]:
    response = _request("DELETE", f"/users/{user_id}")
    response.raise_for_status()
    return response.json()
