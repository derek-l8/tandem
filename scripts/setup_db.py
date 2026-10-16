"""Apply db/schema.sql and upsert db/seed_items.json into the Postgres at DATABASE_URL.

Usage: DATABASE_URL=postgres://... python scripts/setup_db.py [--no-seed]
"""

import json
import os
import sys

import psycopg
from psycopg.types.json import Jsonb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main() -> None:
    dsn = os.environ["DATABASE_URL"]
    with psycopg.connect(dsn) as conn:
        with open(os.path.join(ROOT, "db", "schema.sql")) as f:
            conn.execute(f.read())
        print("schema applied")
        if "--no-seed" in sys.argv:
            return
        with open(os.path.join(ROOT, "db", "seed_items.json")) as f:
            items = json.load(f)
        with conn.cursor() as cur:
            cur.executemany(
                """insert into items (id, name, category, price_cents, tags, in_stock)
                   values (%s, %s, %s, %s, %s, %s)
                   on conflict (id) do update set name = excluded.name, category = excluded.category,
                       price_cents = excluded.price_cents, tags = excluded.tags, in_stock = excluded.in_stock""",
                [(i["id"], i["name"], i["category"], i["price_cents"], Jsonb(i.get("tags", {})),
                  i.get("in_stock", True)) for i in items],
            )
        print(f"seeded {len(items)} items")


if __name__ == "__main__":
    main()
