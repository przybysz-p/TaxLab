"""Uruchom: python -m taxlab 120001"""
import sys
from .calculator import annual_scale_pit

if __name__ == "__main__":
    value = sys.argv[1] if len(sys.argv) > 1 else "120001"
    print(f"Podstawa roczna: {value} PLN")
    print(f"Poglądowy podatek: {annual_scale_pit(value)} PLN")
    print("UWAGA: model dydaktyczny, nie deklaracja PIT.")
