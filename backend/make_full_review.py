import csv
import pandas as pd
import networkx as nx
from neo4j import GraphDatabase
from path_engine import load_graph, NOT_STUDY

G = load_graph("strong")
G = G.subgraph([n for n in G if G.nodes[n]["cat"] not in NOT_STUDY])
edges = sorted(nx.transitive_reduction(G).edges)

drv = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "thesis12345"))
rel = {}
with drv.session() as s:
    for r in s.run("MATCH (a:Concept)-[r:PRECEDES]->(b:Concept) WHERE r.strong "
                   "RETURN a.name AS a, b.name AS b, r.relation AS rel"):
        rel[(r["a"], r["b"])] = r["rel"]

done = pd.read_csv("../docs/edge_validation.csv", encoding="utf-8-sig")
known = {(r["learn_first (A)"], r["then (B)"]): int(r["label"]) for _, r in done.iterrows()}

rows = []
for i, (a, b) in enumerate(edges, 1):
    rows.append([i, a, b, rel.get((a, b), ""), known.get((a, b), ""), ""])

with open("../docs/edge_review_all.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["id", "先学 A (learn first)", "后学 B (then)", "relation",
                "ai_label", "teacher_label (1=必须先学 / 0=不是)"])
    w.writerows(rows)

todo = [r for r in rows if r[4] == ""]
with open("../docs/edges_to_label.txt", "w", encoding="utf-8") as f:
    for r in todo:
        f.write(f"{r[0]},{r[1]},{r[2]},{r[3]}\n")
print("total edges:", len(rows), "| already labeled:", len(rows) - len(todo),
      "| to label:", len(todo))
