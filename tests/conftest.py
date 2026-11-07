"""Wspólne fixture dla testów 01–11.

Pytest automatycznie znajduje fixture w conftest.py. Przeniesienie testów
09–11 do jednego katalogu wymagało też przeniesienia fixture bazy i API tutaj.
"""

import pytest
from fastapi.testclient import TestClient

from taxlab.api import create_app
from taxlab.consultations import init_db


@pytest.fixture
def monthly_revenue_costs():
    """12 miesięcy przychodów 12 000 zł i kosztów 2 000 zł."""
    return [{"revenue": "12000", "costs": "2000"} for _ in range(12)]


@pytest.fixture
def db_path(tmp_path):
    """Osobna, pusta baza SQLite dla każdej funkcji testowej.

    tmp_path = katalog tymczasowy automatycznie tworzony przez pytest;
    init_db() zakłada tabelę consultations i indeks UNIQUE.
    """
    path = tmp_path / "consultations.sqlite3"
    init_db(path)
    return path


@pytest.fixture
def client(db_path):
    """TestClient wywołujący FastAPI z wcześniej utworzoną testową SQLite."""
    return TestClient(create_app(db_path))
