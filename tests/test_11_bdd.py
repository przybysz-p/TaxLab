"""11 — BDD (Behavior-Driven Development) i Gherkin: opis -> wykonywany test.

Scenariusze biznesowe są w features/consultations.feature.
Given = warunki początkowe, When = działanie, Then = oczekiwany efekt.

Tu testujemy PRZEZ FastAPI TestClient i REALNĄ bazę SQLite, nie samą
implementację zdań Gherkina. Wymagana biblioteka pytest-bdd (opcjonalna).
Uruchom: python -m pytest tests/test_11_bdd.py -v
"""

import pytest

# Pozwala uruchomić podstawowe testy nawet bez opcjonalnej biblioteki BDD.
pytest.importorskip("pytest_bdd", reason="Zainstaluj: pip install -r requirements-optional.txt")

from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, scenarios, then, when

from taxlab.api import create_app
from taxlab.consultations import count_confirmed, init_db

# Po przeniesieniu testu do tests/ ścieżka do features/ ma JEDNO ../.
scenarios("../features/consultations.feature")

SLOT = "2030-05-14 10:00"


@pytest.fixture
def context(tmp_path):
    """Każdy scenariusz BDD dostaje czystą bazę i klienta HTTP."""
    db_path = tmp_path / "bdd.sqlite3"
    init_db(db_path)
    return {"db": db_path, "client": TestClient(create_app(db_path))}


@given("Jan has booked Anna on 2030-05-14 at 10:00")
def already_booked(context):
    """GIVEN: w bazie już istnieje potwierdzona rezerwacja Jana."""
    response = context["client"].post(
        "/consultations",
        json={"accountant": "Anna", "slot": SLOT},
        headers={"X-User": "Jan"},
    )
    assert response.status_code == 201


@given("the consultation slot is free")
def slot_is_free(context):
    """GIVEN: sprawdzamy początkowy stan testowej bazy."""
    assert count_confirmed(context["db"], "Anna", SLOT) == 0


@when("Ewa tries to book the same slot")
def ewa_try(context):
    """WHEN: Ewa wysyła prawdziwe żądanie HTTP do naszego API."""
    context["result"] = context["client"].post(
        "/consultations",
        json={"accountant": "Anna", "slot": SLOT},
        headers={"X-User": "Ewa"},
    )


@when("Jan sends the same booking key twice")
def jan_retries(context):
    """WHEN: dwa żądania z request_key=K1; może to być retry po zaniku sieci."""
    body = {"accountant": "Anna", "slot": SLOT, "request_key": "K1"}
    context["first"] = context["client"].post(
        "/consultations", json=body, headers={"X-User": "Jan"}
    )
    context["second"] = context["client"].post(
        "/consultations", json=body, headers={"X-User": "Jan"}
    )


@when(parsers.parse("Jan requests slot {slot}"))
def jan_requests(context, slot):
    """WHEN: parametr ze Scenario Outline zastępuje {slot}."""
    context["result"] = context["client"].post(
        "/consultations",
        json={"accountant": "Anna", "slot": slot.replace("_", " ")},
        headers={"X-User": "Jan"},
    )


@then("the API returns conflict 409")
def status_conflict(context):
    """THEN: porównujemy zwrócony status z oczekiwanym HTTP 409."""
    assert context["result"].status_code == 409


@then("the first booking remains the only confirmed booking")
def no_double(context):
    """THEN: czytamy stan SQLite — nie wystarczy sam kod HTTP."""
    assert count_confirmed(context["db"], "Anna", SLOT) == 1


@then("both responses refer to one booking")
def retry_is_single(context):
    """THEN: jedna konsultacja, mimo że klient wysłał dwa POST-y."""
    assert context["first"].status_code == 201
    assert context["second"].status_code == 200
    assert context["first"].json()["booking"]["id"] == context["second"].json()["booking"]["id"]
    assert count_confirmed(context["db"], "Anna", SLOT) == 1


@then(parsers.parse("the API status is {status:d}"))
def status_is(context, status):
    """THEN: {status:d} z Gherkina zamienia się na liczbę całkowitą."""
    assert context["result"].status_code == status

# NOWE ĆWICZENIE C (anulowanie): patrz cwiczenia/zadanie_C_BDD.py.
# Tam znajduje się gotowy scenariusz i implementacja kroków, ale jako
# KOMENTARZE, żeby nie wykonywać ich automatycznie przed rozwiązaniem.
