"""Edukacyjna logika na bazie parametrów skali PIT 2026.

NIE jest kalkulatorem prawno-podatkowym: pomija odliczenia, składki,
zdrowotne, prawne zasady zaokrągleń i indywidualne okoliczności.
Wyniki w groszach służą do testów obliczeń, a nie do zeznań PIT.
"""
from decimal import Decimal, ROUND_HALF_UP

FIRST_THRESHOLD = Decimal("120000")
LOW_RATE = Decimal("0.12")
HIGH_RATE = Decimal("0.32")
TAX_REDUCTION = Decimal("3600")
GROSZ = Decimal("0.01")


def to_money(value):
    """Przyjmuje kwotę jako tekst/liczbę/Decimal; odrzuca bool i dane nieliczbowe."""
    if isinstance(value, bool):
        raise ValueError("Kwota nie może być wartością bool")
    try:
        result = Decimal(str(value))
    except Exception as exc:
        raise ValueError("Niepoprawna kwota") from exc
    if not result.is_finite():
        raise ValueError("Kwota musi być skończona")
    return result


def annual_income(revenue, costs):
    """Dochód = roczny przychód minus roczne koszty; może być ujemny (strata)."""
    revenue, costs = to_money(revenue), to_money(costs)
    if revenue < 0 or costs < 0:
        raise ValueError("Przychód i koszty muszą być nieujemne")
    return revenue - costs


def annual_scale_pit(tax_base):
    """Poglądowe obliczenie rocznego PIT w skali 2026, bez ulg i składek."""
    tax_base = to_money(tax_base)
    if tax_base <= 0:
        return Decimal("0.00")
    if tax_base <= FIRST_THRESHOLD:
        tax = tax_base * LOW_RATE - TAX_REDUCTION
    else:
        tax = Decimal("10800") + (tax_base - FIRST_THRESHOLD) * HIGH_RATE
    return max(Decimal("0"), tax).quantize(GROSZ, rounding=ROUND_HALF_UP)


def annual_lump_sum_tax(revenue, rate):
    """Ryczałt: PRZYCHÓD × zadana stawka; bez ulg, składek, odliczeń.

    Dobór właściwej stawki do rzeczywistej działalności jest POZA zakresem.
    rate=0.085 oznacza 8,5%, rate=0.12 oznacza 12%.
    """
    revenue, rate = to_money(revenue), to_money(rate)
    if revenue < 0:
        raise ValueError("Przychód nie może być ujemny")
    if not Decimal("0") <= rate <= Decimal("1"):
        raise ValueError("Stawka powinna należeć do zakresu [0,1]")
    return (revenue * rate).quantize(GROSZ, rounding=ROUND_HALF_UP)


def annual_from_months(months):
    """Każdy miesiąc: {'revenue': '10000', 'costs': '2000'}; 12 pozycji."""
    if len(months) != 12:
        raise ValueError("Rok powinien zawierać dokładnie 12 miesięcy")
    total_rev = sum((to_money(m['revenue']) for m in months), Decimal("0"))
    total_costs = sum((to_money(m['costs']) for m in months), Decimal("0"))
    return annual_income(total_rev, total_costs)


def apply_vat(net, rate="0.23"):
    """Niezależny przykład VAT: kwota netto × (1+stawka)."""
    net, rate = to_money(net), to_money(rate)
    if net < 0 or not Decimal("0") <= rate <= Decimal("1"):
        raise ValueError("Niepoprawna kwota lub stawka VAT")
    return (net * (Decimal("1") + rate)).quantize(GROSZ, rounding=ROUND_HALF_UP)
