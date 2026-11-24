"""Sprawdzenie INTEGRALNOŚCI SQLite po Locust (nie modyfikuje bazy).

PowerShell:
    py cwiczenia/raport_sqlite_locust.py locust_database.sqlite3

Uruchom po zakończeniu serwera i testu. Suma HTTP 201 powinna zgadzać się
z liczbą dodanych potwierdzonych wizyt w bazie testowej (gdy była świeża).
"""
import sqlite3
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Użycie: py cwiczenia/raport_sqlite_locust.py PLIK_BAZY.sqlite3")
    path = Path(sys.argv[1])
    if not path.is_file():
        raise SystemExit(f"Nie znaleziono bazy: {path}")
    with sqlite3.connect(f"file:{path.resolve().as_posix()}?mode=ro", uri=True) as db:
        total = db.execute("SELECT COUNT(*) FROM consultations").fetchone()[0]
        confirmed = db.execute(
            "SELECT COUNT(*) FROM consultations WHERE status='confirmed'"
        ).fetchone()[0]
        duplicates = db.execute("""
            SELECT accountant, slot, COUNT(*) AS n
            FROM consultations WHERE status='confirmed'
            GROUP BY accountant, slot HAVING COUNT(*) > 1
        """).fetchall()
        customers = db.execute(
            "SELECT COUNT(DISTINCT accountant) FROM consultations"
        ).fetchone()[0]
        print(f"Baza: {path}")
        print(f"Wszystkie wpisy: {total}")
        print(f"Potwierdzone: {confirmed}")
        print(f"Liczba księgowych: {customers}")
        print(f"Aktywne podwójne rezerwacje: {len(duplicates)}")
        if duplicates:
            for row in duplicates[:10]:
                print("  BŁĄD:", row)
            raise SystemExit("Naruszona integralność aktywnych rezerwacji!")
        print("OK: brak podwójnych aktywnych rezerwacji (zgodnie z UNIQUE).")


if __name__ == "__main__":
    main()
