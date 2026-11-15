"""ZADANIA D, E i F — Gherkin + pytest-bdd + prawdziwe API.

Wymaganie biznesowe:
"Jan ma potwierdzoną rezerwację konsultacji. Jan ją anuluje.
Następnie Ewa może zarezerwować ten sam termin u księgowej Anny."

ZADANIE:
1. Dopisz scenariusz do features/consultations.feature.
2. Dopisz kroki Given / When / Then do tests/test_11_bdd.py.
3. Sprawdź kod HTTP ORAZ stan w SQLite — nie powielaj logiki book() w Then.
4. Uruchom: python -m pytest tests/test_11_bdd.py -v

Wzorcowy scenariusz i kroki podane poniżej są KOMENTARZAMI.
Przepisz / odkomentuj je we wskazanych plikach, aby działały.
"""

# ================================================================
# ROZWIĄZANIE CZĘŚĆ 1 — wstaw do features/consultations.feature
# (usuń znaki # po skopiowaniu; w pliku .feature użyj wcięcia)
# ================================================================
# Scenario: Cancelling a booking frees the consultation slot
#   Given Jan has booked Anna on 2030-05-14 at 10:00
#   When Jan cancels his booking
#   Then Ewa can book the released slot
#
# W PRZYKŁADZIE celowo mamy kroki po angielsku (standard Gherkin),
# ale do prezentacji możesz dopisać polskie tłumaczenie:
# Given = Mając, When = Kiedy, Then = Wtedy.

# ================================================================
# ROZWIĄZANIE CZĘŚĆ 2 — dopisz kroki do tests/test_11_bdd.py
# W tym pliku są już: @when, @then, context, SLOT, count_confirmed.
# ================================================================
#
# @when("Jan cancels his booking")
# def jan_cancels(context):
#     # ARRANGE: istniejąca rezerwacja pochodzi z kroku Given.
#     # ACT 1: pobierz ID rezerwacji z API.
#     # UWAGA: nie mamy endpointu listy wizyt; dla tego scenariusza
#     # rozszerz krok Given (already_booked), by zapisać ID w context.
#     booking_id = context["jan_booking_id"]
#     # ACT 2: Jan wysyła DELETE i zwalnia swój termin.
#     context["cancel_response"] = context["client"].delete(
#         f"/consultations/{booking_id}", headers={"X-User": "Jan"})
#
# @then("Ewa can book the released slot")
# def ewa_books_released_slot(context):
#     # ASSERT: najpierw potwierdź, że anulowanie się udało.
#     assert context["cancel_response"].status_code == 200
#     # ACT: Ewa ponownie próbuje zarezerwować 10:00 przez HTTP.
#     response = context["client"].post(
#         "/consultations",
#         json={"accountant": "Anna", "slot": SLOT},
#         headers={"X-User": "Ewa"})
#     # ASSERT: API zwraca 201, a baza ma jedną AKTYWNĄ rezerwację.
#     assert response.status_code == 201
#     assert response.json()["booking"]["client"] == "Ewa"
#     assert count_confirmed(context["db"], "Anna", SLOT) == 1
#
# ================================================================
# DODATKOWA ZMIANA w istniejącym kroku GIVEN (already_booked):
# po assert response.status_code == 201 dopisz:
#     context["jan_booking_id"] = response.json()["booking"]["id"]
# To świadomie pokazuje, jak kroki BDD współdzielą dane przez context.
# ================================================================

# ZADANIE E
'''
Ćwiczenie E — BDD podatku,

Przepływ testu: tax.feature -> Given/When/Then -> FastAPI TestClient
-> GET /tax/scale -> istniejąca funkcja annual_scale_pit().


import pytest

pytest.importorskip(
    "pytest_bdd",
    reason="BDD wymaga: py -m pip install -r requirements-optional.txt",
)

from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, scenarios, then, when

from taxlab.api import create_app

# Ten sam tekst musi występować w pliku .feature i w dekoratorach kroków.
# Ścieżka ../features/ jest liczona względem folderu tests/.
scenarios("../features/tax.feature")


@pytest.fixture
def context(tmp_path):
    """Izolowany klient API. create_app() tworzy też osobną testową bazę."""
    database = tmp_path / "tax_bdd.sqlite3"
    return {"client": TestClient(create_app(database))}


@given("the simplified tax calculator is available")
def calculator_is_available(context):
    """GIVEN: potwierdzamy, że API działa, zanim wykonamy obliczenie."""
    response = context["client"].get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@when(parsers.parse("client requests tax for base {base:d}"))
def request_tax(context, base):
    """WHEN: liczba ze Scenario Outline trafia do parametru GET ?base=."""
    context["response"] = context["client"].get(
        "/tax/scale", params={"base": str(base)}
    )
    context["base"] = base


@then(parsers.parse("estimated tax is {expected}"))
def check_tax_result(context, expected):
    """THEN: sprawdzamy HTTP, podstawę i dokładny wynik (2 miejsca po przecinku)."""
    response = context["response"]
    assert response.status_code == 200
    body = response.json()
    assert body["base"] == str(context["base"])
    assert body["estimated_tax"] == expected
'''

