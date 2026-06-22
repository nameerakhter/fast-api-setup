from fastapi import FastAPI
from pydantic import BaseModel
from typing import List


app = FastAPI()


class Interns(BaseModel):
    id: int
    name: str
    college: str



names: List[Interns] =[]



@app.get("/")
def read_root():
    return {"message: Welcome interns to ITDA"}

@app.get("/names")
def return_names():
    return Interns

@app.post("/add-intern")
def add_intern(intern: Interns):
    names.append(intern)
    return {"message": "Intern added successfully", "intern": intern}




@app.put("/name/{name_id}")
def update_name(name_id: int, intern: Interns):
    for index, item in enumerate(names):
        if item.id == name_id:
            names[index] = intern
            return {"message": "Intern updated successfully"}
    return {"error": "Intern not found"}
