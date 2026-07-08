# Course Store — Client

**Streamlit** UI for the course store. Calls the FastAPI server over HTTP — no PyMongo here.

Uses the **root** virtual environment — there is no `venv/` inside `client/`.

## Run

**Step 1 — activate root venv** (from project root):

```bash
cd fast-api-setup
source venv/bin/activate    # Linux/macOS — prompt shows (venv)
```

```powershell
cd fast-api-setup
.\venv\Scripts\Activate.ps1    # Windows
```

**Step 2 — run Streamlit** (from `client/`):

```bash
cd client
streamlit run app.py
```

Opens in your browser (default: http://localhost:8501).

## API in a second terminal

Same pattern: activate root venv first, then `cd server`:

```bash
cd fast-api-setup
source venv/bin/activate
cd server
uvicorn main:app --reload
```

If `streamlit` or `uvicorn` is **command not found**, the root venv is not active. Go back to `fast-api-setup/` and run `source venv/bin/activate`.

## How it connects

```
client/app.py  →  client/api.py (httpx)  →  server/main.py  →  MongoDB
```

- **Load courses** — `GET /courses` on button click only
- **Add course** — `POST /courses`, does not auto-refetch the list
- **Delete** — `DELETE /courses/{id}`, updates local state only
