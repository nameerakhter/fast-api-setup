# Course Store — Client

Small **Streamlit** app for the course store UI. Not connected to the FastAPI server yet.

Uses the **root** virtual environment — see [../README.md](../README.md) for setup.

## Run

Root venv active, inside `client/`:

```powershell
streamlit run app.py
```

Opens in your browser (default: http://localhost:8501).

Run the API separately in another terminal (`cd server`, `uvicorn main:app --reload`) when you wire this up later.

## Next step

Connect this app to `server/main.py` with HTTP requests (GET, POST, PATCH, DELETE).
