from neo4j import GraphDatabase
import psycopg

d = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "thesis12345"))
with d.session() as s:
    print("Neo4j:", s.run("RETURN 'ok' AS r").single()["r"])

with psycopg.connect("postgresql://thesis:thesis12345@localhost:5432/learning") as c:
    print("Postgres:", c.execute("SELECT 'ok'").fetchone()[0])
