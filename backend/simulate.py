import random, statistics as st
from path_engine import load_graph, plan, linear_baseline

def make_student(G, rng):
    """Hidden true knowledge: a random prefix of the course plus a few extras."""
    order = sorted(G.nodes, key=lambda n: G.nodes[n]["order"])
    k = rng.randint(0, len(order) // 3)
    known = set(order[:k])
    known |= set(rng.sample(order, rng.randint(0, 5)))
    return known

def run(G, path, known, target, rng, p_ok=0.9, p_missing=0.35):
    """Study items in order. Learning is likely if all prerequisites are known."""
    known = set(known); minutes = 0; fails = 0
    for n in path:
        if n in known:
            continue
        ok = all(p in known for p in G.predecessors(n))
        minutes += G.nodes[n]["minutes"]
        for attempt in range(3):                      # up to 3 tries per item
            if rng.random() < (p_ok if ok else p_missing):
                known.add(n)
                break
            fails += 1
            minutes += G.nodes[n]["minutes"] * 0.5   # re-study penalty
    return minutes, fails, target in known

def experiment(edge_set="strong", n_students=500, seed=1,
               targets=("Hadoop架构和核心组件", "云计算系统的任务调度",
                        "OpenStack体系架构与核心组件")):
    G = load_graph(edge_set); rng = random.Random(seed)
    print(f"\nEdge set: {edge_set} | students: {n_students}")
    for t in targets:
        res = {"slide order": [], "graph path": []}
        for _ in range(n_students):
            known = make_student(G, rng)
            known.discard(t)
            lin = linear_baseline(G, t, set())          # slide order does not know the student
            gph = plan(G, t, known)                     # graph path skips what is known
            for name, path in (("slide order", lin), ("graph path", gph)):
                res[name].append(run(G, path, known, t, rng))
        print(f"  Target: {t}")
        for name, r in res.items():
            print(f"    {name:11}: minutes {st.mean(x[0] for x in r):7.0f} | "
                  f"fails {st.mean(x[1] for x in r):4.1f} | "
                  f"reached target {100*sum(x[2] for x in r)/len(r):4.1f}%")

if __name__ == "__main__":
    for es in ("all", "strong"):
        experiment(es)
