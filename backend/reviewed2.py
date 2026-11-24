import pandas as pd
import path_engine as pe
from reviewed import load_reviewed

BASICS = {"云计算", "虚拟化", "虚拟机", "数据中心", "云数据中心", "分布式计算", "云服务"}
FIRST = "云计算的定义与特征"

def load_reviewed2():
    G = load_reviewed()
    df = pd.read_csv("../docs/edge_review_all.csv", encoding="utf-8-sig")
    zero = df[df["ai_label"] == 0]
    topics = [n for n in G if G.nodes[n]["type"] == "Topic" and G.nodes[n]["order"][0] != 99]
    for t in topics:
        if t == FIRST or G.in_degree(t) > 0:
            continue
        for _, r in zero[zero.iloc[:, 2] == t].iterrows():
            if r.iloc[1] in BASICS:
                G.add_edge(r.iloc[1], t)
    return G

if __name__ == "__main__":
    Gr = load_reviewed2()
    topics = [n for n in Gr if Gr.nodes[n]["type"] == "Topic" and Gr.nodes[n]["order"][0] != 99]
    lone = [t for t in topics if len(pe.plan(Gr, t, set())) == 1]
    print("edges:", Gr.number_of_edges(), "| still disconnected:", lone)
    for t in ["Hadoop架构和核心组件", "云计算系统的任务调度", "OpenStack体系架构与核心组件", "Spark的架构与核心组件", "仿真平台概览"]:
        print(f"{t}: {len(pe.plan(Gr, t, set()))} items")
