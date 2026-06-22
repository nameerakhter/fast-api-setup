# FastAPI Setup

A minimal FastAPI project for learning HTTP APIs, request/response handling, and Python dependency management with a virtual environment.

## Prerequisites

- Python 3.10+ installed ([python.org](https://www.python.org/downloads/))
- A terminal (PowerShell, CMD, or Git Bash on Windows)

Check your version:

```bash
python --version
```

## Project setup

### 1. Clone or open the project

```bash
cd fast-api-setup
```

### 2. Create a virtual environment

A virtual environment (`venv`) keeps this project's packages isolated from your system Python.

```bash
python -m venv venv
```

This creates a `venv/` folder. It is listed in `.gitignore` and should not be committed.

### 3. Activate the virtual environment

**PowerShell (Windows):**

```powershell
.\venv\Scripts\Activate.ps1
```

If you get an execution policy error:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**CMD (Windows):**

```cmd
venv\Scripts\activate.bat
```

When active, your prompt shows `(venv)`.

To leave the venv:

```bash
deactivate
```

### 4. Install dependencies

With the venv activated:

```bash
pip install -r requirements.txt
```

This installs FastAPI, Uvicorn, Pydantic, and their dependencies.

### 5. Freeze dependencies to `requirements.txt`

After installing or upgrading packages in your venv, save the exact versions so others can reproduce your environment:

```bash
pip freeze > requirements.txt
```

Run this whenever you add or update a package (for example after `pip install some-package`). Commit `requirements.txt` to git, but not the `venv/` folder.

**Typical workflow:**

```bash
# activate venv first
pip install fastapi uvicorn
pip freeze > requirements.txt
```

## Run the server

With the venv activated:

```bash
uvicorn main:app --reload
```


| Part       | Meaning                                         |
| ---------- | ----------------------------------------------- |
| `main`     | The Python file `main.py` (no `.py`)            |
| `app`      | The FastAPI instance inside that file           |
| `--reload` | Restart the server when code changes (dev only) |


Open:

- API root: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Interactive docs (Swagger UI): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Alternative docs (ReDoc): [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## How FastAPI works (basics)

FastAPI is a Python web framework for building APIs. It sits on top of **Starlette** (HTTP/routing) and **Pydantic** (data validation).

### Request → response flow

```
Client (browser / Postman / frontend)
    ↓  HTTP request (GET, POST, PUT, ...)
Uvicorn (ASGI server)
    ↓
FastAPI app
    ↓  matches URL + method to a route function
Your endpoint function (e.g. add_intern)
    ↓  returns a dict, list, or Pydantic model
FastAPI serializes to JSON
    ↓
Client receives HTTP response
```

1. **Uvicorn** runs the app and listens for HTTP traffic.
2. **FastAPI** maps the request path and method (`GET /names`, `POST /add-intern`) to a Python function.
3. The function runs and **returns Python data** (dict, list, model).
4. FastAPI converts that return value to **JSON** automatically.

### Core pieces in `main.py`

**The app instance** — entry point for all routes:

```python
app = FastAPI()
```

**Pydantic models** — define and validate request/response shapes:

```python
class Interns(BaseModel):
    id: int
    name: str
    college: str
```

When a client sends JSON in a POST body, FastAPI parses it into an `Interns` object and rejects invalid data (wrong types, missing fields) before your function runs.

**Route decorators** — tie URLs and HTTP methods to functions:

```python
@app.get("/")
@app.post("/add-intern")
@app.put("/name/{name_id}")
```


| Decorator     | HTTP method | Typical use |
| ------------- | ----------- | ----------- |
| `@app.get`    | GET         | Read data   |
| `@app.post`   | POST        | Create data |
| `@app.put`    | PUT         | Update data |
| `@app.delete` | DELETE      | Remove data |


**Path parameters** — values in the URL:

```python
def update_name(name_id: int, intern: Interns):
```

`/name/3` passes `name_id=3`.

**Request body** — JSON body typed as a Pydantic model:

```python
def add_intern(intern: Interns):
```

FastAPI reads the JSON body and validates it against `Interns`.

**Return values** — become the JSON response:

```python
return {"message": "Intern added successfully", "intern": intern}
```

For errors, prefer raising `HTTPException` with a status code instead of returning `{"error": "..."}` with status 200:

```python
from fastapi import HTTPException

raise HTTPException(status_code=404, detail="Intern not found")
```

## API endpoints in this project


| Method | Path              | Description               |
| ------ | ----------------- | ------------------------- |
| GET    | `/`               | Welcome message           |
| GET    | `/names`          | List interns              |
| POST   | `/add-intern`     | Add an intern (JSON body) |
| PUT    | `/name/{name_id}` | Update an intern by ID    |


Example POST body for `/add-intern`:

```json
{
  "id": 1,
  "name": "Jane Doe",
  "college": "Example University"
}
```

Use `/docs` to try endpoints without writing client code.

## Project structure

```
fast-api-setup/
├── main.py              # FastAPI app and routes
├── requirements.txt     # Pinned dependencies
├── .gitignore           # Ignores venv/, __pycache__/
├── README.md
└── venv/                # Local virtual env (not committed)
```

## Useful commands (cheat sheet)

```bash
python -m venv venv                 # Create venv
.\venv\Scripts\Activate.ps1         # Activate (PowerShell)
pip install -r requirements.txt     # Install deps
pip install fastapi uvicorn         # Install packages
pip freeze > requirements.txt       # Save deps
uvicorn main:app --reload           # Run dev server
deactivate                          # Exit venv
```

## Learn more

- [FastAPI documentation](https://fastapi.tiangolo.com/)
- [Pydantic documentation](https://docs.pydantic.dev/)
- [Uvicorn documentation](https://www.uvicorn.org/)

