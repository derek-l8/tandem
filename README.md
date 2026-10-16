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
1. Vercel → Storage → add **Neon Postgres** (sets `DATABASE_URL`, use the pooled URL) and add `ANTHROPIC_API_KEY`.
2. `DATABASE_URL=... python scripts/setup_db.py` (applies `db/schema.sql`, seeds `db/seed_items.json`).
3. `vercel deploy`.

Optional env: `BROJANS_MODEL` (default `claude-opus-5-5`), `BROJANS_EFFORT` (default `medium`).

### Local dev
```
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/pytest                        # fake agents, in-memory store
ANTHROPIC_API_KEY=... .venv/bin/uvicorn api.index:app --reload
curl -X POST localhost:8000/api/negotiations -H 'content-type: application/json' -d '{"buyer_input":"streetwear, size M, under $400"}'
curl -N localhost:8000/api/negotiations/<id>/stream
```
Without `DATABASE_URL`, an in-memory store with the seed inventory is used. That's fine locally, but not on Vercel.
