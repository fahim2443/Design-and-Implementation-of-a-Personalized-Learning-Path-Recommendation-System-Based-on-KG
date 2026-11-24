import pandas as pd
import path_engine as pe

G = pe.load_graph("strong")
df = pd.read_csv("../docs/edge_validation.csv", encoding="utf-8-sig")
df = df[df["relation"] == "reverse_introduces"]
for gap in (0, 1, 2, 3):
    keep = []
    for _, r in df.iterrows():
        a, b = r["learn_first (A)"], r["then (B)"]
        ca, cb = G.nodes[a]["order"][0], G.nodes[b]["order"][0]
        keep.append(ca != 99 and cb != 99 and abs(cb - ca) <= gap)
    k = df[keep]
    print(f"chapter gap <= {gap}: keeps {len(k)}/{len(df)} edges | "
          f"correct among kept {int(k['label'].sum())}/{len(k)} | "
          f"correct lost {int(df['label'].sum() - k['label'].sum())}")
