from fastapi import FastAPI
from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import PingLog


app = FastAPI(
  title="Device Monitoring API",
  description="API for device monitoring through SNMP",
  version="0.1.0",
)

@app.get("/healthz")
def health_check():
  """Endpont de salud: confirma que la API esta activa"""
  return {"status": "ok"}

@app.get("/db-check")
def db_check(db: Session = Depends(get_db)):
  """Confirmas que la API puede consultar la base de datos."""
  total = db.scalar(select(func.count()).select_from(PingLog))
  return {"db": "ok", "ping_log_rows": total}