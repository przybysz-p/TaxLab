"""ZADANIE A — SQLite: zapis, unikalność i wycofanie transakcji.

Wykonaj samodzielnie trzy testy. Korzystaj z funkcji w taxlab.consultations:
- book(path, accountant, client, slot, simulate_failure=False)
- get_booking(path, booking_id)
- count_confirmed(path, accountant, slot)

1) Rezerwacja Jana powinna istnieć po ponownym otwarciu bazy.
2) Jeśli Jan zajął termin, Ewa nie może zająć tego samego terminu.
3) Jeśli wystąpi awaria przed COMMIT, nie ma aktywnej rezerwacji.

Pomoc: fixture db_path jest w tests/conftest.py. Po napisaniu testy możesz
wkleić do tests/test_09_sqlite.py albo uruchomić ten plik jawnie z pytest.

ROZWIĄZANIA są poniżej jako komentarze. Nie trzeba instalować niczego więcej.
"""

# TUTAJ NAPISZ SWOJE TESTY:
# from taxlab.consultations import book, get_booking, count_confirmed, SlotBusy
# import pytest
#
# def test_moj_zapis(db_path):
#     ...

# ================================================================
# ROZWIĄZANIA — najpierw spróbuj samodzielnie!
# Aby uruchomić, skopiuj odkomentowany kod do tests/test_09_sqlite.py
# ================================================================
# import pytest
# from taxlab.consultations import (
#     book, get_booking, count_confirmed, SlotBusy,
# )
#
# SLOT = "2030-05-14 10:00"
#
# # 1. Trwałość zapisu: nowe połączenie znajdzie Jana.
# def test_A1_zapis_pozostaje_w_bazie(db_path):
#     # ARRANGE: baza jest pusta dzięki fixture db_path.
#     # ACT: zapis rezerwacji.
#     booking, _ = book(db_path, "Anna", "Jan", SLOT)
#     # ASSERT: get_booking() czyta rekord poprzez NOWE połączenie SQLite.
#     assert get_booking(db_path, booking["id"])["client"] == "Jan"
#
# # 2. UNIQUE: dwóch klientów nie zajmie tego samego terminu.
# def test_A2_nie_ma_podwojnej_rezerwacji(db_path):
#     book(db_path, "Anna", "Jan", SLOT)
#     # PASS, jeśli druga próba zgłosi wyjątek SlotBusy!
#     with pytest.raises(SlotBusy):
#         book(db_path, "Anna", "Ewa", SLOT)
#     assert count_confirmed(db_path, "Anna", SLOT) == 1
#
# # 3. ROLLBACK: awaria przed zatwierdzeniem = brak trwałego zapisu.
# def test_A3_awaria_wycofuje_zapis(db_path):
#     with pytest.raises(RuntimeError):
#         book(db_path, "Anna", "Jan", SLOT, simulate_failure=True)
#     assert count_confirmed(db_path, "Anna", SLOT) == 0
#
# # DO OMÓWIENIA:
# # W testach 2 i 3 wyjątki są OCZEKIWANE. Dlatego gdy wystąpią,
# # pytest pokazuje PASS, a nie FAIL.
