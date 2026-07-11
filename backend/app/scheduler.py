from apscheduler.schedulers.background import BackgroundScheduler

from app.database import SessionLocal
from app.models import Device
from app.poller import poll_device

POLL_INTERVAL_SECONDS = 60


def poll_all_devices() -> None:
    """Sondea todos los equipos. Esto es lo que corre en cada ciclo."""
    db = SessionLocal()
    try:
        devices = db.query(Device).all()
        for device in devices:
            if not device.snmp_community:
                continue  # sin community no podemos consultarlo, lo saltamos
            try:
                poll_device(db, device)
            except Exception as exc:
                # que un equipo falle no debe frenar a los demás
                print(f"Error sondeando {device.name}: {exc}")
    finally:
        db.close()


scheduler = BackgroundScheduler()


def start_scheduler() -> None:
    scheduler.add_job(
        poll_all_devices,
        trigger="interval",
        seconds=POLL_INTERVAL_SECONDS,
        id="poll_all_devices",
        replace_existing=True,
    )
    scheduler.start()