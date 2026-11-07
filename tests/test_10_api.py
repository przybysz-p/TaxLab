"""10 — TESTY API: FastAPI TestClient + prawdziwa testowa baza SQLite.

Różnica względem test_09_sqlite.py:
- test_09 wywołuje bezpośrednio book() / cancel() (logika + SQLite);
- test_10 wysyła żądania HTTP przez TestClient i sprawdza status + JSON;
- aplikacja używa tej samej, izolowanej bazy testowej.

TestClient NIE wymaga uruchamiania uvicorn ani przeglądarki.
Nagłówek X-User jest WYŁĄCZNIE demonstracyjny, to nie logowanie!
Uruchom: python -m pytest tests/test_10_api.py -v
"""

# Jeden stały termin do testów; każda funkcja dostaje nową bazę przez fixture.
SLOT = "2030-05-14 10:00"


def reserve(client, user="Jan", key=None, slot=SLOT):
    """Pomocnicze wywołanie API — eliminuje powielanie tego samego POST."""
    return client.post(
        "/consultations",                  # adres (endpoint) tworzenia konsultacji
        json={                               # dane wysyłane do API
            "accountant": "Anna",
            "slot": slot,
            "request_key": key,
        },
        headers={"X-User": user},          # fikcyjna tożsamość w wersji demo
    )


def test_health(client):
    """Czy API odpowiada i zwraca oczekiwany JSON stanu?"""
    # ACT: wysyłamy GET, niczego nie zapisujemy.
    response = client.get("/health")
    # ASSERT: status 200 = OK, a JSON ma wymagane pole.
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_tax_preview_reuses_original_taxlab(client):
    """API używa istniejącego kalkulatora podatkowego z zajęć 7–8."""
    # ACT: przesyłamy roczną podstawę w parametrze zapytania GET.
    response = client.get("/tax/scale", params={"base": "120001"})
    # ASSERT: sprawdzamy kod i właściwą obliczoną wartość w JSON.
    assert response.status_code == 200
    assert response.json()["estimated_tax"] == "10800.32"


def test_api_create_and_read_actual_sqlite(client):
    """Pełny przepływ przez API: POST tworzy wizytę, GET ją odnajduje."""
    # ARRANGE: fixture client utworzyła osobną bazę SQLite.
    # ACT 1: Jan wysyła POST rezerwacji.
    response = reserve(client)
    # ASSERT 1: HTTP 201 oznacza utworzenie zasobu.
    assert response.status_code == 201

    # ACT 2: z JSON pobieramy identyfikator właśnie utworzonej wizyty.
    booking_id = response.json()["booking"]["id"]
    read = client.get(
        f"/consultations/{booking_id}", headers={"X-User": "Jan"}
    )
    # ASSERT 2: GET zwraca tę samą, zapisaną w SQLite rezerwację.
    assert read.status_code == 200
    assert read.json()["booking"]["status"] == "confirmed"
    assert read.json()["booking"]["client"] == "Jan"


def test_api_409_second_person_same_slot(client):
    """Zajęty termin → 409 Conflict, a nie ponowne potwierdzenie."""
    # ARRANGE: Jan zajmuje termin Anny.
    assert reserve(client, "Jan").status_code == 201
    # ACT: Ewa próbuje zająć tę samą godzinę.
    response = reserve(client, "Ewa")
    # ASSERT: kod 409 i zrozumiały szczegół w JSON.
    assert response.status_code == 409
    assert "zajety" in response.json()["detail"]
    # UWAGA: to test NEGATYWNY, ale poprawna odmowa oznacza PASS.


def test_api_401_no_header(client):
    """Brak identyfikacji klienta → HTTP 401."""
    # ACT: wysyłamy POST bez demonstracyjnego nagłówka X-User.
    response = client.post(
        "/consultations", json={"accountant": "Anna", "slot": SLOT}
    )
    # ASSERT: API powinno odmówić obsługi żądania.
    assert response.status_code == 401


def test_api_403_other_user_cannot_cancel(client):
    """Użytkownik rozpoznany, ale bez uprawnień → HTTP 403."""
    # ARRANGE: wizyta należy do Jana.
    booking_id = reserve(client, "Jan").json()["booking"]["id"]
    # ACT: Ewa próbuje ją anulować.
    response = client.delete(
        f"/consultations/{booking_id}", headers={"X-User": "Ewa"}
    )
    # ASSERT: Ewa nie ma uprawnienia; serwer odpowiada 403.
    assert response.status_code == 403
    # Nie mylić z 401: tu X-User jest podany, ale właściciel się nie zgadza.


def test_api_404_unknown_booking(client):
    """GET dla nieistniejącej konsultacji → HTTP 404 Not Found."""
    response = client.get("/consultations/999", headers={"X-User": "Jan"})
    assert response.status_code == 404


def test_api_422_invalid_slot(client):
    """Niepoprawny format godziny → HTTP 422 (walidacja danych)."""
    # ACT: zamiast daty i godziny wysyłamy 'tomorrow'.
    response = reserve(client, slot="tomorrow")
    # ASSERT: API odrzuca dane bez zapisania wizyty.
    assert response.status_code == 422


def test_api_idempotency_retry_returns_same_id(client):
    """Powtórzony POST z tym samym request_key zwraca pierwotny obiekt."""
    # ARRANGE: przyjmujemy, że odpowiedź na pierwszy POST mogła zginąć.
    # ACT: Jan ponawia dokładnie to samo żądanie z kluczem 'k1'.
    first = reserve(client, key="k1")
    second = reserve(client, key="k1")

    # ASSERT: 201 = utworzono, 200 = zwrócono istniejącą rezerwację.
    assert first.status_code == 201
    assert second.status_code == 200
    assert first.json()["booking"]["id"] == second.json()["booking"]["id"]
    assert second.json()["replayed"] is True


def test_api_cancel_and_book_again(client):
    """Po DELETE Jan zwalnia termin; następny POST Ewy może go zająć."""
    # ARRANGE: Jan tworzy wizytę.
    first = reserve(client, "Jan")
    booking_id = first.json()["booking"]["id"]

    # ACT 1: Jan anuluje własną konsultację przez DELETE.
    cancellation = client.delete(
        f"/consultations/{booking_id}", headers={"X-User": "Jan"}
    )
    # ASSERT 1: anulowanie zakończyło się sukcesem.
    assert cancellation.status_code == 200
    assert cancellation.json()["booking"]["status"] == "cancelled"

    # ACT 2: Ewa rezerwuje tę samą godzinę.
    # ASSERT 2: jest ponownie dostępna, więc API zwraca 201.
    assert reserve(client, "Ewa").status_code == 201
