# Backend Refactoring Guide: Separation of Concerns

## Overview

This document describes the refactoring of the watchlist application backend to introduce proper separation of concerns. The refactoring maintains 100% API compatibility while organizing code into distinct layers with clear responsibilities.

## Architecture

The backend is now organized into four distinct layers:

### 1. **API Layer** (`main.py`)
- **Responsibility**: HTTP request/response handling and routing
- **Contains**: FastAPI route handlers
- **Key Features**:
  - Receives HTTP requests
  - Validates input using Pydantic models (DTOs)
  - Calls service layer methods
  - Returns typed responses using Pydantic models
  - Handles HTTP-level error responses (HTTPException)

**Example**:
```python
@app.post("/api/watchlist", response_model=SuccessResponse)
def add_to_watchlist(body: AddToWatchlistRequest):
    """Route handler orchestrates: validate → call service → return response"""
    try:
        WatchlistService.add_to_watchlist(body.title_id)
        return SuccessResponse(ok=True)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### 2. **Service Layer** (`services/`)
- **Responsibility**: Business logic and domain rules
- **Contains**: `WatchlistService`, `TitleService`
- **Key Features**:
  - Orchestrates repository operations
  - Validates business rules (e.g., title exists before adding)
  - Transforms repository data into response DTOs
  - May use pagination, filtering, or other business rules

**Example**:
```python
@staticmethod
def add_to_watchlist(title_id: int) -> None:
    """Add a title to watchlist after validating it exists"""
    # Validate business rule
    title = TitleRepository.get_title_by_id(title_id)
    if not title:
        raise ValueError(f"Title with ID {title_id} not found")
    
    # Call repository
    WatchlistRepository.add_title_to_watchlist(title_id)
```

### 3. **Repository Layer** (`repositories/`)
- **Responsibility**: Data access and SQL execution
- **Contains**: `TitleRepository`, `WatchlistRepository`
- **Key Features**:
  - **All SQL queries are here** - no SQL in routes or services
  - Connection management and cleanup
  - Transaction handling
  - Single responsibility per repository class

**Example**:
```python
@staticmethod
def get_watchlist_page(page: int, size: int) -> tuple[list[dict], int]:
    """Retrieve paginated watchlist with total count"""
    conn = get_conn()
    try:
        offset = (page - 1) * size
        rows = conn.execute(
            """SELECT w.id as watchlist_id, ... FROM watchlist w ...""",
            (size, offset),
        ).fetchall()
        total = conn.execute("SELECT COUNT(*) FROM watchlist").fetchone()[0]
        items = [dict(r) for r in rows]
        return items, total
    finally:
        conn.close()
```

### 4. **DTO/Schema Layer** (`models/schemas.py`)
- **Responsibility**: Type-safe request/response contracts
- **Contains**: Pydantic models for all API input/output
- **Key Features**:
  - Request models: `AddToWatchlistRequest`, `MarkWatchedRequest`
  - Response models: `WatchlistItemResponse`, `WatchlistPageResponse`, etc.
  - Consistent field naming (snake_case)
  - Type hints for IDE support and validation

**Example**:
```python
class WatchlistItemResponse(BaseModel):
    """Response model for a single watchlist item"""
    watchlist_id: int
    title_id: int
    title: str
    kind: str
    release_year: int
    genre: str
    is_watched: bool
    added_at: str
    watched_at: Optional[str] = None
```

## Directory Structure

```
backend/
├── main.py                          # API layer (route handlers)
├── db.py                            # Database connection management
├── seed_data.py                     # Seed data (unchanged)
├── models/
│   ├── __init__.py
│   └── schemas.py                   # DTOs for requests/responses
├── repositories/
│   ├── __init__.py
│   ├── title_repository.py          # Title data access
│   └── watchlist_repository.py      # Watchlist data access
└── services/
    ├── __init__.py
    ├── title_service.py             # Title business logic
    └── watchlist_service.py         # Watchlist business logic
```

## API Endpoints (Unchanged)

All endpoints maintain the same interface:

### Catalog
```
GET /api/catalog
Response: List[TitleResponse]
```

### Watchlist
```
GET /api/watchlist?page=1&size=5
Response: WatchlistPageResponse

POST /api/watchlist
Request: AddToWatchlistRequest
Response: SuccessResponse

PATCH /api/watchlist/{watchlist_id}
Request: MarkWatchedRequest
Response: SuccessResponse

