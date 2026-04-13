import asyncio
from pathlib import Path

from backend.graph.neo4j_client import neo4j_client


class SchemaManager:
    def __init__(self):
        self.schema_dir = (
            Path(__file__).parent.parent.parent / "docker" / "neo4j_setup" / "cypher"
        )

    async def run_schema(self, filename: str) -> None:
        cypher_file = self.schema_dir / filename

        if not cypher_file.exists():
            print(f"[WARNING] Schema file not found: {filename}")
            return

        with open(cypher_file, "r") as f:
            statements = f.read()

        for statement in statements.split(";"):
            statement = statement.strip()

            if statement and not statement.startswith("//"):
                try:
                    await neo4j_client.execute(statement)
                except Exception as e:
                    msg = str(e).lower()

                    if "already exists" in msg or "already been created" in msg:
                        print(f"[INFO] Already exists: {statement[:50]}")
                    else:
                        print(f"[ERROR] Failed: {statement[:100]} -> {e}")

        print(f"[INFO] Schema applied: {filename}")

    async def verify_schema(self) -> dict[str, bool]:
        checks = {}

        queries = {
            "host_constraints": "SHOW CONSTRAINTS WHERE entity = 'Host'",
            "attack_event_constraints": "SHOW CONSTRAINTS WHERE entity = 'AttackEvent'",
            "killchain_constraints": "SHOW CONSTRAINTS WHERE entity = 'KillChainStage'",
            "agent_action_constraints": "SHOW CONSTRAINTS WHERE entity = 'AgentAction'",
            "alert_constraints": "SHOW CONSTRAINTS WHERE entity = 'Alert'",
            "asset_constraints": "SHOW CONSTRAINTS WHERE entity = 'Asset'",
        }

        for name, query in queries.items():
            try:
                result = await neo4j_client.execute(query)
                checks[name] = bool(result)
            except Exception:
                checks[name] = False

        return checks

    async def full_init(self) -> None:
        print("[INFO] Schema initialization started")

        # ✅ FIX: connect is sync
        neo4j_client.connect()

        await self.run_schema("init_schema.cql")

        checks = await self.verify_schema()
        all_ok = all(checks.values())

        print(f"[INFO] Schema verification: {checks}")
        print(f"[INFO] Schema success: {all_ok}")

        if not all_ok:
            failed = [k for k, v in checks.items() if not v]
            print(f"[WARNING] Failed constraints: {failed}")


async def main():
    manager = SchemaManager()

    await manager.full_init()

    # ✅ proper async close
    await neo4j_client.close()


if __name__ == "__main__":
    asyncio.run(main())