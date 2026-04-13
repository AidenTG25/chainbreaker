from backend.graph.neo4j_client import neo4j_client
from backend.utils.logger import setup_logger

logger = setup_logger("host_manager")


async def upsert_hosts(ips: list[str]) -> int:
    tasks = [neo4j_client.upsert_host(ip, ip, "unknown") for ip in ips]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    success_count = sum(1 for r in results if not isinstance(r, Exception))
    logger.info("hosts_upserted", total=len(ips), success=success_count)
    return success_count


async def update_host_role(ip: str, role: str) -> None:
    query = "MATCH (h:Host {ip: $ip}) SET h.role = $role, h.last_seen = datetime()"
    await neo4j_client.execute(query, {"ip": ip, "role": role})


async def get_all_hosts() -> list[dict]:
    query = """
    MATCH (h:Host)
    OPTIONAL MATCH (h)-[:COMMUNICATES_WITH]->(h2:Host)
    RETURN h.ip AS ip, h.hostname AS hostname, h.role AS role,
           h.compromise_status AS status, h.first_seen AS first_seen,
           h.last_seen AS last_seen, count(DISTINCT h2) AS connected_peers
    ORDER BY h.last_seen DESC
    """
    return await neo4j_client.execute(query)


async def get_host_by_ip(ip: str) -> dict | None:
    query = """
    MATCH (h:Host {ip: $ip})
    OPTIONAL MATCH (e:AttackEvent)-[:ON_HOST]->(h)
    OPTIONAL MATCH (k:KillChainStage)-[:ON_HOST]->(h)
    RETURN h, collect(DISTINCT properties(e)) AS events, collect(DISTINCT properties(k)) AS stages
    LIMIT 1
    """
    results = await neo4j_client.execute(query, {"ip": ip})
    return results[0] if results else None
