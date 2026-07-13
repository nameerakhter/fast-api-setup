# Server (FastAPI) — beginner guide

This folder is the **backend**. It:

1. Accepts chat requests from Streamlit
2. Checks if the question is allowed (router)
3. Searches NATA knowledge in Qdrant (RAG)
4. Streams an answer from Gemini
5. Saves the conversation in MongoDB

You run it with **Uvicorn**.

---

## Start the API

From the **project root**, activate the venv, then:

```powershell
cd server
uvicorn main:app --reload
```

- App: [http://localhost:8000](http://localhost:8000)
- Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)

`--reload` restarts the server when you change Python files (handy while learning).

---

## Important files (what each one does)

```
server/
├── main.py                 # HTTP routes (GET/POST /public-chat)
├── config.py               # Reads .env values
├── models.py               # Mongo collection names + small helpers
├── chat_store.py           # Create sessions / save messages
├── gemini_client.py        # Call Gemini (text, stream, embeddings)
├── rag.py                  # Search Qdrant for relevant chunks
├── rate_limit.py           # Simple request limits (off in development)
├── agent/
│   ├── prompts.py          # System prompts (router + chatbot + RAG)
│   ├── router.py           # “Is this question relevant?” gate
│   └── public_chatbot.py   # Full answer pipeline + streaming
├── data/
│   ├── nata_faqs.json      # FAQ knowledge
│   └── nata-website-data/  # Website-style markdown pages
└── scripts/
    └── generate_embeddings.py   # Upload knowledge into Qdrant
```

---

## API routes

| Method | URL | What it does |
| ------ | --- | ------------ |
| `GET` | `/` | Simple health / welcome JSON |
| `GET` | `/health` | `{ "ok": true }` |
| `GET` | `/public-chat?lang=en` or `hi` | Load saved messages for this browser session |
| `POST` | `/public-chat?lang=en` or `hi` | Send messages, get a **streaming** plain-text reply |

### Cookie

The API sets `public-chat-session-id` so the same visitor keeps one chat history.

### Example POST body

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Is there negative marking in NATA 2026?",
      "parts": [{ "type": "text", "text": "Is there negative marking in NATA 2026?" }]
    }
  ]
}
```

Response: streamed `text/plain` tokens (Streamlit reads these with `st.write_stream`).

---

## Load knowledge into Qdrant

Do this **once** after filling `.env` (and again when FAQs/markdown change):

```powershell
cd server
python scripts/generate_embeddings.py
```

Wipe and rebuild the collection:

```powershell
python scripts/generate_embeddings.py --reset
```

What the script does:

1. Splits website markdown into sections
2. Turns each FAQ into a text chunk
3. Creates Gemini embeddings
4. Upserts vectors into your Qdrant collection

---

## How a chat request flows

```
POST /public-chat
   │
   ├─ save user message → MongoDB
   ├─ router agent → is this NATA-related / safe?
   │     ├─ no  → short refusal (streamed)
   │     └─ yes → search Qdrant → Gemini answer (streamed)
   └─ save assistant message → MongoDB
```

---

## Environment variables used here

See the root [`.env.example`](../.env.example). The server loads `.env` from the **project root**.

Common ones:

- `MONGODB_URI`
- `GOOGLE_GENERATIVE_AI_API_KEY`
- `QDRANT_URL`, `QDRANT_API_KEY`, `QDRANT_COLLECTION_NAME`
- `EMBEDDING_DIMENSIONS` (must match what you indexed)
- `APP_ENV=development` skips rate limiting locally
