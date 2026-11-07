"""Tiny FastAPI app: tax preview and consultation booking (demo, not production auth)."""
from pathlib import Path
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from .calculator import annual_scale_pit
from .consultations import (
    init_db, book, get_booking, cancel,
    SlotBusy, RequestConflict, BookingNotFound, PermissionDenied,
)

class BookingRequest(BaseModel):
    accountant: str = Field(min_length=1)
    slot: str = Field(min_length=1)
    request_key: str | None = None


def create_app(database_path):
    path=Path(database_path)
    init_db(path)
    app=FastAPI(title='TaxLab API', version='2.0')

    def user_required(user):
        if user is None or not user.strip():
            raise HTTPException(401, 'X-User wymagany (wyłącznie demonstracja)')
        return user

    @app.get('/health')
    def health():
        return {'status':'ok'}

    @app.get('/tax/scale')
    def tax_scale(base: str):
        try:
            return {'base':base, 'estimated_tax':str(annual_scale_pit(base))}
        except ValueError as exc:
            raise HTTPException(422,str(exc)) from exc

    @app.post('/consultations')
    def reserve(payload: BookingRequest, x_user: str | None=Header(default=None, alias='X-User')):
        user=user_required(x_user)
        try:
            item,replayed=book(path,payload.accountant,user,payload.slot,payload.request_key)
        except ValueError as exc:
            raise HTTPException(422,str(exc)) from exc
        except (SlotBusy,RequestConflict) as exc:
            raise HTTPException(409,str(exc)) from exc
        return JSONResponse(status_code=200 if replayed else 201,
                            content={'booking':item,'replayed':replayed})

    @app.get('/consultations/{booking_id}')
    def details(booking_id: int, x_user: str | None=Header(default=None,alias='X-User')):
        user=user_required(x_user)
        try: item=get_booking(path,booking_id)
        except BookingNotFound as exc: raise HTTPException(404,str(exc)) from exc
        if item['client'] != user: raise HTTPException(403,'Brak uprawnien')
        return {'booking':item}

    @app.delete('/consultations/{booking_id}')
    def remove(booking_id: int, x_user: str | None=Header(default=None,alias='X-User')):
        user=user_required(x_user)
        try: item=cancel(path,booking_id,user)
        except BookingNotFound as exc: raise HTTPException(404,str(exc)) from exc
        except PermissionDenied as exc: raise HTTPException(403,str(exc)) from exc
        return {'booking':item}
    return app
