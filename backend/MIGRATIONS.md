# Database Architecture Refactoring

## Overview

The database layer has been refactored to separate concerns:

- **Migrations**: Schema changes (structure, tables, columns)
- **Seeds**: Data initialization (sample/default data)
- **Connection Management**: Database access (in `db.py`)

This separation provides several benefits:

1. Schema can evolve independently of seed data
2. Database can be reset deterministically
3. Tests can use a clean database easily
4. Clear audit trail of what changed when
5. Different environments can use different seeds

## Architecture

### Directory Structure

```
backend/
├── db.py                 # Connection management (updated)
├── migrate.py            # Migration runner
├── seed.py               # Seeder runner
├── migrations/           # Schema migration files
│   ├── __init__.py       # Migration base class
│   └── _001_create_tables.py
├── seeds/                # Data seed files
│   ├── __init__.py       # Seeder base class
│   └── _seed_titles.py
└── scripts/              # Operational scripts
    ├── reset_db.py       # Reset everything
    ├── seed_db.py        # Seed data only
    └── migrate.py        # Run migrations only
```

### Key Components

#### 1. Migrations System (`migrate.py`)

Migrations track schema changes:
- Each migration has a unique name (e.g., `001_create_tables`)
- Each migration has `up()` (apply) and `down()` (revert) methods
- Applied migrations are logged in `.migrations.json`
- Migrations run in order and are idempotent

**MigrationRunner** provides:
- `migrate()`: Apply all pending migrations
- `rollback(steps=1)`: Revert the last N migrations
- `get_pending_migrations()`: List migrations not yet applied
- `get_applied_migrations()`: List migrations that have run

#### 2. Seeds System (`seed.py`)

Seeders insert sample/default data:
- Each seeder implements the `Seeder` interface
- Seeders are independent of migrations
- Can be run multiple times safely
- Ideal for initializing sample data

**SeederRunner** provides:
- `seed(name=None)`: Run seeders by name or all seeders
- Handles database connections safely

#### 3. Connection Management (`db.py`)

Simplified to handle only:
- Creating database connections via `get_conn()`
- Orchestrating startup via `init_db()` (now thin wrapper)

**Startup Flow:**
```
app startup
  → lifespan context manager
    → init_db()
      → run pending migrations
      → seed data
  → app is ready to use
```

## Usage

### Running the App (Normal Flow)

```bash
cd backend
python -m uvicorn main:app --reload
```

The app startup automatically:
1. Applies any pending migrations
2. Seeds data if not already seeded

### Manual Scripts

#### Reset entire database

```bash
python scripts/reset_db.py
```

This:
1. Rolls back all migrations
2. Clears migration log
3. Re-applies all migrations
4. Re-seeds data

**Use when:** Local development, testing, or after schema changes

#### Seed data only

```bash
python scripts/seed_db.py
```

This inserts or updates seed data without touching schema.

**Use when:** You've wiped data but want to restore sample data

#### Run migrations only

```bash
python scripts/migrate.py
```

This applies all pending migrations.

**Use when:** Deploying to production or testing schema changes

### Creating New Migrations

To add a schema change:

1. Create a new file in `backend/migrations/` with format `_NNN_description.py`:

```python
from migrations import Migration
import sqlite3

class AddUserPreferences(Migration):
    name = "002_add_user_preferences"
    
    def up(self, conn: sqlite3.Connection) -> None:
        cur = conn.cursor()
        cur.execute("ALTER TABLE watchlist ADD COLUMN rating INTEGER")
        conn.commit()
    
    def down(self, conn: sqlite3.Connection) -> None:
        # SQLite doesn't support DROP COLUMN easily, use transactions
        cur = conn.cursor()
        cur.executescript("""
            CREATE TABLE watchlist_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title_id INTEGER NOT NULL UNIQUE REFERENCES titles(id),
                is_watched INTEGER NOT NULL DEFAULT 0,
                added_at TEXT NOT NULL DEFAULT (datetime('now')),
                watched_at TEXT
            );
            INSERT INTO watchlist_new SELECT id, title_id, is_watched, added_at, watched_at FROM watchlist;
            DROP TABLE watchlist;
            ALTER TABLE watchlist_new RENAME TO watchlist;
        """)
        conn.commit()
```

