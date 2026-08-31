# Rivram Mini — Frontend

Next.js + TypeScript chat UI. Calls the FastAPI backend directly over
HTTPS from the browser — no Next.js API route proxy.

## Local setup

```bash
npm install
cp .env.example .env.local   # point at your backend
npm run dev -- --port 3001
```

## Environment variables

| Variable | Purpose |
|---|---|
| `NEXT_PUBLIC_BACKEND_URL` | Base URL of the FastAPI backend, e.g. `https://my-test-backend.onrender.com` |

Never put `GEMINI_API_KEY` here or prefix it with `NEXT_PUBLIC_`.
