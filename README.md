# NATA 2026 Chatbot

A beginner-friendly **Python** chatbot that answers questions about **NATA 2026**
(National Aptitude Test in Architecture).

| Piece | Technology | Folder |
| ----- | ---------- | ------ |
| Chat UI | Streamlit | [`client/`](client/README.md) |
| Backend API | FastAPI | [`server/`](server/README.md) |
| Chat history | MongoDB | via `MONGODB_URI` |
| Knowledge search (RAG) | Qdrant + Gemini embeddings | via `QDRANT_*` |
| Answers / safety router | Google Gemini | via `GOOGLE_GENERATIVE_AI_API_KEY` |

> **Mental model:** Streamlit is only the front end. It never talks to MongoDB or
> Gemini directly. Every click becomes an HTTP call to FastAPI, just like a
> React app calling an API.

```
You (browser)
   │
   ▼
Streamlit UI  (:8501)     ← client/
   │  HTTP
   ▼
FastAPI       (:8000)     ← server/
   ├── MongoDB            (save chat sessions)
   ├── Qdrant             (search FAQs / website text)
   └── Gemini             (decide if question is allowed + write answer)
```

---

## What you need before starting

1. **Python 3.10+** installed
2. **MongoDB** running locally (or an Atlas connection string)
3. A **Google AI Studio API key** for Gemini
4. A **Qdrant** collection (Qdrant Cloud free tier is fine)

You do **not** need Node.js for this Python port.

---

## 1. One-time setup

Open a terminal in the **project root** (`fast-api-setup/`).

### Windows (PowerShell)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

### Linux / macOS

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Your prompt should show `(venv)`.

### Fill in `.env`

Open `.env` (created from [`.env.example`](.env.example)) and set at least:

| Variable | What to put |
| -------- | ----------- |
| `GOOGLE_GENERATIVE_AI_API_KEY` | Your Gemini API key |
| `QDRANT_URL` | Qdrant cluster URL |
| `QDRANT_API_KEY` | Qdrant API key (empty for unsecured local Qdrant) |
| `QDRANT_COLLECTION_NAME` | e.g. `nata_knowledge` |
| `MONGODB_URI` | Default local URI usually works |

Never commit `.env` — it is gitignored because it holds secrets.

---

## 2. Index the knowledge base (required once)

The bot answers from FAQs + website excerpts. Those texts must be embedded into Qdrant first.

```powershell
# venv already active, from project root
cd server
python scripts/generate_embeddings.py
```

Rebuild from scratch later with:

```powershell
python scripts/generate_embeddings.py --reset
```

---

## 3. Run the app (two terminals)

Each terminal needs the **root venv** activated first.

### Terminal 1 — API

```powershell
cd fast-api-setup
.\venv\Scripts\Activate.ps1
cd server
uvicorn main:app --reload
```

API: [http://localhost:8000](http://localhost:8000)  
Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### Terminal 2 — Chat UI

```powershell
cd fast-api-setup
.\venv\Scripts\Activate.ps1
cd client
streamlit run app.py
```

UI: [http://localhost:8501](http://localhost:8501)

---

## Quick checks if something fails

| Problem | Likely fix |
| ------- | ---------- |
| `uvicorn` / `streamlit` not found | Activate root `venv` from project root |
| Gemini errors | Check `GOOGLE_GENERATIVE_AI_API_KEY` in `.env` |
| Empty / weak answers | Run `generate_embeddings.py` and confirm Qdrant vars |
| Chat history not saving | Start MongoDB / fix `MONGODB_URI` |
| Streamlit cannot reach API | Keep FastAPI running on port `8000` |

More detail: [`server/README.md`](server/README.md) · [`client/README.md`](client/README.md)

---

## Project map

```
fast-api-setup/
├── .env.example          ← copy to .env and fill secrets
├── requirements.txt      ← pip packages
├── README.md             ← you are here
├── client/               ← Streamlit UI
└── server/               ← FastAPI + RAG + agents + knowledge data
```
