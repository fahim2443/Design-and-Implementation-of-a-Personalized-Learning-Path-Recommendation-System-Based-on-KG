import random, statistics as st
import networkx as nx
from path_engine import load_graph, plan
from simulate import make_student

SLIP, GUESS = 0.10, 0.20   # assumptions, state them in the thesis

def caches(G, scope):
    anc = {n: nx.ancestors(G, n) & scope for n in scope}
    desc = {n: nx.descendants(G, n) & scope for n in scope}
    return anc, desc

def pick_question(scope, known, unknown, anc, desc, mode, rng):
    left = list(scope - known - unknown)
    if not left:
        return None
    if mode == "random":
        return rng.choice(left)
    def score(n):
        a = len(anc[n] - known); d = len(desc[n] - unknown)
        return (min(a, d), a + d)
    return max(left, key=score)

def update(n, correct, scope, known, unknown, anc, desc):
    if correct:
        new = anc[n] | {n}
        known |= new; unknown -= new
    else:
        new = desc[n] | {n}
        unknown |= new; known -= new

def run_quiz(G, target, true_known, budget, mode, rng):
    scope = nx.ancestors(G, target) | {target}
    anc, desc = caches(G, scope)
    known, unknown = set(), set()
    for _ in range(budget):
        q = pick_question(scope, known, unknown, anc, desc, mode, rng)
        if q is None:
            break
        truth = q in true_known
        correct = rng.random() < ((1 - SLIP) if truth else GUESS)
        update(q, correct, scope, known, unknown, anc, desc)
    known.discard(target)
    return known, scope

if __name__ == "__main__":
    G = load_graph("strong")
    targets = ["Hadoop架构和核心组件", "云计算系统的任务调度", "OpenStack体系架构与核心组件"]
    print("budget 0 = no quiz (system assumes the student knows nothing)")
    for budget in (0, 4, 8, 12):
        for mode in (("graph",) if budget == 0 else ("graph", "random")):
            acc, wrong, unnec, ratio = [], [], [], []
            for t in targets:
                rng = random.Random(7)
                for _ in range(200):
                    true_known = make_student(G, rng); true_known.discard(t)
                    inf, scope = run_quiz(G, t, true_known, budget, mode, rng)
                    tk = true_known & scope
                    acc.append(100 * sum((n in inf) == (n in tk) for n in scope) / len(scope))
                    wrong.append(len(inf - tk)); unnec.append(len(tk - inf))
                    ratio.append(len(plan(G, t, inf)) / max(1, len(plan(G, t, true_known))))
            print(f"budget {budget:2} {mode:6}: accuracy {st.mean(acc):5.1f}% | "
                  f"wrongly skipped {st.mean(wrong):4.1f} | unnecessary {st.mean(unnec):4.1f} | "
                  f"path length vs ideal {st.mean(ratio):4.2f}x")
