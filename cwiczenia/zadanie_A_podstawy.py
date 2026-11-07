"""ĆWICZENIE A: dopisz testy dla dochodu 120001 PLN i kosztów 1 PLN.

1. Oblicz dochód.
2. Oblicz podatek od rocznej podstawy.
3. Dopisz test, który celowo wykaże niepoprawną granicę 120000.
"""
from taxlab.calculator import annual_income, annual_scale_pit


def test_wypelnij():
    # TODO: zmień na własne asercje
    assert annual_income("120001", "1") == 120000

""" Rozwiązanie
from decimal import Decimal
from taxlab.calculator import annual_income, annual_scale_pit

def test_income_and_tax():
    # Arrange
    revenue = "120001"
    costs = "1"

    # Act
    income = annual_income(revenue, costs)
    tax = annual_scale_pit(income)

    # Assert
    assert income == Decimal("120000")
    assert tax == Decimal("10800.00")


def test_above_threshold():
    assert annual_scale_pit("120001") == Decimal("10800.32")


def test_exact_threshold():
    assert annual_scale_pit("120000") == Decimal("10800.00")

""" 