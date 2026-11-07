"""02 — Wartości brzegowe i parametryzacja: jedna funkcja testowa, różne dane.

Każda funkcja test_... ma jeden cel; uruchom: python -m pytest tests/test_02_boundaries.py -v
"""

from decimal import Decimal
import pytest
from taxlab.calculator import annual_scale_pit, annual_income


@pytest.mark.parametrize("base, expected", [
    ("0", "0.00"),
    ("29999", "0.00"),
    ("30000", "0.00"),
    ("30001", "0.12"),
    ("119999", "10799.88"),
    ("120000", "10800.00"),
    ("120001", "10800.32"),
    ("150000", "20400.00"),
])
def test_scale_equivalence_and_boundaries(base, expected):
    """pytest uruchomi funkcję osobno dla każdego zestawu (base, expected)."""
    assert annual_scale_pit(base) == Decimal(expected)


@pytest.mark.parametrize("revenue, costs, expected", [
    ("0", "0", "0"),
    ("100000", "20000", "80000"),
    ("1000", "2000", "-1000"),
])
def test_income(revenue, costs, expected):
    """Sprawdzamy przychody minus koszty, w tym przypadek straty."""
    assert annual_income(revenue, costs) == Decimal(expected)
