import networkx as nx
from neo4j import GraphDatabase
import path_engine as pe

GOOD = ["introduces", "extends_to", "contains"]

def load_clean():
    G = pe.load_graph("strong")
    G.remove_edges_from(list(G.edges))
    drv = GraphDatabase.driver(pe.URI, auth=pe.AUTH)
    with drv.session() as s:
        for r in s.run("MATCH (a:Concept)-[r:PRECEDES]->(b:Concept) "
                       "WHERE r.relation IN $g RETURN a.name AS a, b.name AS b", g=GOOD):
            G.add_edge(r["a"], r["b"])
    drv.close()
    return G

if __name__ == "__main__":
    Gs, Gc = pe.load_graph("strong"), load_clean()
    print("is DAG:", nx.is_directed_acyclic_graph(Gc), "| edges strong/clean:",
          Gs.number_of_edges(), Gc.number_of_edges())
    for t in ["Hadoop架构和核心组件", "云计算系统的任务调度", "OpenStack体系架构与核心组件"]:
        a, b = pe.plan(Gs, t, set()), pe.plan(Gc, t, set())
        print(f"{t}: strong {len(a)} items | cleaned {len(b)} items")
    t = "Hadoop架构和核心组件"
    print("\ncleaned path:", " > ".join(pe.plan(Gc, t, set())))
