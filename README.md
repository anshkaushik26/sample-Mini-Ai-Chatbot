 Deployment Test

A small, standalone replica of  architecture, built to prove out
the Vercel + Render + Gemini deployment path before committing to it for
the real project. *** — it does not
import, modify, or depend on it in any way.

## Architecture

```
Browser
   |
   |  HTTPS (direct, no Next.js API proxy)
   v
Next.js frontend (Vercel)
   |
   |  HTTPS
   v
FastAPI backend (Render)
   |
   v
Gemini API
```

The browser calls the FastAPI backend directly via `NEXT_PUBLIC_BACKEND_URL`.
The Gemini API key lives only on the backend and is never sent to the
frontend or the browser.

## Project layout

```
backend/     FastAPI app: chat, conversations, Gemini streaming
frontend/    Next.js + TypeScript chat UI
```

## Local setup

Backend:

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in GEMINI_API_KEY
uvicorn app:app --host 0.0.0.0 --port 8001
```

Frontend:

```bash
cd frontend
npm install
cp .env.example .env.local   # NEXT_PUBLIC_BACKEND_URL=http://localhost:8001
npm run dev -- --port 3001
```

Open http://localhost:3001.

## Environment variables

Backend (`backend/.env`):

| Variable | Example |
|---|---|
| `GEMINI_API_KEY` | (secret, from Google AI Studio) |
| `GEMINI_MODEL` | `gemini-2.5-flash` |
| `FRONTEND_URL` | `https://my-test-app.vercel.app` |

Frontend (`frontend/.env.local` / Vercel project settings):

| Variable | Example |
|---|---|
| `NEXT_PUBLIC_BACKEND_URL` | `https://my-test-backend.onrender.com` |

`GEMINI_API_KEY` must **never** appear in the frontend and must **never**
be prefixed with `NEXT_PUBLIC_`.

## Render deployment (backend)

1. New → Web Service, connect this repo.
2. **Root directory:** `backend`
3. **Build command:** `pip install -r requirements.txt`
4. **Start command:** `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. **Environment variables:** `GEMINI_API_KEY`, `GEMINI_MODEL`, `FRONTEND_URL`
   (set `FRONTEND_URL` to your Vercel URL once you have it — you can
   redeploy after Vercel is live).
6. Plan: **Free**.
7. Deploy, then confirm `https://<your-service>.onrender.com/health`
   returns `{"status":"ok"}`.

Render free instances spin down after inactivity and cold-start on the
next request — expect the first request after idle to be slow. This is
expected free-tier behavior, not a bug.

## Vercel deployment (frontend)

1. New Project, import this repo.
2. **Root directory:** `frontend`
3. **Environment variable:** `NEXT_PUBLIC_BACKEND_URL=https://<your-render-url>`
4. Deploy.
5. Go back to Render and set `FRONTEND_URL` to the resulting `*.vercel.app`
   URL, then redeploy the backend so CORS allows it.

## Troubleshooting

- **CORS error in browser console** — `FRONTEND_URL` on Render doesn't
  match the Vercel URL exactly (check `https://` and no trailing slash).
- **Streaming looks like it arrives all at once** — some proxies buffer
  responses; Render + fetch's `ReadableStream` reader worked correctly in
  local testing (see below). If it doesn't stream in production, check
  that nothing between browser and Render is buffering (e.g. certain CDN
  configs) — not applicable in Render's default setup.
- **500 on `/chat` or `/chat/stream`** — check Render logs; almost always
  a missing/invalid `GEMINI_API_KEY` or an unsupported `GEMINI_MODEL`.
- **Conversations disappear after a while** — expected. Render free's
  filesystem is ephemeral and resets on restart/redeploy/idle spin-down.
- **Port bind errors locally** — this project deliberately runs on 8001
  (backend) / 3001 (frontend) locally, not 8000/3000, to avoid clashing
  with any other app you have running on those ports.

## Memory test results

Measured locally with the production-style start command
(`uvicorn app:app --host 0.0.0.0 --port 8001`), using `ps -o rss=` on the
running process, real Gemini API calls (`gemini-3.5-flash`):

| Point measured | RSS |
|---|---|
| Startup | 78.2 MB |
| After `/health` | 78.9 MB |
| After conversation create/list/get | 79.0 MB |
| Immediately before a chat request | 84.1 MB |
| During active streaming | 84.2 MB |
| After stream completes | 65.4 MB |
| After 5 additional sequential chats | 65.4 MB |

**Peak observed: ~85 MB.** This is far below Render Free's 512 MB limit,
with roughly 6x headroom even under repeated use. Memory did not grow
across repeated chats — no leak observed in this test run.

## Test report

### Backend
- Starts cleanly with the exact production start command — yes
- RAM usage — ~78–85 MB steady state, peak ~85 MB (see table above)
- `/health` — verified, `{"status":"ok"}`
- `/chat` — verified against live Gemini API, correct reply
- `/chat/stream` — verified against live Gemini API; genuine
  `StreamingResponse` (no timer-based faking), confirmed progressive
  delivery in a real headless-browser test
- Conversation persistence — verified: create, list, get messages, delete
  all round-trip correctly through `storage/conversations.json`

### Gemini
- API request successful — yes (`gemini-3.5-flash`, confirmed available
  via `client.models.list()` with the supplied key)
- Streaming successful — yes, chunked text arrived progressively and was
  reassembled and persisted correctly

### Frontend
- Builds successfully — `npm run build` completes with no errors
- Connects to backend — verified in a real Chromium browser (Playwright):
  new chat created, message sent, streamed reply rendered, no console
  errors
- No secret in build output — confirmed `GEMINI` does not appear anywhere
  under `.next/`

### Deployment readiness
- Render-ready — yes: binds `0.0.0.0`, reads `$PORT`, minimal
  dependencies (`fastapi`, `uvicorn`, `google-genai`, `python-dotenv`),
  no Docker, no external database
- Vercel-ready — yes: standard Next.js app, single public env var
- Environment variables documented — yes (this file + both `.env.example`
  files)
- CORS configured — yes: `allow_origins` is explicit
  (`localhost:3000`, `localhost:3001` for local dev, plus `FRONTEND_URL`),
  not `["*"]`; verified both a disallowed origin (`400 Disallowed CORS
  origin`) and an allowed origin (proper `Access-Control-Allow-Origin`
  header) with real preflight requests

### Architecture

Confirmed working end-to-end, locally, with real HTTP requests and a real
Gemini API key:

```
Vercel-style frontend (Next.js dev server)
        |
        v
Render-style backend (uvicorn, production start command)
        |
        v
Gemini API (gemini-3.5-flash)
```

The only step not yet verified is the actual cross-origin HTTPS hop
between deployed Vercel and Render instances — that requires the real
deployment, which you'll perform yourself per the steps above.

## Note on this test run

While setting this project up, port 8000 and port 3000 on this machine
turned out to already be occupied by what appears to be your real Rivram
backend and frontend, running locally. My first backend test request
briefly hit that real backend by accident and created one stray test
conversation there. It was deleted immediately (with your explicit
approval) and confirmed removed — no other interaction with the real
project occurred. This test project now deliberately uses ports 8001 and
3001 locally to avoid any recurrence.
