import random, statistics as st
from collections import defaultdict
from path_engine import load_graph, plan, NOT_STUDY
from quiz import run_quiz
from simulate import make_student

P_OK, P_MISS = 0.9, 0.35
REVIEW = 0.2   # assumption: reviewing something already known costs 20% of its time
TARGETS = ["Hadoop架构和核心组件", "云计算系统的任务调度", "OpenStack体系架构与核心组件"]

def attempt(G, n, truth, rng):
    ok = all(p in truth or G.nodes[p]["cat"] in NOT_STUDY for p in G.predecessors(n))
    return rng.random() < (P_OK if ok else P_MISS)

def static(G, t, belief, truth, rng):
    truth = set(truth); minutes = 0
    for n in plan(G, t, belief):
        m = G.nodes[n]["minutes"]
        if n in truth:
            minutes += REVIEW * m; continue
        for a in range(3):
            minutes += m if a == 0 else 0.5 * m
            if attempt(G, n, truth, rng):
                truth.add(n); break
    return minutes, t in truth

def dynamic(G, t, belief, truth, rng):
    truth = set(truth); B = set(belief); verified = set()
    attempts = defaultdict(int); minutes = 0
    for _ in range(400):
        if t in B: break
        n = next((x for x in plan(G, t, B) if x not in B), None)
        if n is None: break
        m = G.nodes[n]["minutes"]
        if n in truth:
            minutes += REVIEW * m; B.add(n); verified.add(n); continue
        minutes += m if attempts[n] == 0 else 0.5 * m
        attempts[n] += 1
        if attempt(G, n, truth, rng):
            truth.add(n); B.add(n); verified.add(n)
        else:
            for p in G.predecessors(n):          # distrust guessed prerequisites
                if p in B and p not in verified: B.discard(p)
            if attempts[n] >= 3: B.add(n)        # give up on this item
    return minutes, t in truth

G = load_graph("strong")
print("Start from a noisy quiz result. Same students for both methods.")
for budget in (4, 8):
    res = {"static": [], "dynamic": []}
    for t in TARGETS:
        rng = random.Random(11)
        for _ in range(200):
            truth = make_student(G, rng); truth.discard(t)
            belief, _ = run_quiz(G, t, truth, budget, "graph", rng)
            res["static"].append(static(G, t, belief, truth, random.Random(rng.random())))
            res["dynamic"].append(dynamic(G, t, belief, truth, random.Random(rng.random())))
    for k, r in res.items():
        print(f"  quiz {budget:2} questions | {k:7}: minutes {st.mean(x[0] for x in r):6.0f} | "
              f"reached target {100*sum(x[1] for x in r)/len(r):5.1f}%")
