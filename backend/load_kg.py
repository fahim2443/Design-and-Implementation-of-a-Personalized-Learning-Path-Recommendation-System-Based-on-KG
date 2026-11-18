import json, collections
import networkx as nx
from neo4j import GraphDatabase

D = "../data/import/"   # adjust if your files are in a subfolder
g = json.load(open(D + "prerequisite_graph.json", encoding="utf-8"))
names = {n["name"] for n in g["nodes"]}
bad = [e for e in g["edges"] if e["source"] not in names or e["target"] not in names]
print("nodes", len(g["nodes"]), "| edges", len(g["edges"]), "| dangling", len(bad))

G = nx.DiGraph(); G.add_nodes_from(names)
G.add_edges_from((e["source"], e["target"]) for e in g["edges"])
dag = nx.is_directed_acyclic_graph(G)
print("unique pairs", G.number_of_edges(), "| DAG:", dag)
if not dag:
    print("cycle:", nx.find_cycle(G)); raise SystemExit
print("after transitive reduction:", nx.transitive_reduction(G).number_of_edges())
print("by type:", collections.Counter(n["type"] for n in g["nodes"]))
print("by relation:", collections.Counter(e["relation"] for e in g["edges"]).most_common())

for n in g["nodes"]:
    c, s, p = n["first_seen"]
    n["chapter"], n["section"], n["pos"] = (c, s, p) if c != 999 else (None, None, None)
STRONG = ["introduces","reverse_introduces","contains","extends_to",
          "reverse_extends_to","reverse_provides","reverse_enables","reverse_implements"]

drv = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "thesis12345"))
with drv.session() as s:
    s.run("MATCH (n) DETACH DELETE n")   # wipes the 5-node practice graph
    s.run("CREATE CONSTRAINT concept_name IF NOT EXISTS FOR (c:Concept) REQUIRE c.name IS UNIQUE")
    s.run("""UNWIND $rows AS r MERGE (c:Concept {name:r.name})
             SET c.id=r.id, c.type=r.type, c.category=r.category, c.mentions=r.mentions,
                 c.chapter=r.chapter, c.section=r.section, c.pos=r.pos""", rows=g["nodes"])
    s.run("""UNWIND $rows AS e MATCH (a:Concept {name:e.source}) MATCH (b:Concept {name:e.target})
             MERGE (a)-[r:PRECEDES {relation:e.relation}]->(b)
             SET r.strong = e.relation IN $strong, r.reason = e.reason""",
          rows=g["edges"], strong=STRONG)
    print("loaded nodes:", s.run("MATCH (n:Concept) RETURN count(n) AS c").single()["c"],
          "| edges:", s.run("MATCH ()-[r:PRECEDES]->() RETURN count(r) AS c").single()["c"])
