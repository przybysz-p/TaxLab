"""ĆWICZENIE B: opracuj 4 testy ryczałtu przy zadanej stawce 8,5%.

Ważne: to ćwiczenie testuje rachunek revenue*rate, a nie legalność stawki.
Zaplanuj dane: 0, 1000, 100000, ujemny przychód.
"""
from taxlab.calculator import annual_lump_sum_tax


def test_ryczalt_1000():
    assert annual_lump_sum_tax("1000", "0.085") == 85

""" Rozwiązanie
import pytest
from decimal import Decimal
from taxlab.calculator import annual_lump_sum_tax

@pytest.mark.parametrize("revenue, expected", [
    ("0", "0.00"),
    ("1000", "85.00"),
    ("100000", "8500.00"),
])
def test_ryczalt(revenue, expected):
    assert annual_lump_sum_tax(
        revenue, "0.085"
    ) == Decimal(expected)


def test_negative_revenue():
    with pytest.raises(ValueError):
        annual_lump_sum_tax("-1", "0.085")

"""