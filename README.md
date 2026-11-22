# TaxLab

A small Python application for basic tax calculations, reporting and booking accountant consultations. Includes unit tests, SQLite integration tests, API contract tests and optional BDD scenarios. This is a simplified demo, not accounting, legal or tax advice.

## Modules

- `taxlab/calculator.py` — basic income, scale tax, lump-sum and VAT calculations.
- `taxlab/report.py` — tax reports and mockable dependencies.
- `taxlab/consultations.py` — consultation bookings using SQLite, transactions, uniqueness and retries.
- `taxlab/api.py` — FastAPI endpoints for a tax preview and consultation bookings.
- `taxlab/ui_demo.py` — optional local demonstration UI used by Playwright.
- `tests/test_01*` ... `test_08*` — core unit tests.
- `tests/test_09_sqlite.py` and `tests/test_10_api.py` — real database and API tests with Polish in-code explanations.
- `tests/test_11_bdd.py`, `features/` — optional Gherkin scenarios.
- `cwiczenia/` — exercises with commented reference solutions (including UI and nonfunctional quality).

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


## Optional web UI and browser tests (exercises 11–12)

The original TaxLab provides a FastAPI service and Swagger UI, **not an end-user booking form**.
The optional module `taxlab/ui_demo.py` adds a local HTML page at `/` for
**PIT preview and consultation booking**. It reuses `taxlab.api.create_app`,
`taxlab.calculator` and the same SQLite booking logic — no duplicate business rules.

Install the standard dependencies and the browser testing tools from the **project root**:

```powershell
py -m pip install -r requirements.txt
py -m pip install uvicorn pytest-playwright
py -m playwright install chromium
```

Start the interactive page manually:

```powershell
py -m uvicorn taxlab.ui_demo:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/` for the demo and `http://127.0.0.1:8000/docs`
for the API. The demo uses `local_consultations.sqlite3` unless `TAXLAB_DB` is set.

Run the three optional UI/E2E tests with a visible Chromium browser:

```powershell
py -m pytest tests/test_12_ui_playwright.py -v --headed
```

You can omit `--headed` to run headlessly. `test_12_ui_playwright.py` starts
its own Uvicorn process on an available local port and gives **each test a fresh
SQLite database** through `tmp_path`; it does not modify the manual demo's DB.
If pytest reports `SKIPPED`, check whether `pytest-playwright` is installed.
To diagnose failed browser tests:

```powershell
py -m pytest tests/test_12_ui_playwright.py -v --tracing retain-on-failure --screenshot only-on-failure --video retain-on-failure
```

See `cwiczenia/cwiczenie_ui.py` (E2E review and booking conflict) and
`cwiczenia/cwiczenie_niefunkcjonalne.py` (GO/NO-GO and soak/performance analysis).
Both contain commented reference answers; the UI exercise code should be added
to `tests/test_12_ui_playwright.py` to reuse the `ui_url` fixture.

For an **optional, local load test**, install Locust with `py -m pip install locust`
and copy the commented `TaxLabUser` example from the nonfunctional exercise into
`locustfile.py`. Run Locust only against your own local service.

**CI note:** the existing GitHub Actions workflow installs only the core/BDD
requirements and therefore does **not** install Chromium / exercise Playwright
UI tests. A green existing CI run does not prove UI/E2E tests passed. To include
browser tests in CI, add both `pytest-playwright` and browser installation
there, then explicitly run the UI tests.

**Security:** `X-User` is a user-provided teaching header, not authentication.
The local HTML demo is not intended for public deployment or real client data.

## Limitations

- Simplified tax assumptions only: not suitable for real tax declarations.
- Bookings: fixed one-hour slots, interpreted in local time, no overlapping custom intervals.
- No actual login, payments, e-mail, personal information protection, or deployment hardening.
- All test data is synthetic. No credentials or real taxpayer data should be committed.
