"""ZARZĄDZANIE JAKOŚCIĄ — ĆWICZENIE 11: UI / E2E w TaxLab.

Przed rozpoczęciem (z katalogu głównego TaxLab):
    py -m pip install -r requirements.txt
    py -m pip install uvicorn pytest-playwright
    py -m playwright install chromium
    py -m pytest tests/test_12_ui_playwright.py -v --headed

Aplikacja: taxlab/ui_demo.py (formularz -> FastAPI -> SQLite).
Testy przeglądarkowe: tests/test_12_ui_playwright.py.

ĆWICZENIE A — PRZEGLĄD KODU (10–15 min)
Wskaż 4 problemy, a następnie napisz bezpieczniejszy test rezerwacji.

Przykład celowo błędny — NIE uruchamiaj jako poprawnego testu:

    page.goto(ui_url)
    page.locator('button').nth(3).click()
    time.sleep(10)
    # brak sprawdzenia wyniku
    # wszystkie testy mają jedną, współdzieloną bazę

Wskazówki:
- Na ekranie demo są dwa przyciski, więc indeks nth(3) nie wskazuje żadnego.
- Zastanów się, dlaczego selektor pozycyjny pozostanie kruchy nawet po zmianie indeksu.
- Czego powinien oczekiwać test po kliknięciu?
- Jak fixture ui_url i tmp_path zapewniają czystą bazę?

ĆWICZENIE B — KONFLIKT REZERWACJI (10–15 min)
GIVEN: Anna ma wolny termin 2030-05-14 10:00.
WHEN: Jan rezerwuje ten termin, a potem Ewa próbuje go zarezerwować.
THEN: UI pokazuje informację HTTP 409, a w SQLite pozostaje jedna aktywna
      rezerwacja na ten termin, należąca do Jana.

Dopisz nowy test w tests/test_12_ui_playwright.py. Nie edytuj logiki book().

WAŻNE: rozwiązania poniżej są zakomentowane. Aby je uruchomić, skopiuj
odkomentowany kod do tests/test_12_ui_playwright.py (tam jest fixture ui_url).
Obie funkcje wymagają importów Page/expect i dostępu do Playwright/Chromium.
"""

# ============================================================================
# PRZYKŁADOWE ROZWIĄZANIE A — DODAJ DO tests/test_12_ui_playwright.py
# ============================================================================
# def test_cwiczenie_A_stabilna_rezerwacja(page: Page, ui_url):
#     # ARRANGE — osobna baza i lokalny serwer są tworzone przez fixture ui_url.
#     page.goto(ui_url)
#     page.get_by_label("Klient").fill("Jan")
#     page.get_by_label("Księgowa").fill("Anna")
#     page.get_by_label("Termin (YYYY-MM-DD HH:00)").fill("2030-05-14 10:00")
#
#     # ACT — lokator semantyczny, brak time.sleep().
#     page.get_by_role("button", name="Zarezerwuj").click()
#
#     # ASSERT — czekamy na oczekiwany wynik działania API i UI.
#     expect(
#         page.get_by_role("status", name="Wynik rezerwacji")
#     ).to_contain_text("Potwierdzono")
#
# 4 WNIOSKI:
# (1) nth(3) zależy od pozycji elementu i w naszym demo nie istnieje.
# (2) time.sleep(10) czeka na czas, nie na odpowiedź API; jest wolny i zawodny.
# (3) Test bez expect/assert nie potwierdza wyniku rezerwacji.
# (4) Wspólna SQLite powoduje zależność od kolejności; ui_url używa tmp_path.

# ============================================================================
# PRZYKŁADOWE ROZWIĄZANIE B — DODAJ DO tests/test_12_ui_playwright.py
# ============================================================================
# Na górze pliku testowego dopisz import:
# from taxlab.consultations import count_confirmed, get_booking
#
# def test_cwiczenie_B_jan_ewa_konflikt(page: Page, ui_url, tmp_path):
#     SLOT = "2030-05-14 10:00"
#     page.goto(ui_url)
#
#     # GIVEN / WHEN — Jan rezerwuje dostępny termin.
#     page.get_by_label("Klient").fill("Jan")
#     page.get_by_label("Księgowa").fill("Anna")
#     page.get_by_label("Termin (YYYY-MM-DD HH:00)").fill(SLOT)
#     page.get_by_role("button", name="Zarezerwuj").click()
#     expect(
#         page.get_by_role("status", name="Wynik rezerwacji")
#     ).to_contain_text("Potwierdzono")
#
#     # WHEN — Ewa próbuje ZAJĘTEGO terminu Anny.
#     page.get_by_label("Klient").fill("Ewa")
#     page.get_by_role("button", name="Zarezerwuj").click()
#
#     # THEN — widoczny komunikat o konflikcie z API.
#     expect(
#         page.get_by_role("status", name="Wynik rezerwacji")
#     ).to_contain_text("HTTP 409")
#
#     # THEN — testujemy też trwały stan SQLite, a nie sam napis na ekranie.
#     # pytest przekazuje ten sam tmp_path testowi i fixture ui_url.
#     db_path = tmp_path / "ui_e2e.sqlite3"
#     assert count_confirmed(db_path, "Anna", SLOT) == 1
#
#     # Uwaga: X-User w TaxLab jest demonstracyjnym nagłówkiem, nie logowaniem.

# Polecenie po dodaniu testów:
# py -m pytest tests/test_12_ui_playwright.py -v --headed
