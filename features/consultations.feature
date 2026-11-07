Feature: Booking an accountant consultation
  A slot is occupied by at most one confirmed booking.

  Scenario: Another customer cannot reserve a busy slot
    Given Jan has booked Anna on 2030-05-14 at 10:00
    When Ewa tries to book the same slot
    Then the API returns conflict 409
    And the first booking remains the only confirmed booking

  Scenario: Repeating the same request does not create a duplicate
    Given the consultation slot is free
    When Jan sends the same booking key twice
    Then both responses refer to one booking

  Scenario Outline: Invalid and valid slot forms
    Given the consultation slot is free
    When Jan requests slot <slot>
    Then the API status is <status>

    Examples:
      | slot              | status |
      | 2030-05-14_08:00  | 422    |
      | 2030-05-14_10:30  | 422    |
      | 2030-05-14_11:00  | 201    |
