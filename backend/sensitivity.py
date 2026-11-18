import os, random, itertools, csv
import statistics as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from path_engine import load_graph, plan, linear_baseline
from simulate import make_student

TARGETS = ["Hadoop架构和核心组件", "云计算系统的任务调度", "OpenStack体系架构与核心组件"]

def run(G, path, known, target, rng, p_ok, p_missing, tries):
    known = set(known); minutes = 0
    for n in path:
        if n in known:
            continue
        ok = all(p in known for p in G.predecessors(n))
        minutes += G.nodes[n]["minutes"]
        for _ in range(tries):
            if rng.random() < (p_ok if ok else p_missing):
                known.add(n); break
            minutes += G.nodes[n]["minutes"] * 0.5
    return minutes, target in known

G = load_graph("strong")
rows = []
for p_ok, p_missing, tries in itertools.product([0.8, 0.9, 0.95], [0.2, 0.35, 0.5], [2, 3, 4]):
    saved, reach_s, reach_g = [], [], []
    for t in TARGETS:
        rng = random.Random(1)
        ms, mg, rs, rg = [], [], [], []
        for _ in range(300):
            known = make_student(G, rng); known.discard(t)
            a = run(G, linear_baseline(G, t, set()), known, t, rng, p_ok, p_missing, tries)
            b = run(G, plan(G, t, known), known, t, rng, p_ok, p_missing, tries)
            ms.append(a[0]); mg.append(b[0]); rs.append(a[1]); rg.append(b[1])
        saved.append(100 * (1 - st.mean(mg) / st.mean(ms)))
        reach_s.append(100 * sum(rs) / len(rs)); reach_g.append(100 * sum(rg) / len(rg))
    rows.append([p_ok, p_missing, tries, round(st.mean(saved), 1),
                 round(st.mean(reach_s), 1), round(st.mean(reach_g), 1)])

os.makedirs("../docs/figures", exist_ok=True)
with open("../docs/sensitivity_results.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["p_ok", "p_missing", "tries", "time_saved_%", "reach_slide_%", "reach_graph_%"])
    w.writerows(rows)

sv = [r[3] for r in rows]
gap = [r[5] - r[4] for r in rows]
print(f"{len(rows)} settings")
print(f"time saved: min {min(sv):.1f}% | mean {st.mean(sv):.1f}% | max {max(sv):.1f}%")
print(f"reach gap (graph - slide): min {min(gap):.1f} | mean {st.mean(gap):.1f} | max {max(gap):.1f} points")

fig, ax = plt.subplots(1, 2, figsize=(10, 4))
ax[0].hist(sv, bins=10); ax[0].set_xlabel("Time saved (%)"); ax[0].set_ylabel("Settings")
ax[0].set_title("Time saved across 27 settings")
ax[1].hist(gap, bins=10); ax[1].set_xlabel("Reached target: graph minus slide (points)")
ax[1].set_title("Difference in success rate")
plt.tight_layout(); plt.savefig("../docs/figures/fig_sensitivity.png", dpi=200)
print("saved docs/sensitivity_results.csv and docs/figures/fig_sensitivity.png")
