import random, statistics as st
import networkx as nx
import path_engine as pe
from reviewed2 import load_reviewed2
from simulate import make_student

P_OK, P_MISS, TRIES = 0.9, 0.35, 3
TARGETS = ["Hadoop架构和核心组件", "云计算系统的任务调度",
           "OpenStack体系架构与核心组件", "Spark的架构与核心组件"]
Gs, Gr = pe.load_graph("strong"), load_reviewed2()
NS = pe.NOT_STUDY

def ok(n, known):   # strict judge: prerequisites from the ORIGINAL strong graph
    return all(p in known or Gs.nodes[p]["cat"] in NS for p in Gs.predecessors(n))

def run(path, known, t, rng):
    known = set(known); minutes = 0
    for n in path:
        if n in known: continue
        m = Gs.nodes[n]["minutes"]
        for a in range(TRIES):
            minutes += m if a == 0 else 0.5 * m
            if rng.random() < (P_OK if ok(n, known) else P_MISS):
                known.add(n); break
    return minutes, t in known

print("Strict judge = original strong graph. 300 students per target.")
for t in TARGETS:
    rng = random.Random(1)
    need = {n for n in nx.ancestors(Gs, t) if Gs.nodes[n]["cat"] not in NS}
    res = {"slide order": [], "strong graph": [], "reviewed v2": []}
    for _ in range(300):
        known = make_student(Gs, rng); known.discard(t)
        for name, path in (("slide order", pe.linear_baseline(Gs, t, set())),
                           ("strong graph", pe.plan(Gs, t, known)),
                           ("reviewed v2", pe.plan(Gr, t, known))):
            m, reached = run(path, known, t, rng)
            gap = len(need - known - set(path))
            res[name].append((m, reached, gap))
    print(t)
    for k, r in res.items():
        print(f"   {k:12}: minutes {st.mean(x[0] for x in r):6.0f} | reached "
              f"{100*sum(x[1] for x in r)/len(r):5.1f}% | skipped-needed items {st.mean(x[2] for x in r):4.1f}")
