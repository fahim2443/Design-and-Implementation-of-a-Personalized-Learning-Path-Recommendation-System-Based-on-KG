import pandas as pd
import networkx as nx
import path_engine as pe

def load_reviewed():
    G = pe.load_graph("strong")
    df = pd.read_csv("../docs/edge_review_all.csv", encoding="utf-8-sig")
    keep = df[df["ai_label"] == 1]
    G.remove_edges_from(list(G.edges))
    for _, r in keep.iterrows():
        G.add_edge(r.iloc[1], r.iloc[2])
    return G

if __name__ == "__main__":
    Gs, Gr = pe.load_graph("strong"), load_reviewed()
    print("DAG:", nx.is_directed_acyclic_graph(Gr), "| edges strong/reviewed:",
          Gs.number_of_edges(), Gr.number_of_edges())
    topics = [n for n in Gr if Gr.nodes[n]["type"] == "Topic" and Gr.nodes[n]["order"][0] != 99]
    lone = [t for t in topics if len(pe.plan(Gr, t, set())) == 1]
    print("topics with a 1-item path (disconnected):", len(lone), "of", len(topics))
    for t in ["Hadoop架构和核心组件", "云计算系统的任务调度", "OpenStack体系架构与核心组件", "Spark的架构与核心组件"]:
        print(f"{t}: strong {len(pe.plan(Gs, t, set()))} | reviewed {len(pe.plan(Gr, t, set()))}")
    print("\nHadoop path:", " > ".join(pe.plan(Gr, "Hadoop架构和核心组件", set())))
