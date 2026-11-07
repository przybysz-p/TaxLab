"""05 — Dane testowe z fixture, dostarczane automatycznie przez pytest.

Każda funkcja test_... ma jeden cel; uruchom: python -m pytest tests/test_05_fixtures.py -v
"""

from decimal import Decimal
from taxlab.calculator import annual_from_months, annual_scale_pit


def test_12_months(monthly_revenue_costs):
    """Fixture monthly_revenue_costs udostępnia 12 miesięcy danych wejściowych."""
    base = annual_from_months(monthly_revenue_costs)
    assert base == Decimal("120000")
    assert annual_scale_pit(base) == Decimal("10800.00")
