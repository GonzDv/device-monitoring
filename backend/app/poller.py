from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Alert, Device, Metric
from app.snmp import snmp_get

# OIDs numéricos que guardaremos como serie temporal
SYS_UPTIME_OID = "1.3.6.1.2.1.1.3.0"
FAILURE_THRESHOLD = 3

def poll_device(db: Session, device: Device) -> None:
    """Sondea un equipo, guarda métricas, actualiza estado y gestiona alertas."""
    now = datetime.now(timezone.utc)
    reachable = 0.0

    try:
        uptime_raw = snmp_get(
            device.ip_address, device.snmp_community, SYS_UPTIME_OID, device.snmp_port
        )
        reachable = 1.0
        uptime_ticks = _extract_number(uptime_raw)
        if uptime_ticks is not None:
            db.add(Metric(time=now, device_id=device.id,
                metric_key="sys_uptime", value=uptime_ticks))
    except Exception:
        reachable = 0.0

    db.add(Metric(time=now, device_id=device.id,
                metric_key="reachable", value=reachable))

    if reachable == 1.0:
        # --- El equipo respondió ---
        device.status = "up"
        device.last_seen_at = now
        device.consecutive_failures = 0
        _resolve_active_alert(db, device, now)   # si tenía una alerta, se resuelve
    else:
        # --- El equipo no respondió ---
        device.status = "down"
        device.consecutive_failures += 1
        if device.consecutive_failures >= FAILURE_THRESHOLD:
            _open_alert_if_needed(db, device, now)

    db.commit()


def _open_alert_if_needed(db: Session, device: Device, now: datetime) -> None:
    """Abre una alerta de 'equipo caído' solo si no hay ya una activa (deduplicación)."""
    existing = db.execute(
        select(Alert).where(
            Alert.device_id == device.id,
            Alert.alert_type == "device_down",
            Alert.state == "active",
        )
    ).scalar_one_or_none()

    if existing is None:   # no hay alerta activa -> creamos una
        db.add(Alert(
            device_id=device.id,
            alert_type="device_down",
            severity="critical",
            message=f"{device.name} no responde por SNMP",
            state="active",
            opened_at=now,
        ))

def _resolve_active_alert(db: Session, device: Device, now: datetime) -> None:
    """Si el equipo tenía una alerta activa de caída, la marca como resuelta."""
    active = db.execute(
        select(Alert).where(
            Alert.device_id == device.id,
            Alert.alert_type == "device_down",
            Alert.state == "active",
        )
    ).scalar_one_or_none()

    if active is not None:
        active.state = "resolved"
        active.resolved_at = now


def _extract_number(text: str | None) -> float | None:
    """Extrae el primer número de un texto SNMP (los Timeticks traen texto extra)."""
    if not text:
        return None
    import re
    match = re.search(r"\d+", text)
    return float(match.group()) if match else None