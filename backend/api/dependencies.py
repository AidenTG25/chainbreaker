from backend.graph.neo4j_client import neo4j_client

async def get_neo4j_client():
    neo4j_client.connect()
    return neo4j_client