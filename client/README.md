# Course Store — Client

**Streamlit** UI for the course store. Calls the FastAPI server over HTTP — no PyMongo here.

Uses the **root** virtual environment — see [../README.md](../README.md) for setup.

## Run

Root venv active, inside `client/`:

```powershell
streamlit run app.py
```

Opens in your browser (default: http://localhost:8501).

Run the API separately in another terminal:

```powershell
cd server
uvicorn main:app --reload
```

## How it connects

```
client/app.py  →  client/api.py (httpx)  →  server/main.py  →  MongoDB
```

- **Load courses** — `GET /courses` on button click only
- **Add course** — `POST /courses`, does not auto-refetch the list
- **Delete** — `DELETE /courses/{id}`, updates local state only
