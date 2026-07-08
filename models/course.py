# =============================================================================
# COURSE SCHEMA (Pydantic)
# =============================================================================
#
# In Node.js you might use Mongoose schemas. In Python we use Pydantic models.
# FastAPI uses these to validate incoming JSON and shape outgoing responses.
#
# CourseCreate = fields the client sends when creating a course (no id yet).
# Course       = full course returned by the API (includes id from MongoDB).
# =============================================================================

from pydantic import BaseModel, Field


class CourseCreate(BaseModel):
    title: str
    description: str = ""
    instructor_email: str = ""
    price: float = Field(default=0.0, ge=0)


class Course(CourseCreate):
    id: str
