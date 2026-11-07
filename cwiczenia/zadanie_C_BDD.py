"""ZADANIE C — Gherkin + pytest-bdd + prawdziwe API.

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
