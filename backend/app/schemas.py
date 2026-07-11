from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, IPvAnyAddress

class DeviceType(str, Enum):
    printer = "printer"
    switch = "switch"
    router = "router"
    ups = "ups"
    server = "server"
    ap = "ap"
    other  = "other"
    
class SnmpVersion(str, Enum):
    v1 = "v1"
    v2c = "v2c"
    v3 = "v3"

class DeviceCreate(BaseModel):
    """Lo que la API acepta al crear un equipo."""
    name: str
    ip_address: IPvAnyAddress
    device_type: DeviceType
    location: str | None
    snmp_version: SnmpVersion = SnmpVersion.v2c
    snmp_community: str | None = None
    snmp_user: str | None = None
    snmp_port: int = 161

class DeviceRead(BaseModel):
    """Lo que la API devuelve de un equipo."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    ip_address: str
    device_type: str
    location: str | None
    snmp_version: str
    snmp_port: int
    created_at: datetime

class DeviceUpdate(BaseModel):
    """Lo que la API acepta al editar un equipo."""
    name: str | None = None
    ip_address: IPvAnyAddress | None = None
    device_type: DeviceType | None = None
    location: str | None = None
    snmp_version: SnmpVersion | None = None
    snmp_community: str | None = None



