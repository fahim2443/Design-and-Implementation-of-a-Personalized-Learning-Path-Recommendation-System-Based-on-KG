import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from path_engine import load_graph, plan, linear_baseline
import networkx as nx

os.makedirs("../docs/figures", exist_ok=True)
plt.rcParams["font.sans-serif"] = ["Arial Unicode MS", "PingFang SC", "Heiti SC"]
plt.rcParams["axes.unicode_minus"] = False

targets = ["Hadoop架构和核心组件", "云计算系统的任务调度", "OpenStack体系架构与核心组件"]
labels = ["Hadoop architecture", "Task scheduling", "OpenStack architecture"]

Gall, Gstr = load_graph("all"), load_graph("strong")
slide, allp, strong = [], [], []
for t in targets:
    slide.append(len(linear_baseline(Gall, t, set())))
    allp.append(len(plan(Gall, t, set())))
    strong.append(len(plan(Gstr, t, set())))
    anc = len(nx.ancestors(Gall, t))
    print(f"{t}: {anc} raw ancestors (all arrows, before any filtering)")

# Figure 1: number of study items per method
x = range(len(targets)); w = 0.27
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.bar([i - w for i in x], slide, w, label="Slide order")
ax.bar(list(x), allp, w, label="Graph path (all edges)")
ax.bar([i + w for i in x], strong, w, label="Graph path (strong edges)")
for i in x:
    for off, v in ((-w, slide[i]), (0, allp[i]), (w, strong[i])):
        ax.text(i + off, v + 1, str(v), ha="center", fontsize=9)
ax.set_xticks(list(x)); ax.set_xticklabels(labels)
ax.set_ylabel("Items to study"); ax.legend()
ax.set_title("Study items needed to reach each target")
plt.tight_layout(); plt.savefig("../docs/figures/fig_path_comparison.png", dpi=200)

# Table: first 15 prerequisites of Spark architecture (the "61 rows" problem)
t = "Spark的架构与核心组件"
anc = sorted(nx.ancestors(Gall, t))
print(f"\n{t} has {len(anc)} ancestors in the raw graph")
fig, ax = plt.subplots(figsize=(8, 5)); ax.axis("off")
rows = [[i + 1, n, Gall.nodes[n]["type"]] for i, n in enumerate(anc[:15])]
rows.append(["...", f"+ {len(anc) - 15} more", ""])
tbl = ax.table(cellText=rows, colLabels=["#", "Prerequisite", "Type"], loc="center")
tbl.auto_set_font_size(False); tbl.set_fontsize(10); tbl.scale(1, 1.4)
ax.set_title(f"Raw prerequisites of Spark architecture: {len(anc)} items", pad=10)
plt.savefig("../docs/figures/fig_spark_raw_prereqs.png", dpi=200, bbox_inches="tight")
print("saved figures to docs/figures/")
