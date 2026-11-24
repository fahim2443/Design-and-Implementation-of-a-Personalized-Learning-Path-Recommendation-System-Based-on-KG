import pandas as pd
import path_engine as pe

Gs = pe.load_graph("strong")
rej = pd.read_csv("../docs/rejected_edges.csv", encoding="utf-8-sig")
Gp = Gs.copy()
removed = 0
for _, r in rej.iterrows():
    a, b = r["learn_first (A)"], r["then (B)"]
    if Gp.has_edge(a, b):
        Gp.remove_edge(a, b); removed += 1
print("rejected edges removed:", removed)
for t in ["Hadoop架构和核心组件", "云计算系统的任务调度", "OpenStack体系架构与核心组件"]:
    print(f"{t}: strong {len(pe.plan(Gs, t, set()))} items | pruned {len(pe.plan(Gp, t, set()))} items")
