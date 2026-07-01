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
