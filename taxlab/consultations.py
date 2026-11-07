"""Bookings for accountant consultations stored in SQLite.

Demo assumptions: fixed one-hour slots, local Warsaw wall time, no payments or real login.
The database (not the UI) guarantees a single confirmed booking per accountant/slot.
"""
import sqlite3
from datetime import datetime
from pathlib import Path

class SlotBusy(Exception): pass
class RequestConflict(Exception): pass
class BookingNotFound(Exception): pass
class PermissionDenied(Exception): pass


def connect(path):
    db = sqlite3.connect(str(path), timeout=15)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA busy_timeout = 15000')
    return db


def init_db(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with connect(path) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS consultations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            accountant TEXT NOT NULL,
            client TEXT NOT NULL,
            slot TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'confirmed',
            request_key TEXT UNIQUE,
            CHECK(status IN ('confirmed', 'cancelled'))
        )""")
        db.execute("""CREATE UNIQUE INDEX IF NOT EXISTS one_active_booking
            ON consultations(accountant, slot) WHERE status='confirmed' """)


def validate_slot(slot):
    try:
        dt = datetime.strptime(slot, '%Y-%m-%d %H:%M')
        if dt.strftime('%Y-%m-%d %H:%M') != slot or dt.minute != 0 or not 9 <= dt.hour <= 16:
            raise ValueError()
    except (TypeError, ValueError):
        raise ValueError('Slot: YYYY-MM-DD HH:00, godziny rozpoczecia 09-16')
    return slot


def book(path, accountant, client, slot, request_key=None, simulate_failure=False):
    """Atomic INSERT, idempotency-key and an optional fault injected by a test."""
    validate_slot(slot)
    if not isinstance(accountant,str) or not accountant.strip() or not isinstance(client,str) or not client.strip():
        raise ValueError('Wymagane accountant i client')
    db = connect(path)
    try:
        db.execute('BEGIN IMMEDIATE')
        if request_key:
            old = db.execute('SELECT * FROM consultations WHERE request_key=?', (request_key,)).fetchone()
            if old:
                if (old['accountant'], old['client'], old['slot']) != (accountant, client, slot):
                    raise RequestConflict('Ten sam klucz uzyty do innego zadania')
                db.commit()
                return dict(old), True
        try:
            cur=db.execute('INSERT INTO consultations(accountant,client,slot,request_key) VALUES(?,?,?,?)',
                           (accountant,client,slot,request_key))
        except sqlite3.IntegrityError as exc:
            raise SlotBusy('Termin jest zajety') from exc
        if simulate_failure:
            raise RuntimeError('Symulowana awaria przed COMMIT')
        booking=dict(db.execute('SELECT * FROM consultations WHERE id=?',(cur.lastrowid,)).fetchone())
        db.commit()
        return booking, False
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_booking(path, booking_id):
    with connect(path) as db:
        row=db.execute('SELECT * FROM consultations WHERE id=?', (booking_id,)).fetchone()
        if row is None: raise BookingNotFound('Rezerwacja nie istnieje')
        return dict(row)


def count_confirmed(path, accountant, slot):
    with connect(path) as db:
        return db.execute('SELECT COUNT(*) FROM consultations WHERE accountant=? AND slot=? AND status=?',
                          (accountant,slot,'confirmed')).fetchone()[0]


def cancel(path, booking_id, client):
    with connect(path) as db:
        db.execute('BEGIN IMMEDIATE')
        row=db.execute('SELECT * FROM consultations WHERE id=?',(booking_id,)).fetchone()
        if row is None: raise BookingNotFound('Nie znaleziono')
        if row['client'] != client: raise PermissionDenied('Brak uprawnien')
        db.execute('UPDATE consultations SET status=? WHERE id=?',('cancelled',booking_id))
        return dict(db.execute('SELECT * FROM consultations WHERE id=?',(booking_id,)).fetchone())
