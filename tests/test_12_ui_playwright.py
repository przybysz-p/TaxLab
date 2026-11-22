"""Opcjonalne testy UI/E2E TaxLab. Każdy test uruchamia lokalny serwer i własną SQLite.

Instalacja: py -m pip install pytest-playwright uvicorn
           py -m playwright install chromium
Wykonanie: py -m pytest tests/test_12_ui_playwright.py -v --headed
"""
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen

import pytest

pytest.importorskip('pytest_playwright', reason='Zainstaluj: py -m pip install pytest-playwright uvicorn')
from playwright.sync_api import Page, expect

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def ui_url(tmp_path):
    """Izoluje dane i uruchamia serwer HTTP na losowym wolnym porcie."""
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    url = f'http://127.0.0.1:{port}'
    env = dict(os.environ, TAXLAB_DB=str(tmp_path / 'ui_e2e.sqlite3'))
    proc = subprocess.Popen(
        [sys.executable, '-m', 'uvicorn', 'taxlab.ui_demo:app',
         '--host', '127.0.0.1', '--port', str(port)],
        cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(80):
            if proc.poll() is not None:
                pytest.fail('Serwer demonstracyjny TaxLab nie uruchomił się.')
            try:
                with urlopen(url + '/health', timeout=0.3) as response:
                    if response.status == 200:
                        break
            except Exception:
                time.sleep(0.1)
        else:
            pytest.fail('Brak odpowiedzi lokalnego serwera TaxLab.')
        yield url
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)


def test_pit_w_przegladarce(page: Page, ui_url):
    page.goto(ui_url)
    page.get_by_label('Podstawa PIT (PLN)').fill('120001')
    page.get_by_role('button', name='Oblicz PIT').click()
    expect(page.get_by_role('status', name='Wynik podatku')).to_contain_text('10800.32 PLN')


def test_rezerwacja_jana_przez_ui(page: Page, ui_url):
    page.goto(ui_url)
    page.get_by_label('Klient').fill('Jan')
    page.get_by_label('Księgowa').fill('Anna')
    page.get_by_label('Termin (YYYY-MM-DD HH:00)').fill('2030-05-14 10:00')
    page.get_by_role('button', name='Zarezerwuj').click()
    expect(page.get_by_role('status', name='Wynik rezerwacji')).to_contain_text('Potwierdzono')


def test_zajety_termin_przez_ui(page: Page, ui_url):
    page.goto(ui_url)
    page.get_by_label('Klient').fill('Jan')
    page.get_by_role('button', name='Zarezerwuj').click()
    expect(page.get_by_role('status', name='Wynik rezerwacji')).to_contain_text('Potwierdzono')

    page.get_by_label('Klient').fill('Ewa')
    page.get_by_role('button', name='Zarezerwuj').click()
    expect(page.get_by_role('status', name='Wynik rezerwacji')).to_contain_text('HTTP 409')
