"""Dự đoán khách hàng đăng ký tiền gửi có kỳ hạn TRƯỚC khi gọi điện.

Dữ liệu chính: data/bank-additional/bank-additional-full.csv (41.188 dòng, 21 cột).
Chia theo thời gian: dữ liệu được sắp theo ngày -> train 70% / valid 15% / test 15%.
"""
import json
import os

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import seaborn as sns  # noqa: E402
from sklearn.compose import ColumnTransformer  # noqa: E402
from sklearn.ensemble import HistGradientBoostingClassifier  # noqa: E402
from sklearn.impute import SimpleImputer  # noqa: E402
from sklearn.inspection import permutation_importance  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import average_precision_score, roc_auc_score  # noqa: E402
from sklearn.pipeline import Pipeline  # noqa: E402
from sklearn.preprocessing import OneHotEncoder, StandardScaler  # noqa: E402

SEED = 42
HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, "..", ".."))
ADD = os.path.join(WS, "data", "bank-additional", "bank-additional-full.csv")
FULL = os.path.join(WS, "data", "bank-full.csv")
OUT = HERE

sns.set_theme(style="whitegrid")

BASE_RANDOM = "Ngẫu nhiên"
BASE_RULE = "Luật đơn giản (kết quả chiến dịch trước)"
MODEL_LR = "Hồi quy logistic"
MODEL_GB = "Gradient boosting"

# Feature set chính (bank-additional-full.csv). Tuổi và tình trạng hôn nhân bị loại
# khỏi mô hình (thông tin cá nhân nhạy cảm); `day` không có trong file này.
ADD_CAT = ["job", "education", "default", "housing", "loan", "contact",
           "month", "day_of_week", "poutcome"]
ADD_NUM = ["previous", "was_contacted", "pdays_num"]
MACRO = ["emp.var.rate", "cons.price.idx", "cons.conf.idx", "euribor3m", "nr.employed"]

# Feature set cho bank-full.csv (không có chỉ số vĩ mô, có balance và day, không có day_of_week)
FULL_CAT = ["job", "education", "default", "housing", "loan", "contact", "month", "poutcome"]
FULL_NUM = ["balance", "previous", "was_contacted", "pdays_num"]

VI = {
    "job": "nghề nghiệp", "education": "trình độ học vấn", "default": "có nợ tín dụng",
    "housing": "vay mua nhà", "loan": "vay cá nhân", "contact": "loại liên lạc",
    "month": "tháng liên lạc", "day_of_week": "thứ liên lạc", "poutcome": "kết quả chiến dịch trước",
    "previous": "số lần liên lạc trước", "was_contacted": "đã từng được liên lạc",
    "pdays_num": "số ngày từ lần liên lạc trước", "emp.var.rate": "tỷ lệ việc làm",
    "cons.price.idx": "chỉ số giá tiêu dùng", "cons.conf.idx": "niềm tin tiêu dùng",
    "euribor3m": "lãi suất Euribor 3 tháng", "nr.employed": "số người đang làm việc",
    "balance": "số dư tài khoản", "duration": "thời lượng cuộc gọi", "campaign": "số lần gọi trong chiến dịch",
}


def prep(df, sentinel):
    d = df.copy()
    d["was_contacted"] = (d["pdays"] != sentinel).astype(int)
    d["pdays_num"] = d["pdays"].where(d["pdays"] != sentinel)
    d["y_bin"] = (d["y"] == "yes").astype(int)
    return d


def make_pipe(kind, num, cat):
    num_t = Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())])
    pre = ColumnTransformer(
        [("num", num_t, num), ("cat", OneHotEncoder(handle_unknown="ignore"), cat)],
        sparse_threshold=0,
    )
    if kind == "lr":
        clf = LogisticRegression(max_iter=3000, C=1.0)
    else:
        clf = HistGradientBoostingClassifier(
            learning_rate=0.05, max_iter=300, max_leaf_nodes=31,
            min_samples_leaf=40, l2_regularization=1.0, random_state=SEED,
        )
    return Pipeline([("pre", pre), ("clf", clf)])


