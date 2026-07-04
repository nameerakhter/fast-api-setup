# Course Store — Backend (Python)

Teaching project for interns: **PyMongo** (raw MongoDB) → **FastAPI** (HTTP API).

Same flow as the JavaScript version (Mongoose scripts → Hono step-by-step → full Hono app):

1. `mongodb_steps.py` — run once, learn CRUD in the terminal  
2. `main.step_by_step.example.py` — build the API one route at a time  
3. `main.py` — full app, all routes live at once  

## What you are building

A **course-selling website** with two MongoDB collections:

| Collection | Fields |
| ---------- | ------ |
| `users` | `name`, `email`, `role` |
| `courses` | `title`, `description`, `price`, `instructor`, `published` |

## Prerequisites

- Python 3.10+
- MongoDB running locally ([install guide](https://www.mongodb.com/docs/manual/installation/))
- Terminal (PowerShell on Windows is fine)

```bash
python --version
mongosh --version
```

## Setup

```powershell
cd server
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Start MongoDB (Windows service example):

```powershell
net start MongoDB
```

Default connection (in `.env`):

```
MONGODB_URI=mongodb://127.0.0.1:27017/course_store
```

## Teaching order

| Order | File | Command | What interns learn |
| ----- | ---- | ------- | ------------------ |
| 1 | `mongodb_steps.py` | `python mongodb_steps.py` | PyMongo CRUD, one step at a time |
| 2 | `main.step_by_step.example.py` | `uvicorn main.step_by_step.example:app --reload` | HTTP + FastAPI, one step at a time |
| 3 | `main.py` | `uvicorn main:app --reload` | Production-style app, all routes together |

In both step files, **uncomment only one step** at the bottom before running.

---

## Part 1 — MongoDB scripts (`mongodb_steps.py`)

Like `mongoose.js` in the JS course. Each step: **connect → do one thing → print → disconnect**.

| Step | Function | What it does |
| ---- | -------- | ------------ |
| 1 | `step1_connect()` | Connect and disconnect only |
| 2 | `step2_insert_user()` | Insert Alice |
| 3 | `step3_read_users()` | Read all users |
| 4 | `step4_update_user()` | Update Alice's name |
| 5 | `step5_delete_user()` | Delete Alice |
| 6 | `step6_insert_course()` | Insert a course |
| 7 | `step7_update_course()` | Update course price |
| 8 | `step8_delete_course()` | Delete the course |

```bash
python mongodb_steps.py
```

Open the file, uncomment **one** `stepN_...()` at the bottom, run again.

---

## Why scripts alone are not enough

`mongodb_steps.py` is perfect for **learning MongoDB** — but it is **not** a website backend.

| Problem | Explanation |
| ------- | ----------- |
| Runs once and stops | Your script finishes after one action. A website needs a program **always listening**. |
| Users cannot run your script | Visitors on the internet cannot execute Python on your laptop. |
| React cannot talk to MongoDB | Browsers only speak **HTTP**. MongoDB speaks its **own wire protocol**. |
| Password must stay on the server | If React connected directly to MongoDB, you'd expose credentials in the browser. |

![Script vs real app](images/script-vs-real-app.png)

### Script vs real app

| | `mongodb_steps.py` (script) | `main.py` (FastAPI app) |
| --- | --- | --- |
| How it runs | `python mongodb_steps.py` once | `uvicorn main:app --reload` keeps running |
| Who can use it | You, in a terminal | Anyone with HTTP (browser, React, curl) |
| Stays open | No — exits immediately | Yes — waits for requests |
| Good for | Learning PyMongo | Real course store backend |

---

## Why FastAPI?

FastAPI is the **long-running server** between React and MongoDB:

```
React (browser)  →  HTTP  →  FastAPI  →  PyMongo  →  MongoDB  →  JSON back
```

![Real app request flow](images/real-app-request-flow.png)

- **Stays running** and listens for GET, POST, PATCH, DELETE  
- **Many users** can hit it at the same time  
- **Password stays on the server** — React never sees `MONGODB_URI`  
- Returns **JSON** that React can render  

![Why React cannot connect straight to MongoDB](images/react-no-direct-mongodb.png)

**HTTP basics:** [Intro to HTTP slides](https://petal-estimate-4e9.notion.site/Intro-to-HTTP-26c5803f153b4401aa76e9fac08ac427)

*(Auth, JWT, and CORS are a natural next step after this module — not included here.)*

---

## Part 2 — Step-by-step API (`main.step_by_step.example.py`)

Like the Hono learning file. Uncomment **one** `app = build_stepN()` at the bottom:

| Step | What it adds |
| ---- | ------------ |
| 1 | `GET /` — FastAPI runs, no database |
| 2 | Connect MongoDB on startup |
| 3 | `GET /users` |
| 4 | `POST /users` |
| 5 | `PATCH` + `DELETE /users/{id}` |
| 6 | Full `/courses` CRUD (+ all user routes) |

```bash
uvicorn main.step_by_step.example:app --reload
```

Open http://127.0.0.1:8000/docs for interactive API docs.

Compare each step with `main.py` when teaching.

---

## Part 3 — Full app (`main.py`)

All routes registered at once — how a real backend looks.

```bash
uvicorn main:app --reload
```

| Method | Route | Action |
| ------ | ----- | ------ |
| GET | `/` | Hello message |
| GET | `/users` | List all users |
| POST | `/users` | Create user |
| PATCH | `/users/{id}` | Update user |
| DELETE | `/users/{id}` | Delete user |
| GET | `/courses` | List all courses |
| POST | `/courses` | Create course |
| PATCH | `/courses/{id}` | Update course |
| DELETE | `/courses/{id}` | Delete course |

Documents use `"id"` in JSON (MongoDB `_id` converted to string). Invalid or missing ids return **404**.

---

## curl examples

Start the full app first: `uvicorn main:app --reload`

**Root**

```bash
curl http://127.0.0.1:8000/
```

**Users — list**

```bash
curl http://127.0.0.1:8000/users
```

**Users — create**

```bash
curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Alice\",\"email\":\"alice@example.com\",\"role\":\"student\"}"
```

Save the `"id"` from the response for update/delete.

**Users — update** (replace `USER_ID`)

```bash
curl -X PATCH http://127.0.0.1:8000/users/USER_ID \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Alice Johnson\"}"
```

**Users — delete**

```bash
curl -X DELETE http://127.0.0.1:8000/users/USER_ID
```

**Courses — list**

```bash
curl http://127.0.0.1:8000/courses
```

**Courses — create**

```bash
curl -X POST http://127.0.0.1:8000/courses \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"React Fundamentals\",\"description\":\"Learn React from scratch.\",\"price\":49.99,\"instructor\":\"Bob\",\"published\":true}"
```

**Courses — update** (replace `COURSE_ID`)

```bash
curl -X PATCH http://127.0.0.1:8000/courses/COURSE_ID \
  -H "Content-Type: application/json" \
  -d "{\"price\":39.99}"
```

**Courses — delete**

```bash
curl -X DELETE http://127.0.0.1:8000/courses/COURSE_ID
```

**PowerShell note:** use backtick `` ` `` for line breaks, or put the JSON on one line.

---

## Project files

```
server/
├── models.py                      # Collection names + JSON helpers
├── mongodb_steps.py               # Step 1–8 PyMongo tutorial
├── main.py                        # Full FastAPI app
├── main.step_by_step.example.py   # Step 1–6 FastAPI tutorial
├── requirements.txt
├── .env.example
├── pyproject.toml
├── images/                        # Diagram placeholders (see images/README.md)
└── README.md
```

## Reset data in mongosh

```javascript
use course_store
db.users.deleteMany({})
db.courses.deleteMany({})
```

## Learn more

- [MongoDB Manual](https://www.mongodb.com/docs/manual/)
- [PyMongo docs](https://pymongo.readthedocs.io/)
- [FastAPI docs](https://fastapi.tiangolo.com/)
- [Intro to HTTP](https://petal-estimate-4e9.notion.site/Intro-to-HTTP-26c5803f153b4401aa76e9fac08ac427)
