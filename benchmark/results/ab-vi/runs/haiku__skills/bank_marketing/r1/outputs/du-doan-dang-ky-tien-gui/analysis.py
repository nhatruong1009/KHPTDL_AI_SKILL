"""Dự đoán khách hàng đăng ký tiền gửi có kỳ hạn TRƯỚC khi gọi điện.

Dữ liệu: data/bank-additional/bank-additional-full.csv (đầy đủ nhất: 41.188 dòng, 20 biến đầu vào).
Loại bỏ `duration` vì chỉ biết sau khi cuộc gọi kết thúc (rò rỉ dữ liệu).
Chạy: python analysis.py   (đường dẫn tính tương đối với vị trí script)
"""
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, log_loss
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

warnings.filterwarnings("ignore")
SEED = 42
ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
OUT = Path(__file__).resolve().parent
OUT.mkdir(parents=True, exist_ok=True)

MACRO = ["emp.var.rate", "cons.price.idx", "cons.conf.idx", "euribor3m", "nr.employed"]
LEAK = ["duration"]

VN_NAMES = {
    "age": "tuổi", "job": "nghề nghiệp", "marital": "tình trạng hôn nhân", "education": "học vấn",
    "default": "có nợ xấu", "housing": "vay mua nhà", "loan": "vay tiêu dùng", "contact": "loại liên lạc",
    "month": "tháng liên lạc", "day_of_week": "thứ liên lạc", "campaign": "số lần gọi trong chiến dịch",
    "pdays_contacted": "đã từng được liên lạc trước đây", "pdays_num": "số ngày từ lần liên lạc trước",
    "previous": "số lần liên lạc trước đây", "poutcome": "kết quả chiến dịch trước",
    "emp.var.rate": "tỷ lệ biến động việc làm", "cons.price.idx": "chỉ số giá tiêu dùng",
    "cons.conf.idx": "chỉ số niềm tin tiêu dùng", "euribor3m": "lãi suất euribor 3 tháng",
    "nr.employed": "số lao động có việc", "day": "ngày trong tháng", "balance": "số dư tài khoản",
}


def load(path, sep=";"):
    d = pd.read_csv(path, sep=sep)
    d = d.drop_duplicates().reset_index(drop=True)  # 12 dòng trùng hoàn toàn trong bản additional
    d["target"] = (d["y"] == "yes").astype(int)
    return d.drop(columns="y")


def prepare(d, drop_macro=False):
    """Tạo đặc trưng dùng được trước khi gọi. pdays: mã 999 (hoặc -1) = chưa từng được gọi."""
    X = d.drop(columns=["target"] + LEAK, errors="ignore").copy()
    if "pdays" in X:
        sentinel = -1 if (X["pdays"] < 0).any() else 999
        X["pdays_contacted"] = (X["pdays"] != sentinel).astype(int)
        X["pdays_num"] = X["pdays"].where(X["pdays"] != sentinel, 0)
        X = X.drop(columns="pdays")
    if drop_macro:
        X = X.drop(columns=[c for c in MACRO if c in X], errors="ignore")
    cats = [c for c in X.columns if not pd.api.types.is_numeric_dtype(X[c])]
    nums = [c for c in X.columns if c not in cats]
    return X, cats, nums


def make_logit(cats, nums):
    pre = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), cats),
        ("num", StandardScaler(), nums),
    ])
    return Pipeline([("pre", pre), ("clf", LogisticRegression(max_iter=2000, C=1.0))])


def make_gbm(cats, nums):
    pre = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cats),
        ("num", "passthrough", nums),
    ])
    clf = HistGradientBoostingClassifier(
        learning_rate=0.05, max_iter=500, max_leaf_nodes=15, min_samples_leaf=40,
        l2_regularization=1.0, early_stopping=True, validation_fraction=0.1,
        n_iter_no_change=30, random_state=SEED)
    return Pipeline([("pre", pre), ("clf", clf)])


def lift_table(y, score, n_bins=10):
    df = pd.DataFrame({"y": y, "s": score}).sort_values("s", ascending=False).reset_index(drop=True)
    df["decile"] = np.arange(len(df)) * n_bins // len(df) + 1
    g = df.groupby("decile")["y"].agg(["size", "sum"]).rename(columns={"size": "so_khach", "sum": "so_dang_ky"})
    base = df["y"].mean()
    g["ty_le_dang_ky"] = g["so_dang_ky"] / g["so_khach"]
    g["lift"] = g["ty_le_dang_ky"] / base
    g["ty_le_thu_hoi_luy_ke"] = g["so_dang_ky"].cumsum() / df["y"].sum()
    return g.reset_index()


