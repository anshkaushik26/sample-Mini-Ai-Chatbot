# Rivram Mini — Backend

FastAPI backend: conversations + Gemini chat, with genuine streaming.

## Endpoints

- `GET /health`
- `POST /conversations` — `{ "title": "optional" }`
- `GET /conversations`
- `GET /conversations/{id}/messages`
- `DELETE /conversations/{id}`
- `POST /chat` — `{ "conversation_id": "...", "message": "..." }`
- `POST /chat/stream` — same body, streams plain text chunks

## Local setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in GEMINI_API_KEY
uvicorn app:app --host 0.0.0.0 --port 8001
```

Runs on port 8001 locally (not 8000) to avoid clashing with any other
backend you might already have running. Render sets `$PORT` itself in
production — see root README.

## Storage

`storage/conversations.json` is flat-file storage — no database. **Render's
free-tier filesystem is ephemeral**: conversations are lost on every
restart/redeploy. That's expected and acceptable for this deployment test.

## Environment variables

| Variable | Purpose |
|---|---|
| `GEMINI_API_KEY` | Gemini API key. Never exposed to the frontend. |
| `GEMINI_MODEL` | Gemini model id, e.g. `gemini-2.5-flash` |
| `FRONTEND_URL` | Vercel frontend origin, for CORS |
