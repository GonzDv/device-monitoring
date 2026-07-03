from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Device, PingLog
from app.schemas import DeviceCreate, DeviceRead

app = FastAPI(
    title="DeviceMonitoring API",
    description="API del sistema de monitoreo de equipos vía SNMP.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
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


@app.post("/devices", response_model=DeviceRead, status_code=201)
def create_device(payload: DeviceCreate, db: Session = Depends(get_db)):
  device = Device(
    name=payload.name,
    ip_address=str(payload.ip_address),
    device_type=payload.device_type.value,
    location=payload.location
  )
  db.add(device)
  db.commit()
  db.refresh(device)
  return device

@app.get("/devices", response_model=list[DeviceRead])
def list_devices(db: Session = Depends(get_db)):
  devices = db.scalars(select(Device).order_by(Device.created_at.desc())).all()
  return devices