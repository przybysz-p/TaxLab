"""Zależności, które w testach można zastąpić mockiem lub monkeypatch."""
import os
from datetime import date
from .calculator import annual_scale_pit, to_money


def get_tax_year():
    """Konfiguracja aplikacji odczytywana ze zmiennej środowiskowej."""
    return int(os.getenv("TAX_YEAR", "2026"))


def format_tax_report(tax_base, today=None):
    """Data może być podana przez test — bez zależności od prawdziwego zegara."""
    today = today or date.today()
    return f"{today.isoformat()}: przy podstawie {tax_base} zł PIT≈{annual_scale_pit(tax_base)} zł"


def send_tax_report(tax_base, sender):
    """Wysyłkę delegujemy do obiektu sender; w teście zamienimy go na mock."""
    message = f"Szacowany PIT: {annual_scale_pit(tax_base)} PLN"
    sender.send(message)
    return message


def convert_eur_to_pln(eur_amount, rate_provider):
    """Zewnętrzny kurs: provider.get_rate('EUR', 'PLN') (w testach mock)."""
    rate = to_money(rate_provider.get_rate("EUR", "PLN"))
    if rate <= 0:
        raise ValueError("Kurs musi być dodatni")
    return to_money(eur_amount) * rate
