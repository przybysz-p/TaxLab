"""08 — Hypothesis: generowane dane, weryfikacja własności funkcji.

Każda funkcja test_... ma jeden cel; uruchom: python -m pytest tests/test_08_properties.py -v
"""

import pytest
from taxlab.calculator import annual_scale_pit

hypothesis = pytest.importorskip("hypothesis", reason="Rozszerzenie opcjonalne")
from hypothesis import given, strategies as st


@given(st.integers(min_value=0, max_value=500000))
def test_tax_is_nonnegative(base):
    """Hipoteza: podatek nie staje się ujemny dla nieujemnej podstawy."""
    assert annual_scale_pit(base) >= 0


@given(st.integers(min_value=0, max_value=500000))
def test_tax_is_monotonic(base):
    """Hipoteza: wzrost podstawy o 1 zł nie powinien obniżać podatku."""
    assert annual_scale_pit(base + 1) >= annual_scale_pit(base)
