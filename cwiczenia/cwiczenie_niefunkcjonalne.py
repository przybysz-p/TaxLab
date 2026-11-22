"""ZARZĄDZANIE JAKOŚCIĄ — ĆWICZENIE 12: jakość niefunkcjonalna TaxLab.

Dwa zadania A/B z prezentacji — liczby są FIKCYJNE i służą do analizy,
nie są wynikami rzeczywistego pomiaru programu.

ĆWICZENIE A — DECYZJA GO / NO-GO (10–15 min)
Raport z fikcyjnego testu kolejnej wersji TaxLab:
  p95 POST /consultations = 780 ms          (przykładowy cel: p95 < 1000 ms)
  błędy HTTP = 0.2%                          (przykładowy cel: < 1%)
  2% osób korzystających z czytnika ekranu nie potrafi potwierdzić rezerwacji.

Zadania:
  1. Czy proponujesz GO czy NO-GO? Uzasadnij na podstawie ryzyka.
  2. Jakich danych brakuje, żeby podjąć odpowiedzialną decyzję?
  3. Czy dobry p95 i niski odsetek błędów neutralizują problem dostępności?
  4. Podaj trzy działania naprawcze i sposób weryfikacji.

ĆWICZENIE B — SOAK I ROSNĄCA PAMIĘĆ (10–15 min)
Fikcyjny test: 50 użytkowników, p95 = 650 ms, ale pamięć procesu Uvicorn
(RSS) rośnie z każdą minutą. Istnieje ryzyko wyczerpania RAM po godzinie.

Zadania:
  1. Jaki następny test uruchomisz (load, stress, spike czy soak) i dlaczego?
  2. Jakie metryki zbierzesz, oprócz p95?
  3. Zapisz mierzalne kryterium jakości (ustalaj progi w kontekście projektu).
  4. Dodaj ryzyko do Risk Register: P, I, Score, reakcja i właściciel.

JAK ZOBACZYĆ PRAWDZIWE ZAPYTANIA W TaxLab?
  (1) Uruchom lokalnie: py -m uvicorn taxlab.ui_demo:app --port 8000
  (2) Zainstaluj opcjonalne Locust: py -m pip install locust
  (3) Skopiuj odkomentowany przykład z końca pliku do locustfile.py
  (4) Uruchom: py -m locust -f locustfile.py --host=http://127.0.0.1:8000
  (5) W interfejsie Locust ustaw małą liczbę użytkowników i obserwuj wyniki.

UWAGA: Locust wysyła HTTP; nie uruchamia przeglądarki. Testuj tylko własny
lokalny serwer. Jeśli chcesz badać POST /consultations, używaj unikalnych
terminów lub czystej bazy — inaczej oczekiwane 409 zafałszują profil błędów.
"""

# ============================================================================
# PRZYKŁADOWE ROZWIĄZANIE A — ANALIZA DECYZJI
# ============================================================================
# Wydajność: PASS (780 ms < 1000 ms).
# Odsetek błędów: PASS (0.2% < 1%).
# Dostępność kluczowej funkcji: FAIL (2% osób nie może zakończyć rezerwacji).
# Przykładowa decyzja: NO-GO — zablokowana krytyczna funkcja użytkownika.
# Zastrzeżenie: decyzja wymaga analizy krytyczności i właściwych wymogów
# dostępności; ewentualne obejście trzeba ocenić i świadomie zatwierdzić.
#
# Brakujące dane: przeglądarki i czytniki, kroki odtworzenia, wielkość próby,
# czy da się zarezerwować klawiaturą, skala problemu, obowiązujące wymagania.
#
# Działania:
# 1. Popraw etykiety, focus i obsługę komunikatów błędu formularza.
# 2. Przetestuj ponownie z użytkownikami czytnika / technologią asystującą.
# 3. Dopisz test regresji klawiatury oraz przegląd wymagań dostępności.
#
# Uzasadnienie: dwóch spełnionych KPI nie można uśredniać z krytyczną barierą.

# ============================================================================
# PRZYKŁADOWE ROZWIĄZANIE B — ANALIZA I KRYTERIUM
# ============================================================================
# Test: SOAK (długotrwały), np. 90 minut lub dłużej, przy realistycznym profilu
# GET /tax/scale (80%) i GET /health (20%). W normalnych warunkach użyj 50 VU.
# Metryki: RSS (MB) procesu, CPU%, p50/p95/p99, RPS, liczba i odsetek błędów,
# restartów oraz zmiana zużycia pamięci w czasie. Rejestruj np. co minutę.
# Kryterium przykładowe (po uzgodnieniu limitów):
#   „Po rozgrzaniu systemu w teście 90 min RSS nie przekroczy 500 MB,
#     nie rośnie stale w kolejnych próbkach, p95 <= 1 s i błędy HTTP < 1%”.
# 500 MB i 1 s to PRZYKŁADOWE progi projektowe, nie standard ani wynik TaxLab.
# Ryzyko R-NFR-01: wzrost RSS -> wyczerpanie RAM i restart procesu -> przerwa
# w obliczaniu PIT i rezerwacjach. P=3, I=4, Score=12 (ocena przykładowa).
# Reakcja: MITIGATE — analiza profili pamięci, limity, monitoring, regresja soak.
# Właściciel: zespół utrzymania / osoba odpowiedzialna za aplikację.
# Rosnący RSS to SYGNAŁ, nie dowód wycieku pamięci; wymagane dalsze badanie.

# ============================================================================
# OPCJONALNIE — LOKUST / LOCUST: KOD DO PLIKU locustfile.py
# ============================================================================
# from locust import HttpUser, task, between
#
# class TaxLabUser(HttpUser):
#     wait_time = between(2, 5)
#
#     @task(4)  # ok. 80% wywołań
#     def tax_preview(self):
#         self.client.get('/tax/scale', params={'base': '120001'})
#
#     @task(1)  # ok. 20% wywołań
#     def health(self):
#         self.client.get('/health')
#
# Uwaga: samo Locust mierzy m.in. RPS, latencje, błędy. RSS i CPU procesu
# Uvicorn trzeba zbierać osobno (np. Monitor zasobów / psutil / profiler).
