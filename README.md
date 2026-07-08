# FastAPI Setup

Course store teaching repo: **PyMongo** + **FastAPI** backend, **Streamlit** client.

| Folder | What it is |
| ------ | ---------- |
| [`server/`](server/README.md) | MongoDB scripts + FastAPI CRUD API |
| [`client/`](client/README.md) | Streamlit UI (calls the API over HTTP) |

Everything uses **one virtual environment at the project root** (`fast-api-setup/venv/`).

There is **no** separate venv inside `server/` or `client/`. If you `cd server` or `cd client` without activating the root venv first, commands like `uvicorn` and `streamlit` will fail with **command not found**.

## One-time setup

From the project root (`fast-api-setup/`):

**Linux / macOS (bash):**

```bash
python -m venv venv
source venv/bin/activate    # prompt shows (venv)
pip install -r requirements.txt
cp .env.example .env
# start MongoDB (e.g. sudo systemctl start mongod)
```

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1    # prompt shows (venv)
pip install -r requirements.txt
copy .env.example .env
net start MongoDB
```

Your prompt should show `(venv)` when the environment is active.

## Activate venv (every new terminal)

Open a terminal, go to the **project root**, activate venv, **then** `cd` into `server/` or `client/`:

**Linux / macOS:**

```bash
cd fast-api-setup          # project root
source venv/bin/activate   # (venv) must appear in your prompt
cd server                  # or: cd client
```

**Windows (PowerShell):**

```powershell
cd fast-api-setup
.\venv\Scripts\Activate.ps1
cd server                  # or: cd client
```

If you see `bash: uvicorn: command not found`, you forgot to activate the root venv (or never ran `pip install -r requirements.txt`).

If you see `No module named 'dotenv'`, the venv is active but dependencies are outdated — from project root run `pip install -r requirements.txt`.

## Run commands

**Always:** project root → activate venv → `cd server` or `cd client` → run command.

**MongoDB tutorial** (`server/`):

```bash
# after: source venv/bin/activate  &&  cd server
python mongodb_steps.py
```

**FastAPI API** (`server/`):

```bash
# after: source venv/bin/activate  &&  cd server
uvicorn main:app --reload
```

**Streamlit client** (`client/`):

```bash
# after: source venv/bin/activate  &&  cd client
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

Each terminal needs its **own** venv activation (same root `venv/`).

**Terminal 1 — API (Linux / macOS):**

```bash
cd fast-api-setup
source venv/bin/activate
cd server
uvicorn main:app --reload
```

**Terminal 2 — Streamlit UI (Linux / macOS):**

```bash
cd fast-api-setup
source venv/bin/activate
cd client
streamlit run app.py
```

**Windows (PowerShell)** — same idea, use `.\venv\Scripts\Activate.ps1` instead of `source venv/bin/activate`.

Open [http://localhost:8501](http://localhost:8501).

- **Load courses** — sends `GET /courses` only when you click the button (not on page load).
- **Add course** — sends `POST /courses`; the list is **not** auto-refetched.
- **Delete** — sends `DELETE /courses/{id}` and removes the row from local state only.

See [server/README.md](server/README.md) and [client/README.md](client/README.md) for details.