GET /api/watchlist/recent
Response: List[WatchlistItemResponse]
```

## Migration Path for Developers

### Adding a New Feature

**Old Way** (before refactoring):
```python
# ❌ SQL logic mixed in route handler
@app.get("/api/new-feature")
def new_feature():
    conn = get_conn()
    rows = conn.execute("SELECT ... WHERE ...").fetchall()
    conn.close()
    return [dict(r) for r in rows]
```

**New Way** (after refactoring):

**Step 1: Create the DTO** (`models/schemas.py`)
```python
class NewFeatureResponse(BaseModel):
    id: int
    name: str
    # ... other fields
```

**Step 2: Create the repository method** (`repositories/xxx_repository.py`)
```python
@staticmethod
def get_feature_data() -> list[dict]:
    conn = get_conn()
    try:
        rows = conn.execute("SELECT ... WHERE ...").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
```

**Step 3: Create the service method** (`services/xxx_service.py`)
```python
@staticmethod
def get_features() -> list[NewFeatureResponse]:
    items = Repository.get_feature_data()
    return [
        NewFeatureResponse(id=item["id"], name=item["name"], ...)
        for item in items
    ]
```

**Step 4: Add the route** (`main.py`)
```python
@app.get("/api/new-feature", response_model=list[NewFeatureResponse])
def new_feature():
    return Service.get_features()
```

### Key Principles

1. **API Layer**: Only orchestrates - no business logic, no SQL
2. **Service Layer**: Business rules and validation - no SQL execution
3. **Repository Layer**: All SQL queries and data access
4. **DTO Layer**: Clear contracts between layers

### Testing the Layers

Each layer can be tested independently:

```python
# Test repository (unit test with mock DB)
def test_repository():
    items, total = WatchlistRepository.get_watchlist_page(1, 5)
    assert len(items) <= 5

# Test service (unit test with mock repository)
def test_service():
    response = WatchlistService.get_watchlist_page(1, 5)
    assert response.page == 1

# Test API (integration test)
def test_api():
    response = client.get("/api/watchlist")
    assert response.status_code == 200
```

## Error Handling

**Repository Layer**: Raises `sqlite3` exceptions (e.g., `IntegrityError`)
**Service Layer**: Raises `ValueError` for business rule violations
**API Layer**: Catches exceptions and returns HTTP responses

Example:
```python
# Repository throws IntegrityError if duplicate
WatchlistRepository.add_title_to_watchlist(15)

# Service validates before calling repository
def add_to_watchlist(title_id: int):
    title = TitleRepository.get_title_by_id(title_id)
    if not title:
        raise ValueError(f"Title not found")  # ← Service validation
    WatchlistRepository.add_title_to_watchlist(title_id)

# API converts to HTTP response
@app.post("/api/watchlist")
def add_to_watchlist(body: AddToWatchlistRequest):
    try:
        WatchlistService.add_to_watchlist(body.title_id)
        return SuccessResponse(ok=True)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## Benefits of This Architecture

| Benefit | Description |
|---------|------------|
| **Testability** | Each layer can be tested independently with mocks |
| **Maintainability** | Changes to SQL only affect repositories |
| **Reusability** | Services can be called from different interfaces (e.g., REST, GraphQL, CLI) |
| **Scalability** | Easy to add new repositories or services |
| **Type Safety** | DTOs provide clear contracts and IDE support |
| **Separation of Concerns** | Each layer has one job |

## Backward Compatibility

This refactoring is **100% backward compatible**:
- All API endpoints return the same data structures
- HTTP status codes are identical
- Error messages are similar
- Client code requires no changes

## Notes

- The `db.py` module remains unchanged except for imports - it still manages database connections and initialization
- `seed_data.py` is completely unchanged
- The migration and seeding system (in `migrate.py` and `seed.py`) is unaffected
- All business logic is now centralized in the service layer
- Repository methods are stateless and reusable

## Future Improvements

Potential enhancements enabled by this architecture:

1. **Caching Layer**: Add between service and repository
2. **Database Abstraction**: Swap SQLite for PostgreSQL by changing repositories
3. **Async Support**: Convert to async/await in service and repository layers
4. **Advanced Validation**: Add Pydantic validators in DTOs
5. **API Versioning**: Create v2 endpoints that use same services with different DTOs
6. **Dependency Injection**: Use FastAPI's `Depends()` for service injection
