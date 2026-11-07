# Quick interactive demo — TaxLab

All commands run from the repository root. The database is created in a temporary directory during tests.

## 1. Original calculations

```powershell
python -m taxlab 120001
python -m pytest tests/test_02_boundaries.py -v
```

## 2. SQLite integration

```powershell
python -m pytest tests/integration/test_09_sqlite.py -v
```

- `test_booking_survives_new_connection`: check durability.
- `test_duplicate_slot_rejected_by_real_database`: UNIQUE.
- `test_transaction_rolls_back_if_exception_before_commit`: ROLLBACK.
- `test_parallel_bookings_only_one_wins`: concurrent requests.

## 3. API contracts

```powershell
python -m pytest tests/integration/test_10_api.py -v
```

The app checks creation (201), conflicts (409), demo identity (401), permissions (403), invalid input (422), duplicate requests (200), and persistence.

## 4. BDD / Gherkin (optional)

```powershell
python -m pip install -r requirements-optional.txt
python -m pytest tests/bdd -v
```

First read `features/consultations.feature`, then inspect `tests/bdd/test_consultations_bdd.py`. The steps call FastAPI TestClient and real SQLite.

## 5. Manual Swagger UI

```powershell
python -m pip install uvicorn
python -m uvicorn taxlab.demo_api:app --reload
```

Open http://127.0.0.1:8000/docs. For `POST /consultations` use `X-User: Jan` (demo-only header). Body:

```json
{"accountant": "Anna", "slot": "2030-05-14 10:00", "request_key": "request-1"}
```

Repeat with `X-User: Ewa` and a different request_key: expected `409 Conflict`.

**Safety:** `X-User` is not secure authentication. Do not deploy this demo to the public internet.
