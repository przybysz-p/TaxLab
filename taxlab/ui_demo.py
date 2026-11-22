"""TaxLab: lokalny, demonstracyjny interfejs WWW do nauki testów UI/E2E.

Wykorzystuje istniejącą aplikację FastAPI i SQLite. Nie służy do produkcji:
X-User jest podawany przez formularz i NIE stanowi prawdziwego uwierzytelnienia.
Uruchom: py -m uvicorn taxlab.ui_demo:app --host 127.0.0.1 --port 8000
"""
import os
from pathlib import Path
from fastapi.responses import HTMLResponse
from .api import create_app

DB_PATH = Path(os.environ.get("TAXLAB_DB", "local_consultations.sqlite3"))
app = create_app(DB_PATH)

HTML = r'''<!doctype html>
<html lang="pl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TaxLab — demonstracja UI</title>
<style>
:root {font-family: system-ui,Segoe UI,Arial,sans-serif;color:#223044;background:#f3f6fa}
body{max-width:960px;margin:40px auto;padding:0 18px}header{margin-bottom:24px}
h1{font-size:2rem;margin:0 0 8px}p{line-height:1.5}main{display:grid;grid-template-columns:1fr 1fr;gap:18px}
section{background:white;border:1px solid #dde4ec;border-radius:14px;padding:24px;box-shadow:0 6px 22px #192b410d}
h2{font-size:1.2rem;margin-top:0}label{display:block;font-weight:650;margin-top:16px;font-size:0.94rem}
input{display:block;width:100%;box-sizing:border-box;padding:11px;margin-top:5px;border:1px solid #a9b5c2;border-radius:7px;font:inherit}
input:focus-visible,button:focus-visible{outline:3px solid #ef8b24;outline-offset:2px}
button{background:#e98019;color:white;font-weight:700;padding:12px 22px;border:0;border-radius:8px;font:inherit;margin-top:20px;cursor:pointer}
button:hover{background:#bf630c}[role=status]{min-height:28px;margin-top:16px;padding:10px;border-radius:6px;background:#f2f5f9}
small{color:#637082}.notice{font-size:0.9rem;color:#8a4a13}
@media(max-width:700px){main{grid-template-columns:1fr}}
</style></head><body>
<header><h1>TaxLab · demonstracja UI</h1>
<p>Kalkulator uproszczonego PIT oraz rezerwacja konsultacji. Formularze łączą się z istniejącym API FastAPI i bazą SQLite.</p>
<p class="notice">Środowisko dydaktyczne, tylko lokalnie. Pole „Klient” nie jest prawdziwym logowaniem.</p></header>
<main>
<section aria-labelledby="tax-title"><h2 id="tax-title">Oblicz PIT</h2>
<form id="tax-form"><label for="base">Podstawa PIT (PLN)</label><input id="base" name="base" value="120001" required>
<button type="submit">Oblicz PIT</button></form>
<div role="status" aria-label="Wynik podatku" id="tax-result" aria-live="polite">Brak obliczenia</div>
<small>Wyniki edukacyjne, nie służą do rozliczeń podatkowych.</small></section>
<section aria-labelledby="booking-title"><h2 id="booking-title">Zarezerwuj konsultację</h2>
<form id="booking-form">
<label for="client">Klient</label><input id="client" name="client" value="Jan" required>
<label for="accountant">Księgowa</label><input id="accountant" name="accountant" value="Anna" required>
<label for="slot">Termin (YYYY-MM-DD HH:00)</label><input id="slot" name="slot" value="2030-05-14 10:00" required>
<label for="request_key">Klucz żądania (opcjonalny)</label><input id="request_key" name="request_key">
<button type="submit">Zarezerwuj</button></form>
<div role="status" aria-label="Wynik rezerwacji" id="booking-result" aria-live="polite">Brak rezerwacji</div>
</section></main>
<script>
const taxForm=document.querySelector('#tax-form');
taxForm.addEventListener('submit', async event=>{
  event.preventDefault();
  const base=document.querySelector('#base').value;
  const out=document.querySelector('#tax-result'); out.textContent='Obliczam…';
  try {
    const res=await fetch('/tax/scale?'+new URLSearchParams({base}));
    const data=await res.json();
    out.textContent=res.ok ? `Podatek: ${data.estimated_tax} PLN (HTTP ${res.status})` : `Błąd HTTP ${res.status}: ${data.detail}`;
  }catch(e){out.textContent='Nie udało się połączyć z API: '+e.message;}
});
const bookingForm=document.querySelector('#booking-form');
bookingForm.addEventListener('submit', async event=>{
  event.preventDefault();
  const out=document.querySelector('#booking-result'); out.textContent='Rezerwuję…';
  const client=document.querySelector('#client').value;
  const request_key=document.querySelector('#request_key').value;
  const payload={accountant:document.querySelector('#accountant').value,slot:document.querySelector('#slot').value};
  if(request_key.trim()) payload.request_key=request_key;
  try {
    const res=await fetch('/consultations',{method:'POST',headers:{'Content-Type':'application/json','X-User':client},body:JSON.stringify(payload)});
    const data=await res.json();
    if(res.ok){out.textContent=`Potwierdzono: #${data.booking.id}, ${data.booking.client}, ${data.booking.slot} (HTTP ${res.status})`;}
    else {out.textContent=`Błąd HTTP ${res.status}: ${data.detail ?? 'Odrzucono żądanie'}`;}
  }catch(e){out.textContent='Nie udało się połączyć z API: '+e.message;}
});
</script></body></html>'''

@app.get('/', response_class=HTMLResponse, include_in_schema=False)
def demo_home():
    return HTMLResponse(HTML)
