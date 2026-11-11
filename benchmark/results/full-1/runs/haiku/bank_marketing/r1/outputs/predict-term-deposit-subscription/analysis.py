"""Pre-call propensity model for term-deposit subscription.

Question: before calling a client, can we rank clients by likelihood to subscribe,
how much better is that than a naive baseline, and which factors matter most?

Design decisions
- Primary data: data/bank-additional/bank-additional-full.csv (41,188 rows, all 20 inputs
  incl. 5 national economic indicators). Cross-check: data/bank-full.csv (45,211 rows,
  16 inputs, no macro indicators).
- `duration` is excluded: the codebook states it is only known after the call (leakage).
- Macro indicators (emp.var.rate, cons.price.idx, cons.conf.idx, euribor3m, nr.employed)
  are national statistics published around the call date, so they are treated as
  available before the call. A sensitivity run drops them.
- 'unknown' is kept as its own category (it is the codebook's missing-value code).
- pdays=999 means "never contacted before"; split into a flag + a cleaned days value.
"""
from pathlib import Path
import json
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
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

warnings.filterwarnings("ignore")
SEED = 42
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]  # workspace root (outputs/<slug>/ -> workspace)
DATA = ROOT / "data"
OUT = HERE

CAT = ["job", "marital", "education", "default", "housing", "loan",
       "contact", "month", "day_of_week", "poutcome"]
MACRO = ["emp.var.rate", "cons.price.idx", "cons.conf.idx", "euribor3m", "nr.employed"]
NUM_BASE = ["age", "campaign", "previous"]


def load(path, sep=";"):
    df = pd.read_csv(path, sep=sep)
    df["y_bin"] = (df["y"] == "yes").astype(int)
    df = df.drop(columns=["y"])
    df["was_contacted_before"] = (df["pdays"] != 999).astype(int)
    df["pdays_clean"] = df["pdays"].where(df["pdays"] != 999, 0)
    df = df.drop(columns=["pdays"])
    return df


def feature_lists(df, use_macro):
    cats = [c for c in CAT if c in df.columns]
    nums = NUM_BASE + ["was_contacted_before", "pdays_clean"]
    if "balance" in df.columns:
        nums.append("balance")
    if use_macro:
        nums += [c for c in MACRO if c in df.columns]
    return cats, nums


def make_pipeline(model, cats, nums):
    pre = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cats),
        ("num", StandardScaler(), nums),
    ])
    return Pipeline([("pre", pre), ("clf", model)])


def lift_table(y_true, score, groups=10):
    d = pd.DataFrame({"y": y_true, "s": score}).sort_values("s", ascending=False).reset_index(drop=True)
    d["decile"] = (np.arange(len(d)) * groups // len(d)) + 1
    g = d.groupby("decile").agg(n=("y", "size"), subscribers=("y", "sum"))
    g["rate"] = g["subscribers"] / g["n"]
    base = d["y"].mean()
    g["lift"] = g["rate"] / base
    g["cum_capture"] = g["subscribers"].cumsum() / d["y"].sum()
    g["cum_share_called"] = g["n"].cumsum() / len(d)
    return g.reset_index()


def evaluate(name, y_true, score, cv_auc=None):
    top10 = lift_table(y_true, score, 10).iloc[0]
    top20 = lift_table(y_true, score, 5).iloc[0]
    return {
        "model": name,
        "roc_auc": roc_auc_score(y_true, score),
        "pr_auc": average_precision_score(y_true, score),
        "brier": brier_score_loss(y_true, np.clip(score, 0, 1)),
        "top10pct_precision": top10["rate"],
        "top10pct_lift": top10["lift"],
        "top10pct_capture": top10["cum_capture"],
        "top20pct_capture": top20["cum_capture"],
        "cv_roc_auc_mean": None if cv_auc is None else cv_auc.mean(),
        "cv_roc_auc_sd": None if cv_auc is None else cv_auc.std(),
    }


def run(df, label, use_macro):
    cats, nums = feature_lists(df, use_macro)
    X = df.drop(columns=["y_bin"])
    X = X[cats + nums]
    y = df["y_bin"].values
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=SEED)
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)

    rows = []
    # --- Naive baselines ---
    # 1) Majority class: call nobody / predicts "no" for everyone -> constant score.
    rows.append({
        "model": "Baseline A: predict 'no' for all (accuracy-only naive)",
        "roc_auc": 0.5, "pr_auc": y_te.mean(), "brier": None,
        "top10pct_precision": y_te.mean(), "top10pct_lift": 1.0,
        "top10pct_capture": 0.10, "top20pct_capture": 0.20,
        "cv_roc_auc_mean": 0.5, "cv_roc_auc_sd": 0.0,
        "accuracy": 1 - y_te.mean(),
    })
    # 2) Random ordering of clients (call in random order).
    rng = np.random.RandomState(SEED)
    rnd = rng.rand(len(y_te))
    r = evaluate("Baseline B: random call order", y_te, rnd)
    rows.append(r)
    # 3) Business rule: call clients whose previous campaign succeeded, then the rest.
    rule = (X_te["poutcome"] == "success").astype(float).values + 0.001 * rng.rand(len(y_te))
    rows.append(evaluate("Baseline C: rule 'previous campaign was a success'", y_te, rule))

    # --- Models ---
    lr = make_pipeline(LogisticRegression(max_iter=2000, C=1.0), cats, nums)
    gb = make_pipeline(HistGradientBoostingClassifier(
        learning_rate=0.05, max_iter=400, max_leaf_nodes=31, min_samples_leaf=40,
        l2_regularization=1.0, early_stopping=True, validation_fraction=0.1,
        random_state=SEED), cats, nums)

    fitted = {}
    for name, est in [("Logistic regression", lr), ("Gradient boosting (HistGB)", gb)]:
        cv_auc = cross_val_score(est, X_tr, y_tr, cv=skf, scoring="roc_auc", n_jobs=1)
        est.fit(X_tr, y_tr)
        score = est.predict_proba(X_te)[:, 1]
        r = evaluate(name, y_te, score, cv_auc)
        r["accuracy"] = ((score >= y_tr.mean()) == y_te).mean()  # not used for ranking; reference only
        rows.append(r)
        fitted[name] = (est, score)

    metrics = pd.DataFrame(rows)
    metrics.insert(0, "dataset", label)

    # Lift table for best model
    best_name = "Gradient boosting (HistGB)"
    best_est, best_score = fitted[best_name]
    lift = lift_table(y_te, best_score, 10)
    lift.insert(0, "dataset", label)

    # Permutation importance on the held-out test set (grouped by original feature).
    pi = permutation_importance(best_est, X_te, y_te, scoring="roc_auc",
                                n_repeats=10, random_state=SEED, n_jobs=1)
    imp = pd.DataFrame({"feature": X_te.columns, "importance_mean": pi.importances_mean,
                        "importance_sd": pi.importances_std})
    imp = imp.sort_values("importance_mean", ascending=False)
    imp.insert(0, "dataset", label)

    # Logistic coefficients (direction of effects, standardised numerics, one-hot cats)
    lr_est, _ = fitted["Logistic regression"]
    names = lr_est.named_steps["pre"].get_feature_names_out()
    coefs = pd.DataFrame({"term": names, "coef": lr_est.named_steps["clf"].coef_[0]})
    coefs["odds_ratio"] = np.exp(coefs["coef"])
    coefs = coefs.sort_values("coef", key=lambda s: s.abs(), ascending=False)
    coefs.insert(0, "dataset", label)

    return metrics, lift, imp, coefs, (y_te, best_score, fitted)


