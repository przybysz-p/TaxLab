"""OPCJONALNA, KONTROLOWANA awaria: blokada zapisu SQLite na 20 sekund.

Nie używaj do prawdziwych baz ani danych użytkowników!
Uruchamiaj wyłącznie podczas testu Locust na dedykowanym pliku .sqlite3.

PowerShell, w TRZECIM terminalu, gdy Locust już działa:
    py cwiczenia/demonstracja_blokady_sqlite.py locust_database.sqlite3 20

TaxLab ustawia busy_timeout=15000 ms (15 s), więc część zapisów może
skończyć się nieobsłużonym sqlite3.OperationalError -> HTTP 500.
To celowo wstrzyknięta awaria, NIE wynik normalnego testu wydajności.
"""
import sqlite3
import sys
import time
from pathlib import Path


def main():
    if len(sys.argv) not in (2, 3):
        raise SystemExit("Użycie: py cwiczenia/demonstracja_blokady_sqlite.py baza.sqlite3 [sekundy]")
    database = Path(sys.argv[1])
    if not database.is_file():
        raise SystemExit("Baza nie istnieje. Najpierw uruchom serwer TaxLab z TAXLAB_DB.")
    seconds = float(sys.argv[2]) if len(sys.argv) == 3 else 20.0
    if not 1 <= seconds <= 30:
        raise SystemExit("W demonstracji dopuszczalny zakres blokady to 1–30 sekund.")
    connection = sqlite3.connect(str(database), timeout=5)
    try:
        print(f"Blokuję zapisy do {database} przez {seconds:.0f} sekund.")
        connection.execute("BEGIN IMMEDIATE")
        time.sleep(seconds)
        connection.rollback()
        print("Zwolniono blokadę. Sprawdź FAIL i powrót p95 w Locust.")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
