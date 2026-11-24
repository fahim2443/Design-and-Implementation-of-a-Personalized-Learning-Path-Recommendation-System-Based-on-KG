import math
import pandas as pd

df = pd.read_csv("../docs/edge_validation.csv", encoding="utf-8-sig")
df = df[df["label"].isin([0, 1])].copy()
df["label"] = df["label"].astype(int)
n, k = len(df), int(df["label"].sum())

def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n)
    a = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - a) / d, (c + a) / d

lo, hi = wilson(k, n)
print(f"labeled {n} edges | real prerequisites {k} ({100*k/n:.0f}%)")
print(f"95% confidence interval: {100*lo:.0f}% to {100*hi:.0f}%")

nc = df[df["relation"] != "introduces"]
lo2, hi2 = wilson(int(nc["label"].sum()), len(nc))
print(f"excluding 'introduces' (containment): {int(nc['label'].sum())}/{len(nc)} "
      f"({100*nc['label'].mean():.0f}%), interval {100*lo2:.0f}% to {100*hi2:.0f}%")

print("\nBy relation type:")
for rel, g in df.groupby("relation"):
    print(f"  {rel:20} {int(g['label'].sum())}/{len(g)} correct")

print("\nRejected edges (label 0):")
for _, r in df[df["label"] == 0].iterrows():
    print(f"  {r['learn_first (A)']}  ->  {r['then (B)']}")
df[df["label"] == 0][["learn_first (A)", "then (B)"]].to_csv(
    "../docs/rejected_edges.csv", index=False, encoding="utf-8-sig")
