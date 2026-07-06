from datetime import datetime

from sqlalchemy import DateTime, String,  func
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