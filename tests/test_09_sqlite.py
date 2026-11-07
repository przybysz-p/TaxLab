"""09 — TESTY INTEGRACYJNE: logika rezerwacji + prawdziwa SQLite.

Czego chcemy dowieść?
- zapis przeżywa zamknięcie połączenia z bazą;
- UNIQUE chroni przed podwójną rezerwacją;
- ROLLBACK usuwa niezatwierdzony zapis po awarii;
- anulowanie zwalnia termin;
- ponowione żądanie z tym samym kluczem nie tworzy duplikatu;
- równoległe żądania nie pozwalają dwóm osobom zająć tego samego terminu.

To NIE są testy z mockiem. Każdy korzysta z osobnej bazy w katalogu
utworzonym przez pytest (fixture db_path w tests/conftest.py).
Uruchom: python -m pytest tests/test_09_sqlite.py -v
"""

from concurrent.futures import ThreadPoolExecutor

import pytest

from taxlab.consultations import (
    RequestConflict,
    SlotBusy,
    book,
    cancel,
    count_confirmed,
    get_booking,
)

# W modelu konsultacje trwają jedną godzinę i zaczynają się o pełnej godzinie.
SLOT = "2030-05-14 10:00"


def test_booking_survives_new_connection(db_path):
    """Trwałość: rezerwacja jest widoczna po nowym połączeniu z SQLite."""
    # ARRANGE: db_path wskazuje świeżą bazę testową; termin jest wolny.
    # ACT: zapisujemy wizytę. book() zwraca (słownik_rezerwacji, czy_powtórka).
    booking, replayed = book(db_path, "Anna", "Jan", SLOT)

    # ASSERT: zapis powinien być nowy, a nie powtórzony.
    assert replayed is False
    # get_booking() otwiera nowe połączenie, więc sprawdza utrwalony zapis.
    saved = get_booking(db_path, booking["id"])
    assert saved["client"] == "Jan"
    assert saved["status"] == "confirmed"


def test_duplicate_slot_rejected_by_real_database(db_path):
    """UNIQUE: w tym samym terminie u Anny tylko jedna aktywna konsultacja."""
    # ARRANGE: Jan zajął termin.
    book(db_path, "Anna", "Jan", SLOT)

    # ACT + ASSERT: Ewa próbuje zarezerwować ten sam termin.
    # pytest.raises(SlotBusy) = OCZEKUJEMY odmowy; wyjątek oznacza PASS.
    with pytest.raises(SlotBusy):
        book(db_path, "Anna", "Ewa", SLOT)

    # ASSERT: w bazie pozostała dokładnie jedna potwierdzona rezerwacja.
    assert count_confirmed(db_path, "Anna", SLOT) == 1


def test_transaction_rolls_back_if_exception_before_commit(db_path):
    """ROLLBACK: awaria po INSERT, ale przed COMMIT, nie pozostawia rekordu."""
    # ARRANGE: pusta baza testowa.
    # ACT: wstrzykujemy celowy błąd (simulate_failure=True).
    # Funkcja book() zdąży wykonać INSERT, po czym zgłosi RuntimeError.
    with pytest.raises(RuntimeError, match="Symulowana"):
        book(db_path, "Anna", "Jan", SLOT, simulate_failure=True)

    # ASSERT: transakcja została wycofana; nie ma „połowy rezerwacji”.
    assert count_confirmed(db_path, "Anna", SLOT) == 0


def test_cancel_frees_slot(db_path):
    """Po anulowaniu przez Jana ten sam termin może zarezerwować Ewa."""
    # ARRANGE: Jan rezerwuje termin.
    first, _ = book(db_path, "Anna", "Jan", SLOT)

    # ACT: Jan anuluje, Ewa rezerwuje zwolniony termin.
    cancelled = cancel(db_path, first["id"], "Jan")
    second, _ = book(db_path, "Anna", "Ewa", SLOT)

    # ASSERT: anulowana wizyta nie blokuje nowej.
    assert cancelled["status"] == "cancelled"
    assert second["id"] != first["id"]
    assert count_confirmed(db_path, "Anna", SLOT) == 1


def test_retry_same_key_does_not_duplicate(db_path):
    """Idempotencja: powtórne wysłanie tej samej prośby nie tworzy nowej wizyty."""
    # ARRANGE: identyfikator żądania od klienta (np. po awarii sieci).
    request_key = "client-request-123"

    # ACT: dwa identyczne żądania z tym samym kluczem.
    first, first_replayed = book(db_path, "Anna", "Jan", SLOT, request_key)
    second, second_replayed = book(db_path, "Anna", "Jan", SLOT, request_key)

    # ASSERT: pierwsze tworzy wizytę, drugie zwraca tę samą.
    assert first_replayed is False
    assert second_replayed is True
    assert first["id"] == second["id"]
    assert count_confirmed(db_path, "Anna", SLOT) == 1


def test_key_reused_with_different_request_is_conflict(db_path):
    """Ten sam request_key nie może oznaczać dwóch różnych operacji."""
    # ARRANGE: klucz już wykorzystany dla rezerwacji Jana.
    book(db_path, "Anna", "Jan", SLOT, "client-request-123")

    # ACT + ASSERT: ten sam klucz, ale inny klient i inna godzina.
    # Oczekujemy RequestConflict, żeby nie pomylić dwóch operacji.
    with pytest.raises(RequestConflict):
        book(db_path, "Anna", "Ewa", "2030-05-14 11:00", "client-request-123")


def test_parallel_bookings_only_one_wins(db_path):
    """Współbieżność: Jan i Ewa próbują rezerwować tę samą godzinę równocześnie."""
    # ARRANGE: dwa zadania dostaną tę samą bazę i SLOT.
    def attempt(client_name):
        """Funkcja pojedynczego klienta — zwraca prosty opis wyniku."""
        try:
            book(db_path, "Anna", client_name, SLOT)
            return "created"
        except SlotBusy:
            return "conflict"

    # ACT: ThreadPoolExecutor uruchamia próby w dwóch wątkach.
    # map() zbiera wyniki do listy — kolejność zwycięzcy nie jest ustalona.
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(attempt, ["Jan", "Ewa"]))

    # ASSERT: liczy się 1 sukces i 1 konflikt, NIE to, kto był pierwszy.
    assert sorted(results) == ["conflict", "created"]
    # Sam wynik wątków nie wystarczy: potwierdzamy również stan bazy.
    assert count_confirmed(db_path, "Anna", SLOT) == 1

# PYTANIE DO GRUPY:
# Czy ten ostatni test gwarantuje brak wyścigu na KAŻDEJ bazie danych?
# Nie — sprawdza konkretną implementację na SQLite przy zadanym scenariuszu.
# W systemie produkcyjnym testujemy też konfigurację docelowej bazy.
