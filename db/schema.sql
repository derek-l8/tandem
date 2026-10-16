-- Brojans middle man schema (Postgres / Neon). Idempotent: safe to re-run.

create table if not exists items (
    id           text primary key,
    name         text not null,
    category     text not null,
    price_cents  integer not null check (price_cents >= 0),
    tags         jsonb not null default '{}'::jsonb,
    in_stock     boolean not null default true
);

create table if not exists negotiations (
    id           uuid primary key,
    buyer_input  text not null,
    brief        jsonb,
    status       text not null default 'pending',   -- pending | running | done | failed
    step         text not null default 'BRIEF',     -- see models.schemas.Step
    lease_owner  text,
    lease_until  timestamptz,
    error        text,
    created_at   timestamptz not null default now(),
    updated_at   timestamptz not null default now()
);

create table if not exists bundles (
    id              uuid primary key,
    negotiation_id  uuid not null references negotiations(id) on delete cascade,
    round           integer not null,                -- 1, 2, or 3 (final)
    name            text not null,
    item_ids        text[] not null,
    price_cents     integer not null,
    rationale       text not null,
    created_at      timestamptz not null default now()
);
create index if not exists bundles_negotiation_round on bundles (negotiation_id, round);

create table if not exists judgments (
    bundle_id       uuid primary key references bundles(id) on delete cascade,
    negotiation_id  uuid not null references negotiations(id) on delete cascade,
    round           integer not null,
    probability     real not null check (probability between 0 and 1),
    reason          text not null
);
alter table judgments add column if not exists price_score real;
alter table judgments add column if not exists fit_score real;
alter table judgments add column if not exists style_score real;

create table if not exists item_heat (
    negotiation_id  uuid not null references negotiations(id) on delete cascade,
    round           integer not null,
    item_id         text not null,
    score           real not null,
    label           text not null,                   -- hot | neutral | cold
    bundle_count    integer not null,
    primary key (negotiation_id, round, item_id)
);

create table if not exists events (
    id              bigserial primary key,
    negotiation_id  uuid not null references negotiations(id) on delete cascade,
    type            text not null,
    payload         jsonb not null,
    ts              timestamptz not null default now()
);
create index if not exists events_negotiation_id on events (negotiation_id, id);
