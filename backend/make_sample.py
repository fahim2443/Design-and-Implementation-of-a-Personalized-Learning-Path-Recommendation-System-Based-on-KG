import csv, random
import networkx as nx
from neo4j import GraphDatabase
from path_engine import load_graph, NOT_STUDY

G = load_graph("strong")
G = G.subgraph([n for n in G if G.nodes[n]["cat"] not in NOT_STUDY])
H = nx.transitive_reduction(G)
edges = list(H.edges)
print("strong edges after reduction:", len(edges))

drv = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "thesis12345"))
rel = {}
with drv.session() as s:
    for r in s.run("MATCH (a:Concept)-[r:PRECEDES]->(b:Concept) WHERE r.strong "
                   "RETURN a.name AS a, b.name AS b, r.relation AS rel"):
        rel[(r["a"], r["b"])] = r["rel"]

random.Random(5).shuffle(edges)
sample = edges[:60]
with open("../docs/edge_validation.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["id", "learn_first (A)", "then (B)", "relation", "label"])
    for i, (a, b) in enumerate(sample, 1):
        w.writerow([i, a, b, rel.get((a, b), ""), ""])
print("wrote", len(sample), "rows to docs/edge_validation.csv")
