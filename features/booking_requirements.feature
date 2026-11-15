# Przykład F: po doprecyzowaniu wymagań przez właściciela produktu.
# Nie testujemy „dowolnego wolnego terminu”, tylko trzy UZGODNIONE reguły.
Feature: Explicit rules for booking accountant consultations
  Bookings start on the hour, cannot overlap for one accountant,
  and can be cancelled only by their owner.

  Scenario: A booking cannot start at half past the hour
    Given Anna has no consultation at 10:30
    When Jan requests a consultation at 10:30
    Then the API rejects the slot with HTTP 422
    And no confirmed booking exists at 10:30

  Scenario: A busy slot cannot be booked by a second person
    Given Jan has a confirmed consultation with Anna at 10:00
    When Ewa requests Jan's booked slot
    Then the API rejects the booking with HTTP 409
    And only Jan has a confirmed booking at 10:00

  Scenario: A different person cannot cancel Jan's booking
    Given Jan has a confirmed consultation with Anna at 10:00
    When Ewa attempts to cancel Jan's booking
    Then the API refuses cancellation with HTTP 403
    And Jan's booking remains confirmed
