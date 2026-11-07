"""03 — Niepoprawne dane: pytest.raises sprawdza OCZEKIWANY wyjątek.

Każda funkcja test_... ma jeden cel; uruchom: python -m pytest tests/test_03_negative.py -v
"""

import pytest
from taxlab.calculator import annual_income, annual_scale_pit, annual_lump_sum_tax, apply_vat


@pytest.mark.parametrize("value", [-1, "abc", None, True, "NaN"])
def test_bad_tax_base_rejected_or_safe(value):
    """Niepoprawny typ ma zgłosić ValueError; podstawa -1 daje w tym modelu zero."""
    if value == -1:
        # Strata podatkowa (ujemna podstawa) w modelu daje zero.
        assert annual_scale_pit(value) == 0
    else:
        with pytest.raises(ValueError):
            annual_scale_pit(value)


def test_negative_revenue_raises():
    """Ujemny przychód nie jest akceptowany; oczekiwany jest wyjątek ValueError."""
    with pytest.raises(ValueError, match="nieujemne"):
        annual_income("-10", "3")


def test_ryczalt_rate_out_of_range():
    """Stawka 1.2 oznacza 120%, czyli poza dozwolonym zakresem tej funkcji."""
    with pytest.raises(ValueError, match="Stawka"):
        annual_lump_sum_tax("1000", "1.2")


def test_vat_negative():
    """Nie można w tym modelu obliczać VAT od ujemnej ceny netto."""
    with pytest.raises(ValueError):
        apply_vat("-10")
