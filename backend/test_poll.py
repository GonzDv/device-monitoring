from app.database import SessionLocal
from app.models import Device
from app.poller import poll_device

db = SessionLocal()
devices = db.query(Device).all()
for d in devices:
    poll_device(db, d)
    print(f"{d.name}: status={d.status}")
db.close()