import sys
import networkx as nx
from neo4j import GraphDatabase

URI, AUTH = "bolt://localhost:7687", ("neo4j", "thesis12345")

def load_graph(edge_set="all"):
    """edge_set: 'all' uses every arrow, 'strong' uses only strong arrows."""
    G = nx.DiGraph()
    drv = GraphDatabase.driver(URI, auth=AUTH)
    with drv.session() as s:
        for r in s.run("MATCH (c:Concept) RETURN c.name AS n, c.type AS t, "
                       "c.chapter AS ch, c.section AS sec, c.pos AS pos"):
            ch = r["ch"] if r["ch"] is not None else 99
            sec = r["sec"] if r["sec"] is not None else 99
            pos = r["pos"] if r["pos"] is not None else 99
            G.add_node(r["n"], type=r["t"], order=(ch, sec, pos),
                       diff=estimate_difficulty(r["t"], ch))
            G.nodes[r["n"]]["minutes"] = estimate_minutes(r["t"], G.nodes[r["n"]]["diff"])
        for r in s.run("MATCH (a:Concept)-[r:PRECEDES]->(b:Concept) "
                       "RETURN a.name AS a, b.name AS b, r.strong AS strong"):
            if edge_set == "strong" and not r["strong"]:
                continue
            G.add_edge(r["a"], r["b"])
    drv.close()
    return G

# ASSUMPTION: no real difficulty data exists, so we estimate it from node type
# and chapter (later chapters = more advanced). Say this in the thesis.
def estimate_difficulty(node_type, chapter):
    base = {"Topic": 3, "Concept": 2, "ExtendedConcept": 2}.get(node_type, 2)
    if chapter != 99 and chapter >= 6:
        base += 1
    return max(1, min(5, base))

def estimate_minutes(node_type, diff):
    base = {"Topic": 60, "Concept": 25, "ExtendedConcept": 15}.get(node_type, 20)
    return round(base * (0.8 + 0.1 * diff))

def plan(G, target, mastered):
    """Walk backwards from the target, stop at anything already mastered."""
    needed, stack = {target}, [target]
    while stack:
        n = stack.pop()
        for p in G.predecessors(n):
            if p in mastered or p in needed:
                continue
            needed.add(p)
            stack.append(p)
    sub = G.subgraph(needed)
    # topological sort; when several are allowed, easiest first, then course order
    return list(nx.lexicographical_topological_sort(
        sub, key=lambda n: (G.nodes[n]["diff"], G.nodes[n]["order"])))

def linear_baseline(G, target, mastered):
    """Normal course order: everything up to the target, skipping mastered."""
    t_order = G.nodes[target]["order"]
    items = [n for n in G.nodes if G.nodes[n]["order"] <= t_order and n not in mastered]
    return sorted(items, key=lambda n: G.nodes[n]["order"])

def report(target, mastered):
    print(f"\nTARGET: {target} | mastered: {sorted(mastered) or 'nothing'}")
    for edge_set in ("all", "strong"):
        G = load_graph(edge_set)
        if target not in G:
            print("  target not found in graph"); return
        path = plan(G, target, mastered)
        base = linear_baseline(G, target, mastered)
        mins = sum(G.nodes[n]["minutes"] for n in path)
        bmins = sum(G.nodes[n]["minutes"] for n in base)
        print(f"  [{edge_set:6}] graph path: {len(path):3} items, ~{mins} min"
              f"  |  linear order: {len(base):3} items, ~{bmins} min")
        if edge_set == "strong":
            print("  Strong-edge path (first 25):")
            for i, n in enumerate(path[:25], 1):
                print(f"    {i:2}. {n}  [{G.nodes[n]['type']}, diff {G.nodes[n]['diff']}]")

if __name__ == "__main__":
    targets = [sys.argv[1]] if len(sys.argv) > 1 else [
        "Hadoop架构和核心组件", "云计算系统的任务调度", "OpenStack体系架构与核心组件"]
    mastered = set(sys.argv[2].split(",")) if len(sys.argv) > 2 else set()
    for t in targets:
        report(t, mastered)
