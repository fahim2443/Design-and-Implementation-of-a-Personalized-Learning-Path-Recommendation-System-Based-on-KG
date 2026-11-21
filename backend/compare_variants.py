import random, statistics as st
import networkx as nx
from path_engine import load_graph, NOT_STUDY
from pathv import plan_variant, closure
from simulate import make_student

P_OK, P_MISS, TRIES = 0.9, 0.35, 3
TARGETS = ["Hadoop架构和核心组件", "云计算系统的任务调度", "OpenStack体系架构与核心组件"]

def progress(G, path, truth, rng, cutoff, imp):
    known = set(truth); minutes = 0; done = 0; imp_done = 0
    for n in path:
        if n in known: continue
        m = G.nodes[n]["minutes"]; learned = False
        for a in range(TRIES):
            cost = m if a == 0 else 0.5 * m
            if minutes + cost > cutoff: return done, imp_done
            minutes += cost
            ok = all(p in known or G.nodes[p]["cat"] in NOT_STUDY for p in G.predecessors(n))
            if rng.random() < (P_OK if ok else P_MISS):
                known.add(n); learned = True; break
        if learned: done += 1; imp_done += imp[n]
    return done, imp_done

G = load_graph("strong")
t0 = TARGETS[0]
for v in ("v1", "v2", "v3"):
    print(f"\nFirst 12 items, {v}, target {t0}:")
    print("  " + " > ".join(plan_variant(G, t0, set(), v)[:12]))

print("\nProgress when only 50% of the study time is available (300 students per target)")
for v in ("v1", "v2", "v3"):
    frac, impf = [], []
    for t in TARGETS:
        rng = random.Random(3)
        for _ in range(300):
            truth = make_student(G, rng); truth.discard(t)
            base = plan_variant(G, t, truth, "v1")
            nodes = [n for n in base]
            sub = G.subgraph(closure(G, t, truth))
            imp = {n: 1 + len(nx.descendants(sub, n)) for n in sub}
            cutoff = 0.5 * sum(G.nodes[n]["minutes"] for n in nodes)
            path = plan_variant(G, t, truth, v)
            d, i = progress(G, path, truth, rng, cutoff, imp)
            frac.append(100 * d / max(1, len(nodes)))
            impf.append(100 * i / max(1, sum(imp[n] for n in nodes if n in imp)))
    print(f"  {v}: items mastered {st.mean(frac):5.1f}% | importance mastered {st.mean(impf):5.1f}%")