def metrics(y, s):
    y = np.asarray(y)
    s = np.asarray(s, dtype=float)
    rng = np.random.default_rng(SEED)
    s = s + rng.uniform(0, 1e-12, len(s))  # phá hoà điểm bằng nhau một cách ngẫu nhiên
    order = np.argsort(-s, kind="stable")
    ys = y[order]
    out = {
        "roc_auc": roc_auc_score(y, s),
        "pr_auc": average_precision_score(y, s),
        "base_rate": y.mean(),
    }
    for f in (0.10, 0.20, 0.30):
        k = int(round(len(y) * f))
        top = ys[:k]
        p = int(round(f * 100))
        out[f"precision_top{p}"] = top.mean()
        out[f"recall_top{p}"] = top.sum() / y.sum()
        out[f"lift_top{p}"] = top.mean() / y.mean()
    cum = np.cumsum(ys) / ys.sum()
    return out, cum


def evaluate(d, num, cat):
    n = len(d)
    i1, i2 = int(n * 0.70), int(n * 0.85)
    tr, va, te = d.iloc[:i1].copy(), d.iloc[i1:i2].copy(), d.iloc[i2:].copy()
    cols = num + cat
    ytr, yva, yte = tr["y_bin"].values, va["y_bin"].values, te["y_bin"].values
    rng = np.random.default_rng(SEED)
    val, test, scores, fitted = {}, {}, {}, {}

    def add(name, sv, st):
        val[name] = metrics(yva, sv)[0]
        m, cum = metrics(yte, st)
        test[name] = m
        scores[name] = (np.asarray(st), cum)

    add(BASE_RANDOM, rng.uniform(size=len(va)), rng.uniform(size=len(te)))
    rates = tr.groupby("poutcome")["y_bin"].mean()  # chỉ học từ train
    prior = ytr.mean()
    add(BASE_RULE,
        va["poutcome"].map(rates).fillna(prior).values,
        te["poutcome"].map(rates).fillna(prior).values)
    for kind, label in [("lr", MODEL_LR), ("gb", MODEL_GB)]:
        p = make_pipe(kind, num, cat).fit(tr[cols], ytr)
        fitted[label] = p
        add(label, p.predict_proba(va[cols])[:, 1], p.predict_proba(te[cols])[:, 1])
    chosen = max([MODEL_LR, MODEL_GB], key=lambda k: val[k]["roc_auc"])  # chọn trên valid
    return {"val": val, "test": test, "scores": scores, "fitted": fitted, "chosen": chosen,
            "tr": tr, "va": va, "te": te, "cols": cols}


