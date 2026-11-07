"""ĆWICZENIE C: znajdź dwa błędy w poniższej funkcji i napisz testy,
które je ujawnią. Ten plik NIE jest automatycznie zbierany przez pytest.
"""
from decimal import Decimal


def bad_scale_pit(base):
    base = Decimal(str(base))
    if base < 120000:  # BŁĄD 1: granica (porównaj z wymaganiem)
        return max(Decimal("0"), base * Decimal("0.12") - 3600)
    return base * Decimal("0.32") - 3600  # BŁĄD 2: cała kwota zamiast nadwyżki
