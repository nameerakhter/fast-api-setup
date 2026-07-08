# FastAPI Setup

Course store teaching repo: **PyMongo** + **FastAPI** backend, **Streamlit** client.

| Folder | What it is |
| ------ | ---------- |
| [`server/`](server/README.md) | MongoDB scripts + FastAPI CRUD API |
| [`client/`](client/README.md) | Streamlit UI (calls the API over HTTP) |

Everything uses **one virtual environment at the project root**.

## One-time setup

From the project root (`fast-api-setup/`):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
net start MongoDB
```

Your prompt should show `(venv)`. Activate the same venv in every new terminal:

```powershell
.\venv\Scripts\Activate.ps1
```

## Run commands

Always activate the **root** venv first, then `cd` into the folder you need.

**MongoDB tutorial** (from `server/`):

```powershell
cd server
python mongodb_steps.py
```

**FastAPI API** (from `server/`):

```powershell
cd server
uvicorn main:app --reload
```

**Streamlit client** (from `client/`):

```powershell
cd client
streamlit run app.py
```

## Streamlit + FastAPI

Streamlit is a **client** — it calls FastAPI over HTTP with `httpx`, the same way a React app would use `fetch` against a Hono server. Streamlit does **not** import PyMongo.

### Request flow

```
Streamlit UI (client/app.py)
    │  button / form
    ▼
HTTP client (client/api.py)  —  GET / POST / DELETE
    │  http://localhost:8000
    ▼
FastAPI (server/main.py)
    │  route handlers
    ▼
PyMongo  →  MongoDB (course_store)
```

### Run both apps (two terminals)

**Terminal 1 — API:**

```powershell
cd server
uvicorn main:app --reload
```

**Terminal 2 — Streamlit UI:**

```powershell
cd client
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501).

- **Load courses** — sends `GET /courses` only when you click the button (not on page load).
- **Add course** — sends `POST /courses`; the list is **not** auto-refetched.
- **Delete** — sends `DELETE /courses/{id}` and removes the row from local state only.

See [server/README.md](server/README.md) and [client/README.md](client/README.md) for details.
