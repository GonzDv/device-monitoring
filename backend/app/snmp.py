import asyncio

from pysnmp.hlapi.v3arch.asyncio import (
    CommunityData,
    ContextData,
    ObjectIdentity,
    ObjectType,
    SnmpEngine,
    UdpTransportTarget,
    get_cmd,
)


async def _snmp_get_async(
    host: str, community: str, oid: str, port: int = 161,
    timeout: int = 2, retries: int = 1,
) -> str:
    """Consulta UN OID a un equipo por SNMP v2c. Devuelve el valor como texto."""
    engine = SnmpEngine()
    transport = await UdpTransportTarget.create((host, port), timeout=timeout, retries=retries)

    error_indication, error_status, error_index, var_binds = await get_cmd(
        engine,
        CommunityData(community, mpModel=1),  # mpModel=1 = SNMP v2c
        transport,
        ContextData(),
        ObjectType(ObjectIdentity(oid)),
    )
    engine.close_dispatcher()

    if error_indication:                       # el equipo no respondió (timeout, red…)
        raise RuntimeError(str(error_indication))
    if error_status:                           # el equipo respondió con un error SNMP
        raise RuntimeError(error_status.prettyPrint())

    for var_bind in var_binds:                 # var_bind = (OID, valor)
        return var_bind[1].prettyPrint()
    return ""


def snmp_get(host: str, community: str, oid: str, port: int = 161) -> str:
    """Versión síncrona (bloqueante) para usar desde el resto del backend."""
    return asyncio.run(_snmp_get_async(host, community, oid, port))