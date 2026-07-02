from pydantic import BaseModel


class Course(BaseModel):
    title: str
    description: str
    price: float
    instructor: str
    published: bool
