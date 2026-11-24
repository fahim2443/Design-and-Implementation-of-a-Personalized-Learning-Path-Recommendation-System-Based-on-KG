import random, statistics as st
import path_engine as pe
from reviewed2 import load_reviewed2
from simulate import make_student
from sensitivity import run   # same learning model as before

TARGETS = ["Hadoop架构和核心组件", "云计算系统的任务调度",
           "OpenStack体系架构与核心组件", "Spark的架构与核心组件"]
Gs, Gr = pe.load_graph("strong"), load_reviewed2()
print("minutes are averages over 300 simulated students per target")
for t in TARGETS:
    rng = random.Random(1)
    out = {"slide order": [], "strong graph": [], "reviewed v2": []}
    for _ in range(300):
        known = make_student(Gs, rng); known.discard(t)
        for name, G, path in (("slide order", Gs, pe.linear_baseline(Gs, t, set())),
                              ("strong graph", Gs, pe.plan(Gs, t, known)),
                              ("reviewed v2", Gr, pe.plan(Gr, t, known))):
            out[name].append(run(G, path, known, t, rng, 0.9, 0.35, 3))
    print(t)
    for k, r in out.items():
        print(f"   {k:12}: minutes {st.mean(x[0] for x in r):6.0f} | "
              f"reached {100*sum(x[1] for x in r)/len(r):5.1f}%")
