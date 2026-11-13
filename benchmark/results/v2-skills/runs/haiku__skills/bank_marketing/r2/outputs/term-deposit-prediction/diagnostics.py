"""Chẩn đoán độ lệch thời gian và so sánh với chia ngẫu nhiên (chỉ để đối chiếu, không dùng làm kết quả chính)."""
import os

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

import analysis as A

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = HERE

raw = pd.read_csv(A.ADD, sep=";")
d = A.prep(raw, 999)
n = len(d)

# 1) Tỷ lệ đăng ký theo khối 2.000 dòng liên tiếp (thứ tự thời gian trong file)
blk = np.arange(n) // 2000
by_block = (d.assign(block=blk)
            .groupby("block")
            .agg(rows=("y_bin", "size"), base_rate=("y_bin", "mean"),
                 nr_employed_mean=("nr.employed", "mean"),
                 first_month=("month", "first"), last_month=("month", "last")))
by_block.to_csv(os.path.join(OUT, "diagnostic_base_rate_by_block.csv"))
print("Tỷ lệ đăng ký theo khối 2.000 dòng:\n", by_block.round(3).to_string())

# 2) Chia ngẫu nhiên phân tầng (đối chiếu) -> cùng mô hình, cùng baseline
from sklearn.model_selection import train_test_split  # noqa: E402

idx = np.arange(n)
tr_i, te_i = train_test_split(idx, test_size=0.30, stratify=d["y_bin"], random_state=A.SEED)
va_i, te_i = train_test_split(te_i, test_size=0.50, stratify=d["y_bin"].iloc[te_i], random_state=A.SEED)
tr, va, te = d.iloc[tr_i], d.iloc[va_i], d.iloc[te_i]
num, cat = A.ADD_NUM + A.MACRO, A.ADD_CAT
cols = num + cat
rows = []
rates = tr.groupby("poutcome")["y_bin"].mean()
m_rule, _ = A.metrics(te["y_bin"].values, te["poutcome"].map(rates).fillna(tr["y_bin"].mean()).values)
rows.append({"split": "ngẫu nhiên phân tầng (đối chiếu)", "model": A.BASE_RULE, **{k: m_rule[k] for k in ("roc_auc", "lift_top20")}})
for kind, label in [("lr", A.MODEL_LR), ("gb", A.MODEL_GB)]:
    p = A.make_pipe(kind, num, cat).fit(tr[cols], tr["y_bin"])
    m, _ = A.metrics(te["y_bin"].values, p.predict_proba(te[cols])[:, 1])
    rows.append({"split": "ngẫu nhiên phân tầng (đối chiếu)", "model": label, **{k: m[k] for k in ("roc_auc", "lift_top20")}})
pd.DataFrame(rows).to_csv(os.path.join(OUT, "diagnostic_random_split.csv"), index=False)
print("\nChia ngẫu nhiên phân tầng (đối chiếu):\n", pd.DataFrame(rows).round(4).to_string())
print("tỷ lệ nền train/valid/test:", round(tr["y_bin"].mean(), 4), round(va["y_bin"].mean(), 4), round(te["y_bin"].mean(), 4))

# 3) Chia theo thời gian nhưng test = 15% cuối đã phân tích; kiểm tra thêm 'walk-forward' đơn giản
# (huấn luyện trên 60%, kiểm tra trên 20% kế tiếp, rồi 20% cuối) để xem độ ổn định
out = []
for a, b, c in [(0.6, 0.8, 1.0), (0.5, 0.7, 0.85)]:
    i1, i2, i3 = int(n * a), int(n * b), int(n * c)
    tr2, te2 = d.iloc[:i1], d.iloc[i1:i2] if c == 1.0 else d.iloc[i2:i3]
    rates2 = tr2.groupby("poutcome")["y_bin"].mean()
    mr, _ = A.metrics(te2["y_bin"].values, te2["poutcome"].map(rates2).fillna(tr2["y_bin"].mean()).values)
    p = A.make_pipe("lr", num, cat).fit(tr2[cols], tr2["y_bin"])
    ml, _ = A.metrics(te2["y_bin"].values, p.predict_proba(te2[cols])[:, 1])
    out.append({"train_upto": a, "test_from": b, "test_to": c, "test_base_rate": te2["y_bin"].mean(),
                "rule_auc": mr["roc_auc"], "lr_auc": ml["roc_auc"], "lr_lift20": ml["lift_top20"]})
pd.DataFrame(out).to_csv(os.path.join(OUT, "diagnostic_walk_forward.csv"), index=False)
print("\nKiểm tra trượt theo thời gian:\n", pd.DataFrame(out).round(4).to_string())
