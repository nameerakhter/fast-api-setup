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
mongodb://127.0.0.1:27017/course_store
```

The database name is in the URI. Collections used in the demo: `users` and `courses`.

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

`main.py` is a **step-by-step tutorial** (like a Mongoose demo). Each step is a function you run one at a time.

With the venv activated and MongoDB running:

1. Open `main.py` and scroll to the bottom.
2. **Uncomment exactly one** step call (start with `step1_connect()`).
3. Run:

```bash
python main.py
```

4. Comment that step out, uncomment the next one, and run again.

| Step | Function                | What it does                   |
| ---- | ----------------------- | ------------------------------ |
| 1    | `step1_connect()`       | Connect and disconnect only    |
| 2    | `step2_insert_user()`   | Insert Alice into `users`      |
| 3    | `step3_read_users()`    | Read all users                 |
| 4    | `step4_update_user()`   | Update Alice's name            |
| 5    | `step5_delete_user()`   | Delete Alice                   |
| 6    | `step6_insert_course()` | Insert a course into `courses` |
| 7    | `step7_update_course()` | Update course price            |
| 8    | `step8_delete_course()` | Delete the course              |

Run steps **in order** for the user/course demos (insert before read/update/delete).

To clear collections manually in `mongosh`:

```javascript
use course_store
db.users.deleteMany({})
db.courses.deleteMany({})
```

## How MongoDB works in this project

MongoDB stores **documents** (JSON-like objects) inside **collections**. A **database** holds many collections.

```
MongoDB server
    └── course_store          (database)
            ├── users         (collection)
            │       └── { email, name, role, enrolled_courses, ... }
            └── courses       (collection)
                    └── { title, description, price, instructor, published }
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
2. **`client.get_default_database()`** selects the database from the URI (`course_store`).
3. **`db["users"]` / `db["courses"]`** select a collection.
4. **`insert_one` / `find` / `find_one_and_update` / `find_one_and_delete`** perform CRUD on documents.

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

| Field              | Type   | Purpose                                       |
| ------------------ | ------ | --------------------------------------------- |
| `email`            | `str`  | Login / contact (unique in a real app)        |
| `name`             | `str`  | Display name                                  |
| `role`             | `enum` | `student` or `instructor` for a course store  |
| `enrolled_courses` | `list` | Course IDs the user has bought or enrolled in |

### Core pieces in `main.py`

Each step follows the same pattern: connect → do one thing → disconnect.

**Connect (Step 1):**

```python
client = MongoClient(MONGODB_URI)
db = client.get_default_database()
users = db["users"]
```

**Insert (Step 2) — like `User.create()`:**

```python
user = User(name="Alice", email="alice@example.com", role=UserRole.STUDENT)
users.insert_one(user.model_dump(mode="json"))
```

`model_dump(mode="json")` turns the Pydantic model into a plain dict MongoDB can store (enums become strings).

**Read all (Step 3) — like `User.find()`:**

```python
for doc in users.find():
    print(doc)
```

**Update (Step 4) — like `findOneAndUpdate(..., { new: true })`:**

```python
from pymongo import ReturnDocument

updated = users.find_one_and_update(
    {"email": "alice@example.com"},
    {"$set": {"name": "Alice Johnson"}},
    return_document=ReturnDocument.AFTER,
)
```

**Delete (Step 5) — like `findOneAndDelete()`:**

```python
deleted = users.find_one_and_delete({"email": "alice@example.com"})
```

**Disconnect:**

```python
client.close()
```

### PyMongo vs Mongoose (quick comparison)

| Concept         | Mongoose (Node.js)                          | This project (Python)                                   |
| --------------- | ------------------------------------------- | ------------------------------------------------------- |
| Driver          | `mongoose`                                  | `pymongo`                                               |
| Schema          | `mongoose.Schema`                           | Pydantic `BaseModel`                                    |
| Connect         | `mongoose.connect()`                        | `MongoClient(uri)`                                      |
| Create          | `User.create({...})`                        | `users.insert_one({...})`                               |
| Read many       | `User.find()`                               | `users.find()`                                          |
| Update + return | `User.findOneAndUpdate(..., { new: true })` | `users.find_one_and_update(..., return_document=AFTER)` |
| Delete + return | `User.findOneAndDelete(...)`                | `users.find_one_and_delete(...)`                        |

## Project structure

```
fast-api-setup/
├── main.py              # MongoDB connection and sample CRUD
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
deactivate                          # Exit venv
```

## Learn more

- [MongoDB Manual](https://www.mongodb.com/docs/manual/)
- [PyMongo documentation](https://pymongo.readthedocs.io/)
- [Pydantic documentation](https://docs.pydantic.dev/)
- [FastAPI documentation](https://fastapi.tiangolo.com/)
