"""07 — Kontrolowane środowisko i data: powtarzalne testy.

Każda funkcja test_... ma jeden cel; uruchom: python -m pytest tests/test_07_monkeypatch.py -v
"""

from datetime import date
from taxlab.report import get_tax_year, format_tax_report


def test_year_from_environment(monkeypatch):
    """monkeypatch ustawia TAX_YEAR=2025 tylko na czas danego testu."""
    monkeypatch.setenv("TAX_YEAR", "2025")
    assert get_tax_year() == 2025


def test_report_is_independent_of_today():
    """Przekazujemy datę wprost, zamiast polegać na zegarze komputera."""
    # Wstrzykujemy datę zamiast polegać na realnym zegarze.
    assert format_tax_report("120000", date(2026, 12, 31)).startswith("2026-12-31")
