# =============================================================================
# HOW STREAMLIT TALKS TO THE SERVER
# =============================================================================
#
# Streamlit runs in your browser. It cannot connect to MongoDB directly.
# Instead it sends HTTP requests to your FastAPI server (server.py).
#
# Flow:
#   User clicks "Load courses" in Streamlit (app/app.py)
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

# FastAPI default when you run: uvicorn server:app --reload
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
    instructor_email: str = "",
    price: float = 0.0,
) -> dict[str, Any]:
    payload = {
        "title": title,
        "description": description,
        "instructor_email": instructor_email,
        "price": price,
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


def create_user(
    email: str,
    name: str,
    role: str = "student",
    enrolled_courses: list[str] | None = None,
) -> dict[str, Any]:
    payload = {
        "email": email,
        "name": name,
        "role": role,
        "enrolled_courses": enrolled_courses or [],
    }
    response = _request("POST", "/users", json=payload)
    response.raise_for_status()
    return response.json()


def delete_user(email: str) -> dict[str, Any]:
    response = _request("DELETE", f"/users/{email}")
    response.raise_for_status()
    return response.json()
