# Client (Streamlit) — beginner guide

This folder is the **chat UI**. It looks like a small website, but it is still a
Python script. Streamlit redraws the page whenever you click a button or send a message.

**Important:** the client only uses HTTP. It does **not** import PyMongo, Gemini,
or Qdrant. All real work happens in `server/`.

---

## Start the UI

1. Make sure FastAPI is already running on [http://localhost:8000](http://localhost:8000)
2. From the **project root**, activate the venv, then:

```powershell
cd client
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501).

---

## Files

| File | Role |
| ---- | ---- |
| `app.py` | Page layout, language toggle, suggestions, chat bubbles |
| `api.py` | `httpx` helpers: load history + stream chat from FastAPI |
| `.streamlit/config.toml` | Light theme colors |

---

## What you can do in the UI

- Switch **English / हिन्दी**
- Tap a **suggested question** (same ideas as the TypeScript NATA chatbot)
- Type your own question and watch the answer **stream** in
- Click **New chat** to start a fresh session

---

## How the client talks to the server

```
app.py
  │
  ├─ api.get_messages(lang, session_id)
  │     → GET  http://localhost:8000/public-chat?lang=...
  │
  └─ api.stream_chat(messages, lang, session_id)
        → POST http://localhost:8000/public-chat?lang=...
        → yields text chunks into st.write_stream(...)
```

Session id is kept in Streamlit `session_state` and sent as the
`public-chat-session-id` cookie so MongoDB history can continue.

---

## If the UI looks broken

| Symptom | Check |
| ------- | ----- |
| Errors about connection / refused | Is `uvicorn` running in another terminal? |
| History never loads | MongoDB + API health; try **New chat** |
| Answers never appear | Gemini key / Qdrant indexing on the server side |

Return to the root [README](../README.md) for full setup.
