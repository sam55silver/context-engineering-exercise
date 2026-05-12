# Context Engineering Exercise — Watchlist

A tiny full-stack watchlist app. **It has 4 bugs hidden inside it.**

Your job: use your AI coding tool's context-management features (e.g. `@` to include files/folders in OpenCode) to find all four, explain what each one is, and where it lives.

## Stack

- **Backend**: FastAPI + SQLite (Python 3.11+, managed with `uv`)
- **Frontend**: Vite + React + TypeScript

## Run it

You'll need two terminals.

### Backend

```bash
cd backend
uv sync
uv run uvicorn main:app --reload
```

Backend serves on `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend serves on `http://localhost:5173`.

## The challenge

Open the app. Poke around. Three tabs: **My Watchlist**, **Browse Catalog**, **Watched Today**.

Things should "mostly work" — but there are 4 bugs. Some are visible immediately, some only appear when you try certain actions. Some span both frontend and backend.

For each bug, tell us:

1. **What's wrong** (the symptom)
2. **Where it lives** (file + line)
3. **Why it happens** (the root cause)
4. **The fix**

### Hints

- Try every tab.
- Try every button.
- Pay attention to *what* renders, not just *whether* it renders.
- Don't trust types alone — types lie when the server is on the other side.
- Some bugs are only visible in certain conditions. Think about edge cases.

### Using your AI tool

This exercise is designed to reward good **context engineering**:

- Use `@` (or your tool's equivalent) to include both the frontend file *and* the related backend file when investigating cross-stack behavior.
- Ask your AI: "what does this endpoint return, and how does the frontend consume it?"
- The bugs are findable without AI — but they're *much* faster to find when you pull the right context.

Good luck. 🎬
