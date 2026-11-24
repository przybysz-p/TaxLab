"""Ćwiczenie 13: Locust + prawdziwe zapisy do SQLite przez API TaxLab.

DWA TRYBY:
  unique    - każdy POST rezerwuje inny termin: spodziewamy się HTTP 201.
  conflict  - wszyscy walczą o ten sam termin: 1 x HTTP 201, później HTTP 409.

DWA PROFILE RUCHU (takie jak w poprzednim cwiczenia/test_13_locust.py):
  ramp      - 20 użytkowników, +50/min, 500 pod koniec testu.
  spike     - 100 użytkowników, w 3. minucie skok do 1000 na 60 sekund.

WAŻNE: uruchamiaj na OSOBNEJ lokalnej bazie, wyłącznie dydaktycznie.
Przykładowe polecenia znajdują się w odpowiedzi nauczyciela / na zajęciach.

W Locust zobaczysz osobne wiersze dla HTTP 201 i oczekiwanego HTTP 409.
HTTP 409 nie jest awarią: w tym scenariuszu świadczy o prawidłowej ochronie slotu.
HTTP 500, nieoczekiwane 409 w trybie unique, timeout lub zły JSON = FAIL.
"""

import itertools
import os
import uuid
from datetime import datetime, timedelta

from locust import HttpUser, LoadTestShape, between, task

DB_CASE = os.getenv("TAXLAB_DB_CASE", "unique").strip().lower()
PROFILE = os.getenv("TAXLAB_LOCUST_SCENARIO", "ramp").strip().lower()
if DB_CASE not in {"unique", "conflict"}:
    raise ValueError("TAXLAB_DB_CASE: 'unique' albo 'conflict'")
if PROFILE not in {"ramp", "spike"}:
    raise ValueError("TAXLAB_LOCUST_SCENARIO: 'ramp' albo 'spike'")

# Nowy identyfikator przy każdym uruchomieniu pliku Locust: zapobiega
# kolizjom z rezerwacjami z poprzedniego eksperymentu.
RUN_ID = uuid.uuid4().hex[:10]
ACCOUNTANT = f"Anna_load_{RUN_ID}"
COUNTER = itertools.count(0)
DAY_ZERO = datetime(2030, 1, 1)
BUSY_SLOT = "2030-05-14 10:00"


def new_slot_and_id():
    """Kolejne sloty (8 na dzień, godziny 9–16), bez losowych konfliktów."""
    number = next(COUNTER)
    date = DAY_ZERO + timedelta(days=number // 8, hours=9 + number % 8)
    return number, date.strftime("%Y-%m-%d %H:%M")


class TaxLabDatabaseUser(HttpUser):
    wait_time = between(2, 5)

    @task
    def post_reservation(self):
        if DB_CASE == "unique":
            self.create_unique_booking()
        else:
            self.compete_for_one_slot()

    def create_unique_booking(self):
        number, slot = new_slot_and_id()
        payload = {
            "accountant": ACCOUNTANT,
            "slot": slot,
            "request_key": f"{RUN_ID}-{number}",
        }
        with self.client.post(
            "/consultations", json=payload,
            headers={"X-User": f"Student_{RUN_ID}_{number}"},
            name="DB UNIKALNY / POST /consultations",
            catch_response=True, timeout=20,
        ) as response:
            if response.status_code != 201:
                response.request_meta["name"] = "DB UNIKALNY / FAIL"
                response.failure(f"Oczekiwano 201; HTTP {response.status_code}: {response.text[:150]}")
                return
            try:
                record = response.json()["booking"]
                if record["slot"] != slot or record["status"] != "confirmed":
                    raise ValueError("Niezgodny zapis rezerwacji w JSON")
            except (ValueError, KeyError, TypeError) as exc:
                response.request_meta["name"] = "DB UNIKALNY / FAIL"
                response.failure(f"Nieprawidłowy JSON: {exc}")
            else:
                response.request_meta["name"] = "DB UNIKALNY / 201 zapis OK"
                response.success()

    def compete_for_one_slot(self):
        payload = {"accountant": ACCOUNTANT, "slot": BUSY_SLOT}
        with self.client.post(
            "/consultations", json=payload,
            headers={"X-User": f"Student_{uuid.uuid4().hex[:10]}"},
            name="DB KONFLIKT / POST /consultations",
            catch_response=True, timeout=20,
        ) as response:
            if response.status_code == 201:
                response.request_meta["name"] = "DB KONFLIKT / 201 pierwszy zapis OK"
                response.success()
            elif response.status_code == 409:
                try:
                    detail = str(response.json().get("detail", ""))
                except (ValueError, AttributeError):
                    detail = ""
                if "zajety" in detail.lower() or "zajęty" in detail.lower():
                    response.request_meta["name"] = "DB KONFLIKT / 409 oczekiwany (OK)"
                    response.success()
                else:
                    response.request_meta["name"] = "DB KONFLIKT / FAIL"
                    response.failure(f"HTTP 409 z innego powodu: {detail[:150]}")
            else:
                response.request_meta["name"] = "DB KONFLIKT / FAIL"
                response.failure(f"Oczekiwano 201 lub 409; HTTP {response.status_code}: {response.text[:150]}")


class TaxLabDBLoadShape(LoadTestShape):
    """Dziesięciominutowy profil obciążenia taki sam jak przy GET /tax/scale."""

    def tick(self):
        seconds = self.get_run_time()
        if seconds >= 600:
            return None
        if PROFILE == "ramp":
            users = 500 if seconds >= 576 else 20 + 50 * int(seconds // 60)
            return users, 100
        users = 1000 if 180 <= seconds < 240 else 100
        return users, 200
