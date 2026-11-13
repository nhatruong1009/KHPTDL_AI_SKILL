"""Kiểm tra độ bền theo thời gian: bỏ biến định vị giai đoạn (chỉ số vĩ mô, tháng), so với baseline."""
import os

import pandas as pd

import analysis as A

HERE = os.path.dirname(os.path.abspath(__file__))

CLIENT_HIST_CAT = ["job", "education", "default", "housing", "loan", "contact", "poutcome"]
CLIENT_HIST_NUM = ["previous", "was_contacted", "pdays_num"]


def run(label, d, num, cat):
    n = len(d)
    i1, i2 = int(n * 0.70), int(n * 0.85)
    tr, te = d.iloc[:i1], d.iloc[i2:]
    cols = num + cat
    rows = []
    rates = tr.groupby("poutcome")["y_bin"].mean()
    mr, _ = A.metrics(te["y_bin"].values, te["poutcome"].map(rates).fillna(tr["y_bin"].mean()).values)
    rows.append({"scenario": label, "model": A.BASE_RULE, "test_base_rate": te["y_bin"].mean(),
                 "roc_auc": mr["roc_auc"], "lift_top20": mr["lift_top20"]})
    for kind, name in [("lr", A.MODEL_LR), ("gb", A.MODEL_GB)]:
        p = A.make_pipe(kind, num, cat).fit(tr[cols], tr["y_bin"])
        m, _ = A.metrics(te["y_bin"].values, p.predict_proba(te[cols])[:, 1])
        rows.append({"scenario": label, "model": name, "test_base_rate": te["y_bin"].mean(),
                     "roc_auc": m["roc_auc"], "lift_top20": m["lift_top20"]})
    return rows


d_add = A.prep(pd.read_csv(A.ADD, sep=";"), 999)
d_full = A.prep(pd.read_csv(A.FULL, sep=";"), -1)

rows = []
rows += run("bank-additional-full, thời gian: không macro, không tháng",
            d_add, CLIENT_HIST_NUM, [c for c in CLIENT_HIST_CAT])
rows += run("bank-full, thời gian: không tháng", d_full,
            ["balance", "previous", "was_contacted", "pdays_num"],
            ["job", "education", "default", "housing", "loan", "contact", "poutcome"])
out = pd.DataFrame(rows).drop_duplicates()
out.to_csv(os.path.join(HERE, "robustness_time_split.csv"), index=False)
print(out.round(4).to_string())
