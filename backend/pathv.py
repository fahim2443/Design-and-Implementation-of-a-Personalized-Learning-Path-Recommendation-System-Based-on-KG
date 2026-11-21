import networkx as nx
from path_engine import NOT_STUDY

TYPE_RANK = {"Topic": 0, "Concept": 1}

def closure(G, target, mastered):
    needed, stack = {target}, [target]
    while stack:
        n = stack.pop()
        for p in G.predecessors(n):
            if p not in mastered and p not in needed:
                needed.add(p); stack.append(p)
    return needed

def plan_variant(G, target, mastered, variant="v1"):
    """v1 = course order. v2 = global hubs first. v3 = hubs for THIS target first."""
    sub = G.subgraph(closure(G, target, mastered))
    N = G.nodes
    if variant == "v1":
        key = lambda n: (N[n]["order"][0], N[n]["order"][1],
                         TYPE_RANK.get(N[n]["type"], 2), N[n]["diff"], N[n]["order"][2])
    else:
        if variant == "v2":
            pr = nx.pagerank(G.reverse(copy=True))              # whole course
        else:
            pr = nx.pagerank(sub.reverse(copy=True), personalization={target: 1.0})
        key = lambda n: (-round(pr.get(n, 0), 6), N[n]["order"])
    ordered = nx.lexicographical_topological_sort(sub, key=key)
    return [n for n in ordered if N[n]["cat"] not in NOT_STUDY or n == target]
