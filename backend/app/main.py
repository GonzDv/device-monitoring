from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from contextlib import asynccontextmanager

from app.scheduler import scheduler, start_scheduler

from app.database import get_db
from app.models import Device, Metric, PingLog
from app.snmp import snmp_get
from app.schemas import DeviceCreate, DeviceRead, DeviceUpdate



@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()      # al arrancar la API
    yield
    scheduler.shutdown()   # al apagarla


app = FastAPI(
    title="DeviceMonitoring API",
    description="API del sistema de monitoreo de equipos vía SNMP.",
    version="0.1.0",
    lifespan=lifespan, 
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# OIDs estándar del grupo "system" (MIB-II) — sirven para cualquier equipo
SYSTEM_OIDS = {
    "sys_name": "1.3.6.1.2.1.1.5.0",
    "sys_descr": "1.3.6.1.2.1.1.1.0",
    "sys_uptime": "1.3.6.1.2.1.1.3.0",
    "sys_location": "1.3.6.1.2.1.1.6.0",
}


@app.get("/healthz")
def health_check():
    return {"status": "ok"}


@app.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    total = db.scalar(select(func.count()).select_from(PingLog))
    return {"db": "ok", "ping_log_rows": total}


@app.post("/devices", response_model=DeviceRead, status_code=201)
def create_device(payload: DeviceCreate, db: Session = Depends(get_db)):
    device = Device(
        name=payload.name,
        ip_address=str(payload.ip_address),
        device_type=payload.device_type.value,
        location=payload.location,
        snmp_version=payload.snmp_version.value,
        snmp_community=payload.snmp_community,
        snmp_port=payload.snmp_port,
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


@app.get("/devices", response_model=list[DeviceRead])
def list_devices(db: Session = Depends(get_db)):
    devices = db.scalars(select(Device).order_by(Device.created_at.desc())).all()
    return devices


@app.get("/devices/{device_id}/history")
def device_history(device_id: int, limit: int = 50, db: Session = Depends(get_db)):
    device = db.get(Device, device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")

    rows = db.execute(
        select(Metric)
        .where(Metric.device_id == device_id)
        .order_by(Metric.time.desc())
        .limit(limit)
    ).scalars().all()

    return [
        {"time": r.time, "metric_key": r.metric_key, "value": r.value}
        for r in rows
    ]

@app.patch("/devices/{device_id}", response_model=DeviceRead)
def update_device(device_id: int, payload: DeviceUpdate, db: Session = Depends(get_db)):
    device = db.get(Device, device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        if field == "ip_address" and value is not None:
            value = str(value)
        if field in ("device_type", "snmp_version") and value is not None:
            value = value.value
        setattr(device, field, value)

    db.commit()
    db.refresh(device)
    return device

@app.delete("/devices/{device_id}", status_code=204)
def delete_device(device_id: int, db: Session = Depends(get_db)):
    device = db.get(Device, device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    db.delete(device)
    db.commit()



@app.get("/devices/{device_id}/snmp")
def query_device_snmp(device_id: int, db: Session = Depends(get_db)):
    device = db.get(Device, device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    if not device.snmp_community:
        raise HTTPException(status_code=400, detail="El equipo no tiene community SNMP configurada")

    try:
        readout = {
            key: snmp_get(device.ip_address, device.snmp_community, oid, device.snmp_port)
            for key, oid in SYSTEM_OIDS.items()
        }
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=f"El equipo no respondió por SNMP: {exc}")

    return {
        "device_id": device.id,
        "name": device.name,
        "ip_address": device.ip_address,
        "snmp": readout,
    }