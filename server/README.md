# Course Store — Backend

Learn MongoDB with a script, then run a **FastAPI CRUD server** for a course-selling site.

Uses the **root** virtual environment — see [../README.md](../README.md) for setup.

## Collections

| Collection | Fields |
| ---------- | ------ |
| `users` | `name`, `email`, `role` |
| `courses` | `title`, `description`, `price`, `instructor`, `published` |

---

## Setup

Do this once from the **project root** (not inside `server/`):

```powershell
cd ..   # if you are in server/
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
net start MongoDB
```

The `.env` file lives at the project root. `models.py` loads it automatically.

Default value:

```
MONGODB_URI=mongodb://127.0.0.1:27017/course_store
```

For every new terminal:

```powershell
.\venv\Scripts\Activate.ps1
cd server
```

---

## Part 1 — Learn MongoDB (`mongodb_steps.py`)

A terminal script that connects, does one CRUD action, and exits.

**How to run** (venv active, inside `server/`):

1. Open `mongodb_steps.py`
2. Scroll to the bottom and **uncomment one** `stepN_...()` line
3. Run:

```powershell
python mongodb_steps.py
```

4. Comment it out, uncomment the next step, run again

| Step | Function | What it does |
| ---- | -------- | ------------ |
| 1 | `step1_connect()` | Connect and disconnect |
| 2 | `step2_insert_user()` | Insert a user |
| 3 | `step3_read_users()` | Read all users |
| 4 | `step4_update_user()` | Update a user |
| 5 | `step5_delete_user()` | Delete a user |
| 6 | `step6_insert_course()` | Insert a course |
| 7 | `step7_update_course()` | Update a course |
| 8 | `step8_delete_course()` | Delete a course |

Run steps **in order** (insert before read/update/delete).

---

## Part 2 — Run the FastAPI CRUD server (`main.py`)

### Why not just the script?

| Script (`mongodb_steps.py`) | Server (`main.py`) |
| --- | --- |
| Runs once and exits | Stays running, waits for requests |
| Only you in a terminal | Browser, Streamlit, curl can call it |
| Good for learning MongoDB | Good for a real backend |

```
Streamlit / browser  →  HTTP  →  FastAPI  →  PyMongo  →  MongoDB
```

![Script vs real app](images/script-vs-real-app.png)
![Request flow](images/real-app-request-flow.png)
![Why the client can't use MongoDB directly](images/react-no-direct-mongodb.png)

HTTP intro: [Intro to HTTP slides](https://petal-estimate-4e9.notion.site/Intro-to-HTTP-26c5803f153b4401aa76e9fac08ac427)

---

### How to run the server

Root venv active, inside `server/`:

**Step 1 — Start the API**

```powershell
uvicorn main:app --reload
```

You should see:

```
Connected to MongoDB: course_store
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Leave this terminal open until you press `Ctrl+C`.

**Step 2 — Open the interactive docs**

```
http://127.0.0.1:8000/docs
```

**Step 3 — Test with curl**

Open a **second terminal**. Activate root venv, `cd server`:

| # | Action | Command |
| - | ------ | ------- |
| 1 | Health check | `curl http://127.0.0.1:8000/` |
| 2 | List users | `curl http://127.0.0.1:8000/users` |
| 3 | Create user | see below |
| 4 | Update user | see below (need `id` from step 3) |
| 5 | Delete user | `curl -X DELETE http://127.0.0.1:8000/users/USER_ID` |
| 6 | List courses | `curl http://127.0.0.1:8000/courses` |
| 7 | Create course | see below |
| 8 | Update course | see below (need `id` from step 7) |
| 9 | Delete course | `curl -X DELETE http://127.0.0.1:8000/courses/COURSE_ID` |

**Create user**

```powershell
curl -X POST http://127.0.0.1:8000/users -H "Content-Type: application/json" -d "{\"name\":\"Alice\",\"email\":\"alice@example.com\",\"role\":\"student\"}"
```

**Update user** (replace `USER_ID`)

```powershell
curl -X PATCH http://127.0.0.1:8000/users/USER_ID -H "Content-Type: application/json" -d "{\"name\":\"Alice Johnson\"}"
```

**Create course**

```powershell
curl -X POST http://127.0.0.1:8000/courses -H "Content-Type: application/json" -d "{\"title\":\"React Fundamentals\",\"description\":\"Learn React from scratch.\",\"price\":49.99,\"instructor\":\"Bob\",\"published\":true}"
```

**Update course** (replace `COURSE_ID`)

```powershell
curl -X PATCH http://127.0.0.1:8000/courses/COURSE_ID -H "Content-Type: application/json" -d "{\"price\":39.99}"
```

**Step 4 — Stop the server**

Press `Ctrl+C` in the uvicorn terminal.

---

### API routes

| Method | Route | Action |
| ------ | ----- | ------ |
| GET | `/` | Hello message |
| GET | `/users` | List users |
| POST | `/users` | Create user |
| PATCH | `/users/{id}` | Update user |
| DELETE | `/users/{id}` | Delete user |
| GET | `/courses` | List courses |
| POST | `/courses` | Create course |
| PATCH | `/courses/{id}` | Update course |
| DELETE | `/courses/{id}` | Delete course |

---

## Project files

```
fast-api-setup/
├── venv/                   # single virtual env (not committed)
├── requirements.txt        # all Python deps (server + client)
├── .env.example
├── server/
│   ├── models.py
│   ├── mongodb_steps.py
│   ├── main.py
│   └── README.md
└── client/
    ├── app.py
    └── README.md
```

## Reset database

In `mongosh`:

```javascript
use course_store
db.users.deleteMany({})
db.courses.deleteMany({})
```

## Troubleshooting

| Problem | Fix |
| ------- | --- |
| `ServerSelectionTimeoutError` | Start MongoDB (`net start MongoDB`) |
| `ModuleNotFoundError` | From project root: activate venv, `pip install -r requirements.txt` |
| Port 8000 in use | Stop other uvicorn, or use `--port 8001` |
| Step 3+ in mongodb_steps shows empty/`None` | Run the insert step first |

## Learn more

- [PyMongo docs](https://pymongo.readthedocs.io/)
- [FastAPI docs](https://fastapi.tiangolo.com/)
- [MongoDB Manual](https://www.mongodb.com/docs/manual/)
