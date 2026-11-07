"""04 — Uproszczone reguły biznesowe: ryczałt oraz VAT.

Każda funkcja test_... ma jeden cel; uruchom: python -m pytest tests/test_04_ryczalt.py -v
"""

from decimal import Decimal
import pytest
from taxlab.calculator import annual_lump_sum_tax, annual_income, apply_vat


@pytest.mark.parametrize("revenue, rate, expected", [
    ("0", "0.085", "0.00"),
    ("1000", "0.085", "85.00"),
    ("120000", "0.12", "14400.00"),
    ("150000", "0.085", "12750.00"),
])
def test_ryczalt(revenue, rate, expected):
    """Parametryzowane przykłady przychodów i stawek ryczałtu."""
    assert annual_lump_sum_tax(revenue, rate) == Decimal(expected)


def test_ryczalt_does_not_subtract_costs():
    """Porównujemy dochód i ryczałt: podstawą ryczałtu jest tu przychód."""
    # Koszt nie jest argumentem funkcji ryczałtu. To inna podstawa niż skala.
    assert annual_income("100000", "80000") == Decimal("20000")
    assert annual_lump_sum_tax("100000", "0.085") == Decimal("8500.00")


def test_vat_gross():
    """100 zł netto plus 23% VAT to 123 zł brutto."""
    assert apply_vat("100", "0.23") == Decimal("123.00")