def topk_metrics(y, score, fracs=(0.1, 0.2, 0.3)):
    order = np.argsort(-score)
    out = {}
    for f in fracs:
        k = int(round(len(y) * f))
        top = np.asarray(y)[order[:k]]
        out[f"lift_top{int(f*100)}"] = top.mean() / np.mean(y)
        out[f"thu_hoi_top{int(f*100)}"] = top.sum() / np.sum(y)
    return out


def rule_score(d):
    """Baseline đơn giản: ưu tiên khách có kết quả chiến dịch trước là 'success', rồi 'failure'."""
    m = {"success": 2, "failure": 1}
    return d["poutcome"].map(m).fillna(0).values if "poutcome" in d else np.zeros(len(d))


def run(path, label, sep=";", drop_macro_variant=True, save_charts=True):
    d = load(path, sep)
    X, cats, nums = prepare(d)
    y = d["target"].values
    Xtr, Xte, ytr, yte, dtr, dte = train_test_split(
        X, y, d, test_size=0.25, stratify=y, random_state=SEED)

    models = {
        "Baseline: tỷ lệ chung (không dự đoán gì)": None,
        "Baseline: luật đơn giản (kết quả chiến dịch trước)": "rule",
        "Hồi quy logistic": make_logit(cats, nums),
        "Gradient boosting (HistGB)": make_gbm(cats, nums),
    }
    rows, scores = [], {}
    cv = StratifiedKFold(5, shuffle=True, random_state=SEED)
    for name, m in models.items():
        is_model = not (m is None or isinstance(m, str))  # baseline không có xác suất thật
        if m is None:
            s = np.full(len(yte), ytr.mean())
            cv_auc = np.full(5, np.nan)  # hằng số -> AUC = 0.5 theo định nghĩa, không cần CV
        elif m == "rule":
            s = rule_score(dte) + 1e-6 * np.random.RandomState(SEED).rand(len(dte))
            cv_auc = np.full(5, np.nan)  # luật cố định, không được huấn luyện nên không có CV
        else:
            m.fit(Xtr, ytr)
            s = m.predict_proba(Xte)[:, 1]
            cv_auc = cross_val_score(m, X, y, cv=cv, scoring="roc_auc")
        scores[name] = s
        row = {
            "mô_hình": name,
            "roc_auc_holdout": roc_auc_score(yte, s),
            "roc_auc_cv_tb": np.nanmean(cv_auc) if is_model else np.nan,
            "roc_auc_cv_sd": np.nanstd(cv_auc) if is_model else np.nan,
            "pr_auc_holdout": average_precision_score(yte, s),
            "brier": brier_score_loss(yte, np.clip(s, 0, 1)) if is_model else np.nan,
            "log_loss": log_loss(yte, np.clip(s, 1e-6, 1 - 1e-6)) if is_model else np.nan,
        }
        row.update(topk_metrics(yte, s))
        rows.append(row)
    res = pd.DataFrame(rows)

    # Biến thể không có chỉ số kinh tế vĩ mô (các chỉ số này thay đổi theo thời kỳ, khó biết trước khi chiến dịch mới)
    if drop_macro_variant:
        Xm, catsm, numsm = prepare(d, drop_macro=True)
        idx_tr, idx_te = train_test_split(np.arange(len(y)), test_size=0.25, stratify=y, random_state=SEED)
        gb_nm = make_gbm(catsm, numsm).fit(Xm.iloc[idx_tr], y[idx_tr])
        s_nm = gb_nm.predict_proba(Xm.iloc[idx_te])[:, 1]
        r = {"mô_hình": "Gradient boosting, không dùng chỉ số vĩ mô",
             "roc_auc_holdout": roc_auc_score(yte, s_nm),
             "pr_auc_holdout": average_precision_score(yte, s_nm),
             "brier": brier_score_loss(yte, s_nm)}
        r.update(topk_metrics(yte, s_nm))
        res = pd.concat([res, pd.DataFrame([r])], ignore_index=True)

    res.to_csv(OUT / f"ket_qua_mo_hinh_{label}.csv", index=False)

    # Lift theo decile (mô hình tốt nhất)
    best = "Gradient boosting (HistGB)"
    lt = lift_table(yte, scores[best])
    lt.to_csv(OUT / f"lift_theo_decile_{label}.csv", index=False)

    # Quan trọng đặc trưng: permutation importance trên holdout (đo mức giảm ROC AUC)
    gbm = models[best]
    pi = permutation_importance(gbm, Xte, yte, scoring="roc_auc", n_repeats=10,
                                random_state=SEED, n_jobs=-1)
    imp = pd.DataFrame({"đặc_trưng": X.columns, "giảm_roc_auc_tb": pi.importances_mean,
                        "độ_lệch_chuẩn": pi.importances_std})
    imp["tên_tiếng_việt"] = imp["đặc_trưng"].map(VN_NAMES).fillna(imp["đặc_trưng"])
    imp = imp.sort_values("giảm_roc_auc_tb", ascending=False)
    imp.to_csv(OUT / f"quan_trong_dac_trung_{label}.csv", index=False)

    # Hệ số hồi quy logistic (odds ratio) để biết chiều tác động
    lg = models["Hồi quy logistic"]
    names = lg.named_steps["pre"].get_feature_names_out()
    coef = lg.named_steps["clf"].coef_[0]
    co = pd.DataFrame({"đặc_trưng": names, "hệ_số_log_odds": coef,
                       "odds_ratio": np.exp(coef)})
    co.to_csv(OUT / f"he_so_logistic_{label}.csv", index=False)

    if save_charts:
        make_charts(res, lt, imp, scores, yte, label)

    return res, lt, imp, co


