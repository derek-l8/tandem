# brojans
Troylabs

## Middle man backend (FastAPI on Vercel)

Runs buyer agent ↔ seller agent through 3 rounds:
`BRIEF → R1_PROPOSE → R1_JUDGE → R2_REFINE → R2_JUDGE → FINAL → DONE`.
After each judging round the middle man scores every item (mean buy-probability of the
bundles containing it) and tells the seller which items are hot and which are cold. Cold
items are rejected in later rounds.

| Endpoint | |
|---|---|
| `POST /api/negotiations` `{buyer_input, brief?}` | create; returns `{id, stream_url}` |
| `GET /api/negotiations/{id}/stream` | SSE: replays history, runs/resumes the negotiation, streams live (`?after=` / `Last-Event-ID`) |
| `GET /api/negotiations/{id}` | JSON snapshot: rounds, bundles, judgments, heat, final offer |
| `POST /api/negotiations/{id}/retry` | re-arm a failed negotiation (resumes at the failed step) |

SSE event types: `brief`, `bundles_proposed`, `bundle_judged`, `heat`, `final_offer`, `done`, `error`.

### Setup
1. Vercel → Storage → add **Neon Postgres** (sets `DATABASE_URL`, use the pooled URL) and add `OPENAI_API_KEY` (see *API keys* below).
2. `DATABASE_URL=... python scripts/setup_db.py` (applies `db/schema.sql`, seeds `db/seed_items.json`).
3. `vercel deploy`.

Optional env: `OPENAI_MODEL` (default `gpt-5.4`), `OPENAI_REASONING_EFFORT` (default `medium`; set empty for non-reasoning models).

### Local dev
```
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/pytest                        # fake agents, in-memory store
.venv/bin/uvicorn api.index:app --reload --env-file .env.local
curl -X POST localhost:8000/api/negotiations -H 'content-type: application/json' -d '{"buyer_input":"streetwear, size M, under $400"}'
curl -N localhost:8000/api/negotiations/<id>/stream
```
Without `DATABASE_URL`, an in-memory store with the seed inventory is used. That's fine locally, but not on Vercel.

### API keys
Never commit keys. `.env` and `.env.local` are gitignored.

- **Local:** create `.env.local` in the repo root:
  ```
  OPENAI_API_KEY=sk-...
  # DATABASE_URL=postgres://...   (optional; omit to use the in-memory store)
  ```
  and run uvicorn with `--env-file .env.local` as shown above.
- **Vercel:** Project → Settings → Environment Variables → add `OPENAI_API_KEY` for Production
  (and Preview if you use preview deploys), or run `vercel env add OPENAI_API_KEY`. Redeploy after
  adding. Pull them locally with `vercel env pull .env.local`.
