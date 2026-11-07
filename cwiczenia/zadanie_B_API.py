"""ZADANIE B — API rezerwacji (FastAPI TestClient).

Napisz testy sprawdzające następujące odpowiedzi:
1. 201 Created — Jan utworzył rezerwację (sprawdź też JSON i odczyt GET).
2. 409 Conflict — Ewa próbuje zarezerwować zajętą godzinę.
3. 401 Unauthorized — zabrakło nagłówka X-User.
4. 403 Forbidden — Ewa chce anulować rezerwację Jana.

Co najmniej jeden test powinien sprawdzać DWA poziomy:
  (a) odpowiedź HTTP/JSON, (b) zapis w testowej bazie SQLite.
Wskazówka: wykorzystaj fixture client i db_path z tests/conftest.py.

Rozwiązania zakomentowane niżej. To wersja uproszczona odpowiednia
na pierwszą demonstrację; dokładniejsze wzory są w tests/test_10_api.py.
"""

# MIEJSCE NA TWOJE TESTY:
# def test_moje_api(client):
#     ...

# ================================================================
# ROZWIĄZANIA — odkomentuj i uruchom dopiero po własnej próbie
# ================================================================
# from taxlab.consultations import count_confirmed
#
# SLOT = "2030-05-14 10:00"
#
# def test_B1_poprawny_zapis(client, db_path):
#     # ARRANGE: nowa, pusta SQLite utworzona przez pytest.
#     # ACT: Jan przesyła JSON do POST /consultations.
#     res = client.post("/consultations",
#         json={"accountant": "Anna", "slot": SLOT},
#         headers={"X-User": "Jan"})
#     # ASSERT 1: HTTP i dane odpowiedzi.
#     assert res.status_code == 201
#     booking = res.json()["booking"]
#     assert booking["client"] == "Jan"
#     # ASSERT 2: stan rzeczywistej bazy (nie sam status 201).
#     assert count_confirmed(db_path, "Anna", SLOT) == 1
#     # ASSERT 3: GET odczytuje istniejący obiekt.
#     read = client.get(f"/consultations/{booking['id']}",
#         headers={"X-User": "Jan"})
#     assert read.status_code == 200
#
# def test_B2_termin_zajety(client):
#     body = {"accountant": "Anna", "slot": SLOT}
#     client.post("/consultations", json=body, headers={"X-User": "Jan"})
#     res = client.post("/consultations", json=body, headers={"X-User": "Ewa"})
#     assert res.status_code == 409
#     assert "detail" in res.json()  # JSON wyjaśnia problem.
#
# def test_B3_brak_X_User(client):
#     res = client.post("/consultations", json={"accountant": "Anna", "slot": SLOT})
#     assert res.status_code == 401
#
# def test_B4_zakaz_cudzego_anulowania(client):
#     body = {"accountant": "Anna", "slot": SLOT}
#     created = client.post("/consultations", json=body, headers={"X-User": "Jan"})
#     booking_id = created.json()["booking"]["id"]
#     res = client.delete(f"/consultations/{booking_id}", headers={"X-User": "Ewa"})
#     assert res.status_code == 403
#
# # PORÓWNANIE: 401 = brak identyfikacji; 403 = osoba znana, bez uprawnień.
# # UWAGA: nagłówek X-User to tylko DEMO, nie prawdziwe logowanie.