def make_charts(res, lt, imp, scores, yte, label):
    # 1) Đường lợi ích tích lũy: % khách đăng ký thu được khi gọi top X% theo điểm
    fig, ax = plt.subplots(figsize=(8, 5.5))
    ax.plot([0, 1], [0, 1], "--", color="#999999", label="Chọn ngẫu nhiên")
    for name, s in scores.items():
        if name.startswith("Baseline: tỷ lệ"):
            continue
        order = np.argsort(-s)
        cum = np.cumsum(np.asarray(yte)[order]) / np.sum(yte)
        x = np.arange(1, len(s) + 1) / len(s)
        ax.plot(x, cum, label=name, linewidth=2)
    ax.set_xlabel("Tỷ lệ khách được gọi (theo thứ tự điểm giảm dần)")
    ax.set_ylabel("Tỷ lệ khách đăng ký thu được")
    ax.set_title("Đường lợi ích: gọi 20% khách đầu tiên thu được bao nhiêu khách đăng ký?")
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.legend(frameon=False, fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / f"duong_loi_ich_{label}.png", dpi=150)
    plt.close(fig)

    # 2) Quan trọng đặc trưng
    top = imp.head(12).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(top["tên_tiếng_việt"], top["giảm_roc_auc_tb"], xerr=top["độ_lệch_chuẩn"],
            color="#2b6cb0")
    ax.set_xlabel("Mức giảm ROC AUC khi xáo trộn đặc trưng (trên tập kiểm tra)")
    ax.set_title("12 yếu tố quan trọng nhất để dự đoán đăng ký tiền gửi")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / f"quan_trong_dac_trung_{label}.png", dpi=150)
    plt.close(fig)

    # 3) Tỷ lệ đăng ký theo decile
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(lt["decile"].astype(str), lt["ty_le_dang_ky"], color="#2f855a")
    ax.axhline(yte.mean(), color="#555555", linestyle="--", label=f"Tỷ lệ chung {yte.mean():.1%}")
    ax.set_xlabel("Nhóm điểm (decile 1 = điểm cao nhất)")
    ax.set_ylabel("Tỷ lệ đăng ký thực tế")
    ax.set_title("Tỷ lệ đăng ký thực tế theo nhóm điểm mô hình")
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / f"ty_le_theo_decile_{label}.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main_path = DATA / "bank-additional" / "bank-additional-full.csv"
    res, lt, imp, co = run(main_path, "chinh", sep=";", drop_macro_variant=True, save_charts=True)
    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", 30)
    print("== Kết quả trên bank-additional-full (holdout 25%) ==")
    print(res.round(4).to_string(index=False))
    print("\n== Lift theo decile (GBM) ==")
    print(lt.round(3).to_string(index=False))
    print("\n== Top 12 đặc trưng (permutation, GBM) ==")
    print(imp.head(12).round(4).to_string(index=False))
    print("\n== Hệ số logistic (odds ratio) — 15 đặc trưng mạnh nhất theo |log-odds| ==")
    print(co.reindex(co.hệ_số_log_odds.abs().sort_values(ascending=False).index).head(15).round(3).to_string(index=False))

    # Độ nhạy: bank-full.csv (45.211 dòng, có balance, không có chỉ số vĩ mô, poutcome có 'unknown')
    res2, lt2, imp2, _ = run(DATA / "bank-full.csv", "bank-full", sep=";",
                             drop_macro_variant=False, save_charts=False)
    print("\n== Độ nhạy trên bank-full.csv ==")
    print(res2.round(4).to_string(index=False))
    print("\n== Top 8 đặc trưng (bank-full) ==")
    print(imp2.head(8).round(4).to_string(index=False))
