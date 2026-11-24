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
- `cwiczenia/test_13_locust_sqlite.py` — Locust profiles for concurrent SQLite bookings.
- `cwiczenia/demonstracja_blokady_sqlite.py` and `cwiczenia/raport_sqlite_locust.py` — simulated locking and data-integrity report.

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

For optional load testing, see the complete Locust/SQLite exercise below.

**CI note:** the existing GitHub Actions workflow installs only the core/BDD
requirements and therefore does **not** install Chromium / exercise Playwright
UI tests. A green existing CI run does not prove UI/E2E tests passed. To include
browser tests in CI, add both `pytest-playwright` and browser installation
there, then explicitly run the UI tests.

**Security:** `X-User` is a user-provided teaching header, not authentication.
The local HTML demo is not intended for public deployment or real client data.

## Locust + SQLite: obciążenie zapisów do bazy (ćwiczenie 13)

Ćwiczenie dotyczy **rzeczywistego endpointu** `POST /consultations` w TaxLab. W odróżnieniu
od szybkiego `GET /tax/scale` każde żądanie rezerwacji wykonuje transakcję SQLite.
Uruchamiaj wszystko **tylko lokalnie**, na danych testowych i na osobnym pliku bazy.
Nie testuj publicznych usług ani cudzych serwerów bez pozwolenia.

### Pliki

- `cwiczenia/test_13_locust_sqlite.py` — profile `ramp`/`spike` i tryby `unique`/`conflict`;
  **to plik uruchamiany przez Locust, a nie przez `pytest`**.
- `cwiczenia/raport_sqlite_locust.py` — tylko odczytuje SQLite i sprawdza brak
  dwóch potwierdzonych rezerwacji tej samej księgowej na ten sam termin.
- `cwiczenia/demonstracja_blokady_sqlite.py` — opcjonalnie przetrzymuje blokadę
  transakcji przez 1–30 sekund. Celowo prowokuje problem; nie wykonuj na ważnych danych.

### Przygotowanie — dwa terminale PowerShell

W katalogu głównym TaxLab zainstaluj Locust (zakładamy działające API/UI):

```powershell
py -m pip install locust uvicorn
New-Item -ItemType Directory -Force locust_results | Out-Null
```

W **terminalu 1** uruchom serwer, wybierając osobną bazę. NIE dodawaj `--reload`:

```powershell
$env:TAXLAB_DB = "locust_database.sqlite3"
py -m uvicorn taxlab.ui_demo:app --host 127.0.0.1 --port 8000
```

W **terminalu 2** wybierz profil, uruchom Locust i śledź dashboard:

- Dashboard: `http://127.0.0.1:8089` → **Charts**, **Statistics**, **Failures**.
- `ramp`: 20 użytkowników na starcie, +50/min, do 500 pod koniec 10 minut.
- `spike`: 100 użytkowników, w minucie 3.–4. skok do 1000, następnie powrót do 100.
- `unique`: każdy klient rezerwuje **inny termin** (oczekiwany HTTP **201**).
- `conflict`: wielu klientów próbuje zarezerwować **ten sam termin** (pierwszy HTTP **201**, kolejne HTTP **409**).

**Test A: zapis różnych terminów, ramp 10 minut:**

```powershell
$env:TAXLAB_DB_CASE = "unique"
$env:TAXLAB_LOCUST_SCENARIO = "ramp"
py -m locust -f cwiczenia/test_13_locust_sqlite.py `
  --host http://127.0.0.1:8000 `
  --autostart `
  --web-host 127.0.0.1 `
  --csv locust_results/db_unique_ramp `
  --html locust_results/db_unique_ramp.html
```

**Test B: konflikt jednego terminu, spike 10 minut:**

```powershell
$env:TAXLAB_DB_CASE = "conflict"
$env:TAXLAB_LOCUST_SCENARIO = "spike"
py -m locust -f cwiczenia/test_13_locust_sqlite.py `
  --host http://127.0.0.1:8000 `
  --autostart `
  --web-host 127.0.0.1 `
  --csv locust_results/db_conflict_spike `
  --html locust_results/db_conflict_spike.html
```

**Ważne:** każdy eksperyment uruchom na **świeżej bazie** (zatrzymaj serwer
`Ctrl+C`, zmień `TAXLAB_DB` na np. `locust_spike.sqlite3` i uruchom serwer ponownie).
W przeciwnym razie w tabeli będą rekordy z poprzedniego testu i porównanie będzie mylące.
Otrzymane CSV i HTML trafiają do `locust_results/`, który jest ignorowany przez Git.

### Kontrola integralności bazy

Po zakończeniu testu zatrzymaj Locust i serwer. Dla bazy użytej w danym teście:

```powershell
py cwiczenia/raport_sqlite_locust.py locust_database.sqlite3
```

Oczekiwane: **zero podwójnych aktywnych rezerwacji**. W trybie `unique` liczba
NOWYCH potwierdzonych rezerwacji powinna odpowiadać liczbie udanych HTTP 201
(przy świeżej bazie). W trybie `conflict` tylko pierwsze żądanie może dać 201,
pozostałe poprawnie zwracają 409. **HTTP 409 to oczekiwany wynik biznesowy,
nie awaria serwera** — skrypt Locust odpowiednio go oznacza.

### Opcjonalne ćwiczenie: kontrolowana blokada bazy

**Wyłącznie** w osobnej bazie testowej: podczas testu `unique` uruchom w
**terminalu 3** (ten sam plik bazy co serwer!):

```powershell
py cwiczenia/demonstracja_blokady_sqlite.py locust_database.sqlite3 20
```

TaxLab ma ustawiony `busy_timeout` SQLite na 15 sekund, zatem dłuższa blokada
może spowodować wzrost p95, timeouty i HTTP 500. To **celowa symulacja awarii**,
nie pomiar normalnej wydajności aplikacji. Nie ma gwarancji uzyskania dokładnie
jednego rodzaju błędu — zależy to od czasu napływu żądań i obciążenia systemu.

### Co opisać w sprawozdaniu?

1. Dla jakiego profilu i ilu użytkowników p95 zaczyna wyraźnie rosnąć?
2. Jak zmieniają się throughput (RPS) i odsetek rzeczywistych błędów?
3. Czy po minutowym spike system wraca do zachowania z początku testu?
4. Czy SQLite zachowała integralność (wynik `raport_sqlite_locust.py`)?
5. Dlaczego HTTP 409 jest **sukcesem reguły rezerwacji** w trybie konfliktu,
   ale HTTP 500 i nieoczekiwane 409 w trybie `unique` są niepowodzeniami?

Otrzymane wyniki zależą od sprzętu, wydajności lokalnego serwera, wersji bibliotek
i współdzielenia komputera przez Locust i Uvicorn. Nie są uniwersalnym benchmarkiem SQLite.

## Limitations

- Simplified tax assumptions only: not suitable for real tax declarations.
- Bookings: fixed one-hour slots, interpreted in local time, no overlapping custom intervals.
- No actual login, payments, e-mail, personal information protection, or deployment hardening.
- All test data is synthetic. No credentials or real taxpayer data should be committed.