2. Add it to the `_load_migrations()` function in `migrate.py`:

```python
def _load_migrations() -> list:
    """Load all migration classes dynamically."""
    migrations = []
    
    # Import 001_create_tables
    mod = importlib.import_module("migrations._001_create_tables")
    migrations.append(mod.CreateTables())
    
    # Import 002_add_user_preferences
    mod = importlib.import_module("migrations._002_add_user_preferences")
    migrations.append(mod.AddUserPreferences())  # Added
    
    return migrations
```

3. Run migrations:

```bash
python scripts/migrate.py
```

### Creating New Seeds

To add initial data:

1. Create a new file in `backend/seeds/` with format `_seed_*.py`:

```python
from seeds import Seeder
import sqlite3

class SeedUsers(Seeder):
    name = "seed_users"
    
    def seed(self, conn: sqlite3.Connection) -> None:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        if cur.fetchone()[0] > 0:
            print("Users already seeded, skipping")
            return
        
        cur.execute("INSERT INTO users (name) VALUES (?)", ("Default User",))
        conn.commit()
        print("Seeded 1 user")
```

2. Add it to the `_load_seeders()` function in `seed.py`:

```python
def _load_seeders() -> list:
    """Load all seeder classes dynamically."""
    seeders = []
    
    # Import seed_titles
    mod = importlib.import_module("seeds._seed_titles")
    seeders.append(mod.SeedTitles())
    
    # Import seed_users
    mod = importlib.import_module("seeds._seed_users")
    seeders.append(mod.SeedUsers())  # Added
    
    return seeders
```

3. Run seeders:

```bash
python scripts/seed_db.py
```

## Migration Log

Applied migrations are tracked in `.migrations.json`:

```json
{
  "applied": [
    "001_create_tables"
  ]
}
```

This file is auto-generated and shouldn't be edited manually.

## Differences from Previous Approach

| Aspect | Old | New |
|--------|-----|-----|
| Schema creation | In `db.py` `init_db()` | In `migrations/` |
| Data seeding | In `db.py` `init_db()` | In `seeds/` |
| Tracking changes | Not tracked | `.migrations.json` |
| Reset data | Requires code changes | `scripts/reset_db.py` |
| Schema testing | Difficult | Easy (can run specific migrations) |
| Coupling | Tight (schema + data) | Loose (independent) |
| Evolution | Hard (mixed concerns) | Easy (clear separation) |

## Testing

With this architecture, tests can:

1. Create a clean database
2. Apply only the migrations needed
3. Seed only the data needed
4. Reset between tests

Example test setup:

```python
import sqlite3
from migrate import MigrationRunner
from seed import SeederRunner

def test_with_fresh_db():
    # Create test database
    test_db = "test.db"
    sqlite3.connect(test_db).close()
    
    # Apply migrations
    runner = MigrationRunner(db_path=test_db)
    runner.migrate()
    
    # Seed data
    seeder = SeederRunner(db_path=test_db)
    seeder.seed()
    
    # Run tests...
    
    # Cleanup
    Path(test_db).unlink()
```

## Troubleshooting

### "Database not found" error

The database file must exist before migrations run. The app startup creates it automatically, but if running scripts manually:

```bash
# Create empty database
touch watchlist.db
python scripts/migrate.py
```

### Migration failed

If a migration fails partway through:

1. Check the error message
2. Fix the migration code
3. Rollback: `python -c "from migrate import get_runner; get_runner().rollback()"`
4. Fix the migration and try again

### Seeds not inserting

Seeds check if data already exists before inserting. If seeds aren't working:

1. Verify the table exists: `sqlite3 watchlist.db ".tables"`
2. Check if data is already there: `sqlite3 watchlist.db "SELECT COUNT(*) FROM titles"`
3. Clear the database and reseed: `python scripts/reset_db.py`

## Next Steps / Future Enhancements

- [ ] Add migration validation (syntax, dependencies)
- [ ] Add seed data versioning
- [ ] Add database backup before migrations
- [ ] Add environment-specific seeds (dev vs prod)
- [ ] Integrate with alembic for more advanced features
