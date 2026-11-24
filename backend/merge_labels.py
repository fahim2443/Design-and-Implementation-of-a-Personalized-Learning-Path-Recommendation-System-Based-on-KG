import pandas as pd
ones = {2,3,4,8,9,11,13,14,15,16,17,18,20,22,23,24,25,29,32,33,35,37,38,39,42,43,45,46,47,48,
        50,51,54,56,60,61,63,64,65,67,70,73,74,75,76,80,81,84,85,88,90,94,95,97,
        99,100,101,102,103,104,105,106,107,108,109,113,115,116,117,118,119,121,123,124,125,
        127,128,129,131,132,133,134,135,136,139,143,148,149,155,156,159,161,162,164,165,
        176,178,184,185,186,189,190,191,192,199,203,205,206,207,208,209,210,211,212,
        215,216,229,231,234,235}
df = pd.read_csv("../docs/edge_review_all.csv", encoding="utf-8-sig")
for i, r in df.iterrows():
    if pd.isna(r["ai_label"]) or r["ai_label"] == "":
        df.at[i, "ai_label"] = 1 if r["id"] in ones else 0
df["ai_label"] = df["ai_label"].astype(int)
df.to_csv("../docs/edge_review_all.csv", index=False, encoding="utf-8-sig")
print("total", len(df), "| label 1:", int(df["ai_label"].sum()), "| label 0:", int((df["ai_label"] == 0).sum()))
