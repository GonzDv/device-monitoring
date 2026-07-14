import asyncio

from pysnmp.hlapi.v3arch.asyncio import (
    CommunityData,
    ContextData,
    ObjectIdentity,
    ObjectType,
    SnmpEngine,
    UdpTransportTarget,
    get_cmd,
    walk_cmd,
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

async def _snmp_walk_async(
    host: str, community: str, oid: str, port: int = 161,
    timeout: int = 2, retries: int = 1,
) -> list[tuple[str, object]]:
    """Recorre una rama de OIDs. Devuelve lista de (oid, valor_crudo)."""
    engine = SnmpEngine()
    transport = await UdpTransportTarget.create((host, port), timeout=timeout, retries=retries)
    results: list[tuple[str, object]] = []

    async for (error_indication, error_status, _, var_binds) in walk_cmd(
        engine,
        CommunityData(community, mpModel=1),
        transport,
        ContextData(),
        ObjectType(ObjectIdentity(oid)),
        lexicographicMode=False, 
    ):
        if error_indication:
            engine.close_dispatcher()
            raise RuntimeError(str(error_indication))
        if error_status:
            engine.close_dispatcher()
            raise RuntimeError(error_status.prettyPrint())
        for var_bind in var_binds:
            results.append((str(var_bind[0]), var_bind[1]))

    engine.close_dispatcher()
    return results


def snmp_walk(host: str, community: str, oid: str, port: int = 161) -> list[tuple[str, object]]:
    """Versión síncrona del walk."""
    return asyncio.run(_snmp_walk_async(host, community, oid, port))


def decode_snmp_text(value: object) -> str:
    """Convierte un valor SNMP de texto a str, tolerando acentos (Latin-1)."""
    try:
        return bytes(value).decode("latin-1").strip()
    except Exception:
        return str(value).strip()