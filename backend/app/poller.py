from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import Device, Metric
from app.snmp import snmp_get

# OIDs numéricos que guardaremos como serie temporal
SYS_UPTIME_OID = "1.3.6.1.2.1.1.3.0"


def poll_device(db: Session, device: Device) -> None:
    """Sondea un equipo: consulta SNMP, guarda métricas y actualiza su estado."""
    now = datetime.now(timezone.utc)
    reachable = 0.0

    try:
        # sysUpTime viene como "Timeticks"; intentamos leerlo
        uptime_raw = snmp_get(
            device.ip_address, device.snmp_community, SYS_UPTIME_OID, device.snmp_port
        )
        reachable = 1.0
        # Guardamos el uptime en centésimas de segundo si se puede convertir a número
        uptime_ticks = _extract_number(uptime_raw)
        if uptime_ticks is not None:
            db.add(Metric(time=now, device_id=device.id,
                          metric_key="sys_uptime", value=uptime_ticks))
    except Exception:
        reachable = 0.0  # no respondió: lo marcamos como caído

    # Siempre guardamos si estaba alcanzable (1) o no (0)
    db.add(Metric(time=now, device_id=device.id,
                  metric_key="reachable", value=reachable))

    # Actualizamos el estado actual del equipo
    device.status = "up" if reachable == 1.0 else "down"
    if reachable == 1.0:
        device.last_seen_at = now

    db.commit()


def _extract_number(text: str | None) -> float | None:
    """Extrae el primer número de un texto SNMP (los Timeticks traen texto extra)."""
    if not text:
        return None
    import re
    match = re.search(r"\d+", text)
    return float(match.group()) if match else None