def main():
    main_df = load(DATA / "bank-additional" / "bank-additional-full.csv")
    cross_df = load(DATA / "bank-full.csv")

    m1, lift1, imp1, coef1, pack1 = run(main_df, "bank-additional-full (with macro)", use_macro=True)
    m2, lift2, imp2, coef2, _ = run(main_df, "bank-additional-full (no macro)", use_macro=False)
    m3, lift3, imp3, coef3, _ = run(cross_df, "bank-full (no macro, cross-check)", use_macro=False)

    metrics = pd.concat([m1, m2, m3], ignore_index=True)
    metrics.to_csv(OUT / "model_metrics.csv", index=False)
    pd.concat([lift1, lift2, lift3]).to_csv(OUT / "lift_by_decile.csv", index=False)
    pd.concat([imp1, imp2, imp3]).to_csv(OUT / "permutation_importance.csv", index=False)
    pd.concat([coef1, coef2, coef3]).to_csv(OUT / "logistic_coefficients.csv", index=False)

    # ---- Charts ----
    y_te, best_score, fitted = pack1
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    from sklearn.metrics import roc_curve, precision_recall_curve
    ax = axes[0]
    for name, (est, sc) in fitted.items():
        fpr, tpr, _ = roc_curve(y_te, sc)
        ax.plot(fpr, tpr, label=f"{name} (AUC={roc_auc_score(y_te, sc):.3f})")
    ax.plot([0, 1], [0, 1], "k--", lw=1, label="Random (AUC=0.5)")
    ax.set_xlabel("False positive rate"); ax.set_ylabel("True positive rate")
    ax.set_title("ROC on held-out 20% test set"); ax.legend(loc="lower right", fontsize=8)

    ax = axes[1]
    cum = lift1  # gradient boosting, primary dataset
    ax.plot(cum["cum_share_called"] * 100, cum["cum_capture"] * 100, marker="o", label="Gradient boosting")
    ax.plot([0, 100], [0, 100], "k--", lw=1, label="Random call order")
    ax.set_xlabel("% of clients called (ranked by model score)")
    ax.set_ylabel("% of all subscribers captured")
    ax.set_title("Cumulative gains: who to call first"); ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "roc_and_gains.png", dpi=150)
    plt.close(fig)

    top = imp1.head(12).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(top["feature"], top["importance_mean"], xerr=top["importance_sd"], color="#2b6cb0")
    ax.set_xlabel("Drop in test ROC AUC when feature is shuffled")
    ax.set_title("Top factors (gradient boosting, permutation importance)")
    fig.tight_layout()
    fig.savefig(OUT / "feature_importance.png", dpi=150)
    plt.close(fig)

    summary = {
        "n_rows_primary": int(len(main_df)),
        "base_rate_primary": float(main_df["y_bin"].mean()),
        "n_rows_crosscheck": int(len(cross_df)),
        "base_rate_crosscheck": float(cross_df["y_bin"].mean()),
        "duplicate_rows_primary": int(pd.read_csv(DATA / "bank-additional" / "bank-additional-full.csv", sep=";").duplicated().sum()),
    }
    (OUT / "run_summary.json").write_text(json.dumps(summary, indent=2))
    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", 20)
    print(metrics.round(4).to_string(index=False))
    print(lift1.round(3).to_string(index=False))
    print(imp1.head(12).round(4).to_string(index=False))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
