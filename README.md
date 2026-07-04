# FastAPI Setup

Course store teaching repo: **PyMongo** + **FastAPI** backend, **Streamlit** client.

| Folder | What it is |
| ------ | ---------- |
| [`server/`](server/README.md) | MongoDB scripts + FastAPI CRUD API |
| [`client/`](client/README.md) | Streamlit UI (not wired to the API yet) |

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

See [server/README.md](server/README.md) and [client/README.md](client/README.md) for details.
