# FastAPI Setup

Teaching repo for backend development with **Python**, **PyMongo**, and **FastAPI**.

## Start here

All intern-facing material lives in **`server/`**:

```powershell
cd server
```

See **[server/README.md](server/README.md)** for setup, teaching order, and curl examples.

### Quick commands (from `server/`)

```bash
pip install -r requirements.txt
python mongodb_steps.py                              # MongoDB tutorial (steps 1–8)
uvicorn main.step_by_step.example:app --reload       # API tutorial (steps 1–6)
uvicorn main:app --reload                            # Full course store API
```

## What's in the repo

| Path | Purpose |
| ---- | ------- |
| `server/` | **Main teaching folder** — scripts, step-by-step API, full FastAPI app |
| `main.py`, `models/` (root) | Earlier standalone MongoDB demo — use `server/` for the full curriculum |