def main():
    os.makedirs(OUT, exist_ok=True)
    raw = pd.read_csv(ADD, sep=";")
    dup_n = int(raw.duplicated().sum())
    d = prep(raw, 999)
    num_main = ADD_NUM + MACRO
    R = evaluate(d, num_main, ADD_CAT)
    chosen = R["chosen"]

    # --- bảng chia dữ liệu và tỷ lệ đăng ký nền (kiểm tra độ lệch) ---
    split = pd.DataFrame([
        {"split": nm, "rows": len(x), "base_rate": x["y_bin"].mean()}
        for nm, x in [("train", R["tr"]), ("valid", R["va"]), ("test", R["te"])]
    ])
    split.to_csv(os.path.join(OUT, "split_info.csv"), index=False)

    pd.DataFrame(R["val"]).T.rename_axis("model").to_csv(os.path.join(OUT, "metrics_valid.csv"))
    pd.DataFrame(R["test"]).T.rename_axis("model").to_csv(os.path.join(OUT, "metrics_test.csv"))

    # --- độ nhạy ---
    sens_rows = []

    def sens(label, dd, num, cat):
        r = evaluate(dd, num, cat)
        for mname in [MODEL_LR, MODEL_GB]:
            m = r["test"][mname]
            sens_rows.append({"scenario": label, "model": mname,
                              "roc_auc": m["roc_auc"], "pr_auc": m["pr_auc"],
                              "lift_top20": m["lift_top20"], "recall_top20": m["recall_top20"]})
        return r

    sens("Chính (không duration/campaign, có chỉ số vĩ mô)", d, num_main, ADD_CAT)
    sens("S1: thêm duration (biến sau cuộc gọi, chỉ để đối chiếu)", d, num_main + ["duration"], ADD_CAT)
    sens("S2: thêm campaign (chưa biết trước cuộc gọi)", d, num_main + ["campaign"], ADD_CAT)
    sens("S3: bỏ chỉ số kinh tế vĩ mô", d, ADD_NUM, ADD_CAT)
    full = prep(pd.read_csv(FULL, sep=";"), -1)
    sens("S4: bank-full.csv (45.211 dòng, không có chỉ số vĩ mô)", full, FULL_NUM, FULL_CAT)
    pd.DataFrame(sens_rows).to_csv(os.path.join(OUT, "sensitivity.csv"), index=False)

    # --- permutation importance trên test cho mô hình được chọn ---
    te, cols = R["te"], R["cols"]
    pipe = R["fitted"][chosen]
    pi = permutation_importance(pipe, te[cols], te["y_bin"].values, scoring="roc_auc",
                                n_repeats=5, random_state=SEED)
    imp = (pd.DataFrame({"feature": cols, "auc_drop_mean": pi.importances_mean,
                         "auc_drop_std": pi.importances_std})
           .sort_values("auc_drop_mean", ascending=False))
    imp.to_csv(os.path.join(OUT, "permutation_importance.csv"), index=False)

    # --- hệ số hồi quy logistic (hướng tác động, chỉ mang tính liên hệ) ---
    lr = R["fitted"][MODEL_LR]
    coef = pd.DataFrame({"term": lr.named_steps["pre"].get_feature_names_out(),
                         "coef_std": lr.named_steps["clf"].coef_[0]})
    coef["abs"] = coef["coef_std"].abs()
    coef = coef.sort_values("abs", ascending=False).drop(columns="abs").head(20)
    coef.to_csv(os.path.join(OUT, "logit_coefficients_top20.csv"), index=False)

    # --- kiểm tra lỗi theo nhóm tuổi (không dùng làm biến dự đoán) ---
    st = R["scores"][chosen][0]
    thr = np.quantile(st, 0.80)
    tt = te.copy()
    tt["score"] = st
    tt["flag"] = tt["score"] >= thr
    tt["age_band"] = pd.cut(tt["age"], [0, 29, 39, 49, 59, 120],
                            labels=["<30", "30-39", "40-49", "50-59", "60+"])
    age_rows = []
    for b, g in tt.groupby("age_band", observed=True):
        auc_b = roc_auc_score(g["y_bin"], g["score"]) if g["y_bin"].nunique() == 2 else np.nan
        age_rows.append({"age_band": str(b), "n": len(g), "base_rate": g["y_bin"].mean(),
                         "share_flagged_top20": g["flag"].mean(),
                         "precision_flagged": g.loc[g["flag"], "y_bin"].mean(),
                         "roc_auc_within_band": auc_b})
    pd.DataFrame(age_rows).to_csv(os.path.join(OUT, "age_group_audit.csv"), index=False)

    # --- biểu đồ ---
    short = {BASE_RANDOM: "Ngẫu nhiên", BASE_RULE: "Luật\nđơn giản",
             MODEL_LR: "Hồi quy\nlogistic", MODEL_GB: "Gradient\nboosting"}
    names = [BASE_RANDOM, BASE_RULE, MODEL_LR, MODEL_GB]
    colors = ["#9e9e9e", "#f0a202", "#2b6cb0", "#1a365d"]
    ch = R["test"][chosen]
    rule = R["test"][BASE_RULE]
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
    aucs = [R["test"][k]["roc_auc"] for k in names]
    lifts = [R["test"][k]["lift_top20"] for k in names]
    ax[0].bar([short[k] for k in names], aucs, color=colors)
    ax[0].set_ylim(0.5, 1.0)
    ax[0].set_ylabel("ROC-AUC (tập test)")
    for i, v in enumerate(aucs):
        ax[0].text(i, v + 0.005, f"{v:.3f}", ha="center")
    ax[0].set_title(f"AUC {ch['roc_auc']:.3f} so với {rule['roc_auc']:.3f} của luật đơn giản")
    ax[1].bar([short[k] for k in names], lifts, color=colors)
    ax[1].set_ylabel("Lift trong nhóm 20% xếp hạng đầu")
    ax[1].axhline(1, color="black", lw=0.8, ls="--")
    for i, v in enumerate(lifts):
        ax[1].text(i, v + 0.05, f"{v:.2f}x", ha="center")
    ax[1].set_title(f"Nhóm 20% đầu có tỷ lệ đăng ký gấp {ch['lift_top20']:.2f} lần mức nền")
    for a in ax:
        a.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "model_comparison.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 6))
    n_te = len(te)
    x = np.arange(1, n_te + 1) / n_te
    for k, c in zip(names, colors):
        cum = R["scores"][k][1]
        ax.plot(x, cum, color=c, lw=2.2 if k == chosen else 1.4, label=short[k].replace("\n", " "))
    cap20 = R["scores"][chosen][1][int(0.2 * n_te) - 1]
    ax.axvline(0.2, color="black", lw=0.8, ls=":")
    ax.set_xlabel("Tỷ lệ khách hàng được gọi (theo thứ tự điểm dự đoán)")
    ax.set_ylabel("Tỷ lệ người đăng ký thu được")
    ax.set_title(f"Gọi 20% khách hàng đứng đầu thu được {cap20:.0%} người đăng ký (ngẫu nhiên: 20%)")
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.savefig(os.path.join(OUT, "gains_curve.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)

    top = imp.head(10).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh([VI.get(f, f) for f in top["feature"]], top["auc_drop_mean"],
            xerr=top["auc_drop_std"], color="#2b6cb0")
    ax.set_xlabel("Giảm ROC-AUC khi xáo trộn biến (tập test)")
    top1 = imp.iloc[0]
    ax.set_title(f"Yếu tố quan trọng nhất là '{VI.get(top1['feature'], top1['feature'])}': "
                 f"xáo trộn làm AUC giảm {top1['auc_drop_mean']:.3f}")
    ax.spines[["top", "right"]].set_visible(False)
    fig.savefig(os.path.join(OUT, "feature_importance.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)

    summary = {
        "dup_rows_in_additional_full": dup_n,
        "rows": {"train": len(R["tr"]), "valid": len(R["va"]), "test": len(R["te"])},
        "chosen_model": chosen,
        "test": R["test"], "valid": R["val"],
        "sensitivity": sens_rows,
        "top_features": imp.head(10).to_dict(orient="records"),
    }
    with open(os.path.join(OUT, "results.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2, default=float)

    pd.set_option("display.width", 200)
    print("split:\n", split)
    print("\nVALID:\n", pd.DataFrame(R["val"]).T.round(4))
    print("\nTEST:\n", pd.DataFrame(R["test"]).T.round(4))
    print("\nchosen:", chosen)
    print("\nSENSITIVITY:\n", pd.DataFrame(sens_rows).round(4).to_string())
    print("\nPERMUTATION IMPORTANCE (top 12):\n", imp.head(12).round(4).to_string())
    print("\nAGE AUDIT:\n", pd.DataFrame(age_rows).round(3).to_string())
    print("\nLR COEF (top 15):\n", coef.head(15).round(3).to_string())


if __name__ == "__main__":
    main()
