# =============================================================================
# USER SCHEMA (Pydantic)
# =============================================================================
#
# Defines the shape of a user document in MongoDB.
# Used by main.py (script) and server.py (API routes).
#
# UserRole is an enum so only "student" or "instructor" are allowed.
# =============================================================================

from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class UserRole(str, Enum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"


class User(BaseModel):
    email: str
    name: str
    role: UserRole = UserRole.STUDENT
    enrolled_courses: List[str] = Field(default_factory=list)
