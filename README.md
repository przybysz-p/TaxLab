# TaxLab

A small Python application for basic tax calculations, reporting and booking accountant consultations. Includes unit tests, SQLite integration tests, API contract tests and optional BDD scenarios. This is a simplified demo, not accounting, legal or tax advice.

## Modules

- `taxlab/calculator.py` — basic income, scale tax, lump-sum and VAT calculations.
- `taxlab/report.py` — tax reports and mockable dependencies.
- `taxlab/consultations.py` — consultation bookings using SQLite, transactions, uniqueness and retries.
- `taxlab/api.py` — FastAPI endpoints for a tax preview and consultation bookings.
- `tests/test_01*` ... `test_08*` — core unit tests.
- `tests/test_09_sqlite.py` and `tests/test_10_api.py` — real database and API tests with Polish in-code explanations.
- `tests/test_11_bdd.py`, `features/` — optional Gherkin scenarios.
- `cwiczenia/` — exercises with commented reference solutions.

## Quick start (Python 3.10+)

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -v
```

Optional BDD / property-based testing:

```powershell
python -m pip install -r requirements-optional.txt
python -m pytest -v
```

From project root: `python -m taxlab 120001`.

Run a local API for experimentation:

```powershell
python -m pip install uvicorn
python -m uvicorn taxlab.demo_api:app --reload
```

Open `http://127.0.0.1:8000/docs` for Swagger UI.
The API uses `X-User` solely as a teaching shortcut; it is **NOT authentication**. Never expose this service to the public internet.

For a Polish explanation of every test and commands, see [`TESTY_PRZEWODNIK_PL.md`](TESTY_PRZEWODNIK_PL.md).

## HTTP example

`POST /consultations` with JSON `{"accountant":"Anna","slot":"2030-05-14 10:00","request_key":"K1"}` and header `X-User: Jan`. Returns 201. A second customer for the same slot gets 409. Repeating the same request key returns the original booking (200). See `tests/test_10_api.py`.

## Limitations

- Simplified tax assumptions only: not suitable for real tax declarations.
- Bookings: fixed one-hour slots, interpreted in local time, no overlapping custom intervals.
- No actual login, payments, e-mail, personal information protection, or deployment hardening.
- All test data is synthetic. No credentials or real taxpayer data should be committed.
