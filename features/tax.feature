# Przykład E: dwie wartości przy granicy 120 000 PLN.
# Model podatkowy jest celowo uproszczony; nie służy do rozliczeń podatkowych.
Feature: Calculating simplified PIT near the threshold
  The tax preview API reuses the calculator from earlier exercises.

  Scenario Outline: Tax near threshold
    Given the simplified tax calculator is available
    When client requests tax for base <base>
    Then estimated tax is <expected>

    Examples:
      | base   | expected |
      | 120000 | 10800.00 |
      | 120001 | 10800.32 |
