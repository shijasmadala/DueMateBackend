# DueMate Backend

DueMate reminds people about subscriptions, bills, and document expiry dates.

This repository currently contains the **database layer only**: SQLAlchemy models, a database session, Alembic migrations, and a tiny FastAPI app with a health check. Authentication, push sending, and business APIs are not implemented yet.

## What you need

- macOS (Apple Silicon is fine)
- Python 3.12+ (this project was started with Python 3.15)
- [Postgres.app](https://postgresapp.com/) with PostgreSQL 18
- A database named `duemate`

## Folder structure

```text
DueMateBackend/
├── .env.example              # Safe template for database settings
├── .gitignore                # Keeps .env, .venv, and cache files out of git
├── README.md
├── requirements.txt          # Python packages and versions
├── alembic.ini               # Alembic's main config file
├── alembic/
│   ├── env.py                # Tells Alembic how to connect and find models
│   ├── script.py.mako        # Template used to generate new migration files
│   └── versions/             # One Python file per schema change
├── app/
│   ├── main.py               # FastAPI app (health check only)
│   ├── core/
│   │   ├── config.py         # Reads DATABASE_URL from the environment
│   │   └── database.py       # Engine, session factory, get_db()
│   └── models/
│       ├── base.py           # Declarative base, UUID and timestamp mixins
│       ├── enums.py          # Allowed string values used by the models
│       ├── user.py
│       ├── payment_item.py
│       ├── document.py
│       ├── payment_record.py
│       ├── reminder_preference.py
│       ├── device_token.py
│       └── reminder_delivery.py
└── .venv/                    # Local virtual environment (not committed)
```

## Table relationships

Every row that is not a user includes `user_id`. That keeps each person's data isolated and makes it possible to query "all reminders for this user" without guessing through joins.

```text
users
  ├── payment_items (item_type = subscription | bill)
  │     ├── payment_records
  │     ├── reminder_preferences
  │     └── reminder_deliveries
  ├── documents
  │     ├── reminder_preferences
  │     └── reminder_deliveries
  ├── device_tokens
  └── reminder_deliveries
```

- **users**: account identity. `password_hash` is stored for a future auth step; it is nullable so we can create users while auth APIs do not exist yet.
- **payment_items**: one row per subscription or bill. `recurrence` is `monthly`, `yearly`, or `one_time`. Money uses `NUMERIC(12, 2)`.
- **documents**: one row per document with an `expiry_date`.
- **payment_records**: history of amounts paid against a payment item.
- **reminder_preferences**: reminder settings for **either** a payment item **or** a document, never both. `days_before` plus `remind_at` decide when to notify.
- **device_tokens**: Android/iOS devices registered for push notifications.
- **reminder_deliveries**: one row per reminder occurrence. The unique pair `(reminder_preference_id, target_event_date)` prevents sending the same reminder twice for the same due/expiry date.

Foreign keys use `ON DELETE CASCADE`, so deleting a user (or a payment item/document) removes the dependent rows.

## Local setup

### 1. Create and activate a virtual environment

A virtual environment keeps this project's packages separate from the rest of your Mac.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Your prompt should start with `(.venv)`.

### 2. Install Python packages

```bash
python -m pip install -r requirements.txt
```

This installs FastAPI, SQLAlchemy, Alembic, psycopg (the PostgreSQL driver), and pydantic-settings.

### 3. Create the database in Postgres.app

1. Open Postgres.app and start the server if it is not running.
2. Open a SQL shell. Either click **psql** in Postgres.app or run:

```bash
psql -d postgres
```

3. Create the database if it does not already exist. This command does **not** drop or replace an existing database:

```sql
SELECT datname FROM pg_database WHERE datname = 'duemate';
```

If that returns no row:

```sql
CREATE DATABASE duemate;
```

4. Leave the SQL shell:

```sql
\q
```

### 4. Configure environment variables

Copy the example file:

```bash
cp .env.example .env
```

Open `.env` and confirm `DATABASE_URL` matches your Postgres.app user, host, port, and database name.

- Do not commit `.env`.
- Do not put production passwords in this file.
- Postgres.app local connections often work with **no password**. If your install requires one, add it in the URL as `postgresql+psycopg://USERNAME:PASSWORD@localhost:5432/duemate`.

`postgresql+psycopg://` tells SQLAlchemy to use the psycopg 3 driver.

### 5. Apply migrations (after you have reviewed the migration file)

Alembic stores each schema change as a Python file under `alembic/versions/`. Applying a migration executes that file against PostgreSQL.

```bash
alembic upgrade head
```

`head` means "the newest revision in this project".

To see the current database revision:

```bash
alembic current
```

To preview SQL without applying it:

```bash
alembic upgrade head --sql
```

### 6. Run the API (optional)

```bash
uvicorn app.main:app --reload
```

Then open `http://127.0.0.1:8000/health`. You should see `{"status":"ok"}`.

## How Alembic fits together

1. You change SQLAlchemy models in `app/models/`.
2. `alembic revision --autogenerate -m "short description"` compares those models to the live database and writes a new file in `alembic/versions/`.
3. You **read that file**. Autogenerate is a draft. It can miss CHECK details or include noise.
4. Only then do you run `alembic upgrade head`.

Alembic records applied revisions in a table named `alembic_version`. That is how it knows what to run next. It will not drop your database unless a migration file explicitly says so. The initial migration in this project only **creates** tables.

## Creating a new migration later

```bash
alembic revision --autogenerate -m "add column to users"
# read the generated file
alembic upgrade head
```

To undo the most recent revision during local development:

```bash
alembic downgrade -1
```

That runs the `downgrade()` function in the latest migration. Use it only when you understand what it will drop.
# DueMateBackend
