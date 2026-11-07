# TaxLab — przewodnik po testach 01–11

Kod i repozytorium zawierają podstawowe obliczenia podatkowe, zapisy konsultacji w SQLite oraz API FastAPI. To uproszczony program demonstracyjny, nie system podatkowy do rzeczywistych rozliczeń. Każdy test dostaje osobne przygotowane środowisko.

## Gdzie co jest?

- `taxlab/` — kod aplikacji (nie zmieniamy przy zwykłym uruchamianiu testów).
- `tests/` — **wszystkie** testy od `test_01_...` do `test_11_bdd.py`.
- `tests/conftest.py` — wspólne fixture (`monthly_revenue_costs`, `db_path`, `client`).
- `features/consultations.feature` — czytelne, biznesowe scenariusze Gherkin.
- `cwiczenia/` — ćwiczenia A–C z pierwszej i drugiej części oraz **rozwiązania jako komentarze**.

## Co robią poszczególne testy?

| Plik | Mechanizm | Co sprawdzamy? |
|---|---|---|
| `test_01_first_test.py` | AAA | przychód minus koszty; podatek przy dokładnym progu |
| `test_02_boundaries.py` | parametryzacja | 0, 30000, 30001, 120000, 120001 i inne wartości graniczne |
| `test_03_negative.py` | `pytest.raises` | niepoprawne dane i oczekiwane wyjątki |
| `test_04_ryczalt.py` | reguły biznesowe | ryczałt i VAT — oczekiwane wyniki |
| `test_05_fixtures.py` | fixture | 12 miesięcy danych wejściowych |
| `test_06_mocks.py` | mock | brak prawdziwego e-maila i serwisu kursów walut |
| `test_07_monkeypatch.py` | monkeypatch | konfiguracja roku, data raportu |
| `test_08_properties.py` | Hypothesis | generowanie wielu wartości, testy własności — opcjonalne |
| `test_09_sqlite.py` | **integracja SQLite** | trwałość, UNIQUE, ROLLBACK, anulowanie, retry, współbieżność |
| `test_10_api.py` | **API + SQLite** | statusy HTTP, JSON, utworzenie/odczyt, uprawnienia, idempotencja |
| `test_11_bdd.py` | **BDD / Gherkin** | wykonywanie Given–When–Then przez API i SQLite — opcjonalne |

## Jak rozumieć najważniejsze linijki w `test_09_sqlite.py`?

- `book(db_path, 'Anna', 'Jan', SLOT)` — zapisujemy rezerwację bezpośrednio przez kod aplikacji.
- `get_booking(db_path, booking['id'])` — otwieramy nowe połączenie SQLite i szukamy zapisu: sprawdzamy trwałość.
- `with pytest.raises(SlotBusy)` — **oczekujemy** odmowy dla drugiej osoby. Takie odrzucenie daje **PASS**.
- `simulate_failure=True` — **celowo** wywołujemy awarię po INSERT i przed COMMIT. Potem sprawdzamy, czy `ROLLBACK` wycofał zmianę.
- `request_key` — identyfikator pojedynczej próby utworzenia wizyty. Retry z tym samym kluczem ma zwrócić to samo ID.
- `ThreadPoolExecutor(max_workers=2)` — dwóch klientów działa równocześnie. Oczekujemy **1 sukcesu i 1 konfliktu**, nie zakładamy kto wygra.
- `count_confirmed(...) == 1` — sprawdzamy stan **prawdziwej SQLite**, a nie tylko wynik funkcji.

## Jak rozumieć `test_10_api.py`?

1. `client.post(..., json=...)` — TestClient wysyła żądanie POST do FastAPI.
2. `response.status_code` — status HTTP: `201` utworzono, `200` OK, `401` brak identyfikacji, `403` brak uprawnień, `409` konflikt, `422` błędne dane.
3. `response.json()` — odpowiedź zawiera dane i szczegóły: `booking.id`, `status`, `detail`.
4. `client.get(...)` — sprawdzamy, czy rezerwacja jest odczytywalna po zapisaniu.
5. `client.delete(...)` — sprawdzamy anulowanie i możliwość zwolnienia terminu.

**Uwaga:** `X-User` jest uproszczeniem demonstracyjnym, a nie prawdziwym mechanizmem uwierzytelniania.

## BDD — co jest na czym oparte?

- **Given (Mając):** przygotowanie danych, np. Jan ma rezerwację.
- **When (Kiedy):** działanie, np. Ewa próbuje zająć termin przez API.
- **Then (Wtedy):** wynik, np. HTTP `409` i dokładnie jedna aktywna rezerwacja w SQLite.

`features/consultations.feature` zawiera scenariusze, a `tests/test_11_bdd.py` wiąże ich zdania z funkcjami Pythona. Biblioteka `pytest-bdd` jest opcjonalna.

## Komendy (PowerShell, z głównego katalogu TaxLab)

```powershell
python -m pip install -r requirements.txt
python -m pytest tests/test_09_sqlite.py -v
python -m pytest tests/test_10_api.py -v
python -m pytest -v
```

Dodatki BDD i Hypothesis:

```powershell
python -m pip install -r requirements-optional.txt
python -m pytest tests/test_11_bdd.py -v
```

Jeśli dwie biblioteki opcjonalne nie są zainstalowane, ich moduły mogą zgłosić **SKIPPED**, co nie jest błędem aplikacji.

## Zadania i rozwiązania

`cwiczenia/zadanie_A_SQLite.py`, `cwiczenia/zadanie_B_API.py`, `cwiczenia/zadanie_C_BDD.py` zawierają opisy, miejsce na pracę i zakomentowane rozwiązania. Żeby rozwiązanie stało się wykonywalnym testem, trzeba skopiować je do odpowiedniego `tests/test_09_...`, `test_10_...` lub `test_11_...` i usunąć komentarze. Rozwiązanie C wymaga też dodania scenariusza do pliku `.feature`.

**Nie interpretuj 100% PASS jako gwarancji poprawności całego systemu.** Testy pokazują to, co jawnie sprawdziliśmy; inne przepisy, przypadki bezpieczeństwa i interfejsy użytkownika nie są jeszcze objęte testami.
