# FastAPI Setup

A minimal Python project for learning virtual environments, dependency management, and MongoDB with **PyMongo** and **Pydantic**.

## Prerequisites

- Python 3.10+ ([python.org](https://www.python.org/downloads/))
- MongoDB running locally or a remote connection string ([MongoDB install guide](https://www.mongodb.com/docs/manual/installation/))
- A terminal (PowerShell, CMD, or Git Bash on Windows)

Check your versions:

```bash
python --version
mongosh --version
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

This installs PyMongo, Pydantic, FastAPI, Uvicorn, and their dependencies.

### 5. Freeze dependencies to `requirements.txt`

After installing or upgrading packages in your venv, save the exact versions so others can reproduce your environment:

```bash
pip freeze > requirements.txt
```

Run this whenever you add or update a package. Commit `requirements.txt` to git, but not the `venv/` folder.

## MongoDB setup

### Run MongoDB locally

**Windows (if installed as a service):**

```powershell
net start MongoDB
```

**Or start `mongod` manually** (path depends on your install):

```powershell
mongod --dbpath C:\data\db
```

**Connect with the shell** (optional, to inspect data):

```bash
mongosh
```

### Connection string

By default, `main.py` connects to:

```
mongodb://127.0.0.1:27017
```

It uses the database `course_store` and the collection `users`.

To point at a different host (Atlas, Docker, etc.), set `MONGODB_URI`:

**PowerShell:**

```powershell
$env:MONGODB_URI = "mongodb://127.0.0.1:27017"
python main.py
```

**CMD:**

```cmd
set MONGODB_URI=mongodb://127.0.0.1:27017
python main.py
```

## Run the MongoDB sample

With the venv activated and MongoDB running:

```bash
python main.py
```

Expected output:

```
Connected to MongoDB
Created user with id: ...
Student: Nameer (akhtarnameer@gmail.com)
Disconnected
```

Each run inserts a new user. If you hit a duplicate-email error, clear the collection in `mongosh`:

```javascript
use course_store
db.users.deleteMany({})
```

## How MongoDB works in this project

MongoDB stores **documents** (JSON-like objects) inside **collections**. A **database** holds many collections.

```
MongoDB server
    └── course_store          (database)
            └── users         (collection)
                    └── { email, name, role, enrolled_courses, ... }
```

### Request → database flow

```
main.py
    ↓  MongoClient(MONGODB_URI)
PyMongo driver
    ↓  TCP connection to MongoDB
MongoDB server
    ↓  read/write documents in a collection
Your Python code gets dicts back (or insert results)
```

1. **`MongoClient`** opens a connection to the MongoDB server.
2. **`client[DATABASE_NAME]`** selects the database (`course_store`).
3. **`db[COLLECTION_NAME]`** selects the collection (`users`).
4. **`insert_one` / `find`** read and write documents.

### User schema (`models/user.py`)

In Node.js you might use **Mongoose** to define a schema. In Python we use **Pydantic** for the same job — shape and validate data before it hits the database.

```python
class UserRole(str, Enum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"

class User(BaseModel):
    email: str
    name: str
    role: UserRole = UserRole.STUDENT
    enrolled_courses: List[str] = []
```

| Field              | Type     | Purpose                                      |
| ------------------ | -------- | -------------------------------------------- |
| `email`            | `str`    | Login / contact (unique in a real app)       |
| `name`             | `str`    | Display name                                 |
| `role`             | `enum`   | `student` or `instructor` for a course store |
| `enrolled_courses` | `list`   | Course IDs the user has bought or enrolled in |

### Core pieces in `main.py`

**Connect:**

```python
client = MongoClient(MONGODB_URI)
db = client["course_store"]
users = db["users"]
```

**Create a validated user and insert:**

```python
student = User(email="...", name="...", role=UserRole.STUDENT)
users.insert_one(student.model_dump(mode="json"))
```

`model_dump(mode="json")` turns the Pydantic model into a plain dict MongoDB can store (enums become strings).

**Query and read back:**

```python
for doc in users.find({"role": "student"}):
    user = User(**doc)
```

`find` returns raw dicts from MongoDB. Pydantic rebuilds a `User` object from each dict.

**Disconnect:**

```python
client.close()
```

### PyMongo vs Mongoose (quick comparison)

| Concept        | Mongoose (Node.js)     | This project (Python)        |
| -------------- | ---------------------- | ---------------------------- |
| Driver         | `mongoose`             | `pymongo`                    |
| Schema         | `mongoose.Schema`      | Pydantic `BaseModel`         |
| Connect        | `mongoose.connect()`   | `MongoClient(uri)`           |
| Create         | `User.create({...})`   | `users.insert_one({...})`    |
| Read           | `User.find({...})`     | `users.find({...})`          |

## Run the FastAPI server

With the venv activated and MongoDB running:

```bash
uvicorn server:app --reload
```

API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

Routes:

| Method | Path              | Description      |
| ------ | ----------------- | ---------------- |
| GET    | `/courses`        | List courses     |
| POST   | `/courses`        | Create a course  |
| DELETE | `/courses/{id}`   | Delete a course  |
| GET    | `/users`          | List users       |
| POST   | `/users`          | Create a user    |
| DELETE | `/users/{email}`  | Delete a user    |

CORS allows `http://localhost:8501` so the Streamlit app can call the API from the browser.

## Streamlit + FastAPI

Streamlit is a **client** — it calls FastAPI over HTTP with `httpx`, the same way a React app would use `fetch` against a Hono server. Streamlit does **not** import PyMongo.

### Request flow

```
Streamlit UI (app/app.py)
    │  button / form
    ▼
HTTP client (app/api.py)  —  GET / POST / DELETE
    │  http://localhost:8000
    ▼
FastAPI (server.py)
    │  route handlers
    ▼
PyMongo  →  MongoDB (course_store)
```

### Run both apps (two terminals)

**Terminal 1 — API:**

```bash
uvicorn server:app --reload
```

**Terminal 2 — Streamlit UI:**

```bash
streamlit run app/app.py
```

Open [http://localhost:8501](http://localhost:8501).

- **Load courses** — sends `GET /courses` only when you click the button (not on page load).
- **Add course** — sends `POST /courses`; the list is **not** auto-refetched.
- **Delete** — sends `DELETE /courses/{id}` and removes the row from local state only.

## Project structure

```
fast-api-setup/
├── main.py              # MongoDB connection and sample CRUD
├── server.py            # FastAPI REST API (users + courses)
├── app/
│   ├── api.py           # HTTP client wrappers (httpx)
│   └── app.py           # Streamlit UI
├── models/
│   ├── user.py          # User schema (Pydantic)
│   └── course.py        # Course schema (Pydantic)
├── requirements.txt     # Pinned dependencies
├── .gitignore           # Ignores venv/, __pycache__/, .env
├── README.md
└── venv/                # Local virtual env (not committed)
```

## Useful commands (cheat sheet)

```bash
python -m venv venv                 # Create venv
.\venv\Scripts\Activate.ps1         # Activate (PowerShell)
pip install -r requirements.txt     # Install deps
python main.py                      # Run MongoDB sample
uvicorn server:app --reload         # Start FastAPI server
streamlit run app/app.py            # Start Streamlit UI
deactivate                          # Exit venv
```

## Learn more

- [MongoDB Manual](https://www.mongodb.com/docs/manual/)
- [PyMongo documentation](https://pymongo.readthedocs.io/)
- [Pydantic documentation](https://docs.pydantic.dev/)
- [FastAPI documentation](https://fastapi.tiangolo.com/)