# ZADANIE F 
'''
Ćwiczenie F — doprecyzowanie specyfikacji i testy BDD.

NIEJASNE: „Klient może rezerwować dowolny wolny termin”.
USTALONE Z WŁAŚCICIELEM PRODUKTU (przykładowe decyzje):
  1. Wizyta trwa umowną godzinę, początek tylko o HH:00.
  2. Jeden księgowy nie ma dwóch aktywnych wizyt w tym samym slocie.
  3. Klient może anulować wyłącznie własną rezerwację.

UWAGA: limit liczby różnych terminów u jednego klienta jest NIEUSTALONY;
nie dopisujemy testu wymagającego nieuzgodnionego zachowania.



import pytest

pytest.importorskip(
    "pytest_bdd",
    reason="BDD wymaga: py -m pip install -r requirements-optional.txt",
)

from fastapi.testclient import TestClient
from pytest_bdd import given, scenarios, then, when

from taxlab.api import create_app
from taxlab.consultations import count_confirmed, get_booking

scenarios("../features/booking_requirements.feature")

SLOT_1000 = "2030-05-14 10:00"
SLOT_1030 = "2030-05-14 10:30"


@pytest.fixture
def context(tmp_path):
    """Oddzielna baza SQLite dla KAŻDEGO scenariusza BDD."""
    db_path = tmp_path / "booking_spec.sqlite3"
    return {
        "db": db_path,
        "client": TestClient(create_app(db_path)),
    }


@given("Anna has no consultation at 10:30")
def anna_is_free_at_1030(context):
    """GIVEN: test zaczyna się od pustej bazy."""
    assert count_confirmed(context["db"], "Anna", SLOT_1030) == 0


@given("Jan has a confirmed consultation with Anna at 10:00")
def jan_has_booking(context):
    """GIVEN: rezerwujemy przez API i zapamiętujemy ID do testu 403."""
    response = context["client"].post(
        "/consultations",
        json={"accountant": "Anna", "slot": SLOT_1000},
        headers={"X-User": "Jan"},
    )
    assert response.status_code == 201
    context["jan_booking_id"] = response.json()["booking"]["id"]


@when("Jan requests a consultation at 10:30")
def jan_requests_1030(context):
    """WHEN: niepoprawny slot ma zostać odrzucony przez walidację."""
    context["response"] = context["client"].post(
        "/consultations",
        json={"accountant": "Anna", "slot": SLOT_1030},
        headers={"X-User": "Jan"},
    )


@when("Ewa requests Jan's booked slot")
def ewa_requests_busy_slot(context):
    """WHEN: Ewa próbuje zająć ten sam termin co Jan."""
    context["response"] = context["client"].post(
        "/consultations",
        json={"accountant": "Anna", "slot": SLOT_1000},
        headers={"X-User": "Ewa"},
    )


@when("Ewa attempts to cancel Jan's booking")
def ewa_attempts_cancel(context):
    """WHEN: ID rezerwacji zna Ewa, ale nie jest jej właścicielem."""
    context["response"] = context["client"].delete(
        f"/consultations/{context['jan_booking_id']}",
        headers={"X-User": "Ewa"},
    )


@then("the API rejects the slot with HTTP 422")
def rejected_slot(context):
    assert context["response"].status_code == 422


@then("no confirmed booking exists at 10:30")
def no_booking_at_1030(context):
    """THEN: nie wystarczy 422 — baza musi pozostać bez tego wpisu."""
    assert count_confirmed(context["db"], "Anna", SLOT_1030) == 0


@then("the API rejects the booking with HTTP 409")
def booking_conflict(context):
    assert context["response"].status_code == 409


@then("only Jan has a confirmed booking at 10:00")
def only_jan_has_booking(context):
    """THEN: w bazie jedna aktywna rezerwacja, należąca do Jana."""
    assert count_confirmed(context["db"], "Anna", SLOT_1000) == 1
    booking = get_booking(context["db"], context["jan_booking_id"])
    assert booking["client"] == "Jan"
    assert booking["status"] == "confirmed"


@then("the API refuses cancellation with HTTP 403")
def forbidden_cancel(context):
    assert context["response"].status_code == 403


@then("Jan's booking remains confirmed")
def jan_booking_untouched(context):
    """THEN: odmowa dostępu nie może anulować rezerwacji Jana."""
    booking = get_booking(context["db"], context["jan_booking_id"])
    assert booking["client"] == "Jan"
    assert booking["status"] == "confirmed"
    assert count_confirmed(context["db"], "Anna", SLOT_1000) == 1

'''
