"""06 — Mock zastępuje pocztę i kurs walut, więc nie używamy sieci.

Każda funkcja test_... ma jeden cel; uruchom: python -m pytest tests/test_06_mocks.py -v
"""

from decimal import Decimal
from unittest.mock import Mock
from taxlab.report import send_tax_report, convert_eur_to_pln


def test_email_is_sent_without_real_email():
    """Mock sprawdza jedno wywołanie send() z treścią raportu; nic nie wysyła."""
    fake_sender = Mock()
    result = send_tax_report("120001", fake_sender)
    assert "10800.32" in result
    fake_sender.send.assert_called_once_with(result)


def test_exchange_rate_without_real_web():
    """Podstawiamy kurs EUR/PLN=4.20 i kontrolujemy wywołanie dostawcy."""
    fake_provider = Mock()
    fake_provider.get_rate.return_value = "4.20"
    assert convert_eur_to_pln("100", fake_provider) == Decimal("420.00")
    fake_provider.get_rate.assert_called_once_with("EUR", "PLN")
