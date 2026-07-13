from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey , String,  func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PingLog(Base):
    """Tabla mínima de prueba para validar la conexión y las migraciones."""
    __tablename__ = "ping_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

class Device(Base):
    """Un equipo monitoreable (impresora, switch, router, etc.)."""
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    ip_address: Mapped[str] = mapped_column(String(45))
    device_type: Mapped[str] = mapped_column(String(20))
    location: Mapped[str | None] = mapped_column(String(120))
    snmp_version: Mapped[str] = mapped_column(String(4), server_default="v2c")
    snmp_community: Mapped[str | None] = mapped_column(String(100))
    snmp_port: Mapped[int] = mapped_column(server_default="161")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    status: Mapped[str] = mapped_column(String(12), server_default="unknown")
    consecutive_failures: Mapped[int] = mapped_column(server_default="0")
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

class Metric(Base):
    """Una lectura numérica de un equipo en un momento dado (serie temporal)."""
    __tablename__ = "metrics"

    time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), primary_key=True
    )
    device_id: Mapped[int] = mapped_column(primary_key=True)
    metric_key: Mapped[str] = mapped_column(String(50), primary_key=True)
    value: Mapped[float] = mapped_column(Float)
    

class Alert(Base):
    """Una alerta generada por el sistema (p. ej. equipo caído)."""
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[int] = mapped_column(
        ForeignKey("devices.id", ondelete="CASCADE")
    )
    alert_type: Mapped[str] = mapped_column(String(30))
    severity: Mapped[str] = mapped_column(String(12), server_default="critical")
    message: Mapped[str] = mapped_column(String(255))
    state: Mapped[str] = mapped_column(String(12), server_default="active")
    opened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))