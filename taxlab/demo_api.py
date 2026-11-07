"""Local demo API only. `python -m uvicorn taxlab.demo_api:app --reload`."""
from pathlib import Path
from .api import create_app
app=create_app(Path('local_consultations.sqlite3'))
