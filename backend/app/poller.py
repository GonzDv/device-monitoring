from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Alert, Device, Metric
from app.snmp import snmp_get, snmp_walk, decode_snmp_text

# OIDs numéricos que guardaremos como serie temporal
SYS_UPTIME_OID = "1.3.6.1.2.1.1.3.0"
PAGE_COUNT_OID = "1.3.6.1.2.1.43.10.2.1.4"      # prtMarkerLifeCount
SUPPLY_DESC_OID = "1.3.6.1.2.1.43.11.1.1.6"     # descripción del consumible
SUPPLY_LEVEL_OID = "1.3.6.1.2.1.43.11.1.1.9"    # nivel actual
SUPPLY_MAX_OID = "1.3.6.1.2.1.43.11.1.1.8"      # capacidad máxima

SUPPLY_KEYWORDS = {
    "black": "black", "negro": "black",
    "cyan": "cyan", "cian": "cyan",
    "magenta": "magenta",
    "yellow": "yellow", "amarillo": "yellow",
    "waste": "waste", "residual": "waste",
}

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
        _resolve_active_alert(db, device, now)
        if device.device_type == "printer":
            poll_printer_extras(db, device, now)
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

def _supply_key(description: str) -> str:
    """Convierte la descripción del fabricante en una clave estándar."""
    text = description.lower()

    if "residual" in text or "waste" in text:
        return "waste"

    if "cyan" in text or "cian" in text:
        return "cyan"
    if "magenta" in text:
        return "magenta"
    if "yellow" in text or "amarillo" in text:
        return "yellow"
    if "black" in text or "negro" in text:
        return "black"

    if "toner" in text or "tóner" in text or "cartridge" in text or "cartucho" in text:
        return "black"

    return "other"

def poll_printer_extras(db: Session, device: Device, now: datetime) -> None:
    """Sondea contador de páginas y consumibles. Solo para impresoras."""
    # --- Contador de páginas (puede haber uno o varios índices) ---
    try:
        counters = snmp_walk(device.ip_address, device.snmp_community,
                            PAGE_COUNT_OID, device.snmp_port)
        total = sum(int(value) for _, value in counters)
        db.add(Metric(time=now, device_id=device.id,
                    metric_key="page_count", value=float(total)))
    except Exception:
        pass  # si no lo reporta, seguimos sin romper

    # --- Consumibles: descripción + nivel + capacidad ---
    try:
        descs = snmp_walk(device.ip_address, device.snmp_community,
                        SUPPLY_DESC_OID, device.snmp_port)
        levels = snmp_walk(device.ip_address, device.snmp_community,
                        SUPPLY_LEVEL_OID, device.snmp_port)
        maxes = snmp_walk(device.ip_address, device.snmp_community,
                        SUPPLY_MAX_OID, device.snmp_port)

        for i, (_, desc_value) in enumerate(descs):
            if i >= len(levels) or i >= len(maxes):
                break
            level = int(levels[i][1])
            maximum = int(maxes[i][1])
            if level < 0 or maximum <= 0:
                continue          
            pct = (level / maximum) * 100
            key = _supply_key(decode_snmp_text(desc_value))
            db.add(Metric(time=now, device_id=device.id,
                        metric_key=f"supply.{key}.pct", value=pct))
    except Exception:
        pass