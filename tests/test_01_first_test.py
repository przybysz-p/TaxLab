"""01 — AAA (Arrange / Act / Assert) i próg podatkowy.

Każda funkcja test_... ma jeden cel; uruchom: python -m pytest tests/test_01_first_test.py -v
"""

from decimal import Decimal
from taxlab.calculator import annual_income, annual_scale_pit


def test_annual_income_arrange_act_assert():
    """Sprawdzamy roczny dochód: 150000 przychodu minus 30000 kosztów = 120000."""
    # Arrange: roczne sumy (PLN)
    revenue, costs = "150000", "30000"
    # Act: wywołanie funkcji
    actual = annual_income(revenue, costs)
    # Assert: oczekiwana różnica
    assert actual == Decimal("120000")


def test_tax_exact_threshold():
    """Na granicy 120000 model powinien zwrócić 10800.00."""
    assert annual_scale_pit("120000") == Decimal("10800.00")
