"""Reference solutions -> benchmark/ground_truth.json

Computes the facts a correct answer should contain, from the REAL downloaded
data, with the cleaning the task requires. Where a question allows several
reasonable choices (year, exclusion rule, definition), several variants are
computed so the judge can accept any defensible one.

    python -I benchmark/reference.py            # all tasks
    python -I benchmark/reference.py himalaya   # one task
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent
D = ROOT / "data"


def r(x, n=2):
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x), n)


# ---------------------------------------------------------------------------
def retail_uk() -> dict:
    x = pd.read_excel(D / "retail_uk/online_retail_II.xlsx", sheet_name=None)
    raw = pd.concat(x.values(), ignore_index=True)
    n_raw = len(raw)
    df = raw.drop_duplicates()
    n_dup = n_raw - len(df)
    overlap = sum((v.InvoiceDate >= "2010-12-01") & (v.InvoiceDate < "2010-12-10")
                  for v in [list(x.values())[0]]).sum()
    df = df.assign(rev=df.Quantity * df.Price, inv=df.Invoice.astype(str))
    df["cancel"] = df.inv.str.startswith("C")
    sc = df.StockCode.astype(str)
    nonprod = sc.str.fullmatch(r"(POST|DOT|M|m|C2|BANK CHARGES|AMAZONFEE|ADJUST\d*|B|CRUK|D|PADS|S|TEST\d*|gift_.*)")
    df["product"] = ~nonprod

    def window(y):
        return df[(df.InvoiceDate >= f"{y}-01-01") & (df.InvoiceDate < f"{y}-12-10")]

    out = {"n_rows_raw_both_sheets": n_raw, "n_exact_duplicate_rows": int(n_dup),
           "n_rows_in_sheet_overlap_2010-12-01_to_09": int(overlap),
           "data_end": str(df.InvoiceDate.max()), "share_rows_missing_customer_id_pct":
           r(df["Customer ID"].isna().mean() * 100)}
    variants = {}
    for name, mask in {
        "net_all_lines (sales - cancellations, incl. fees)": pd.Series(True, index=df.index),
        "net_product_lines (excl. POST/fees/adjustments)": df["product"],
        "gross_sales_only (no cancellations, qty>0, price>0)": (~df.cancel) & (df.Quantity > 0) & (df.Price > 0),
    }.items():
        a, b = window(2010)[mask].rev.sum(), window(2011)[mask].rev.sum()
        f10 = df[(df.InvoiceDate.dt.year == 2010) & mask].rev.sum()
        variants[name] = {"jan1_dec9_2010": r(a, 0), "jan1_dec9_2011": r(b, 0), "growth_like_for_like_pct": r((b / a - 1) * 100),
                          "full_2010": r(f10, 0), "naive_2011_vs_full_2010_pct": r((b / f10 - 1) * 100)}
    out["revenue_variants_GBP"] = variants

    # new vs returning (customers with an ID, product lines, like-for-like windows)
    c = df[df["Customer ID"].notna() & df["product"]]
    first = c.groupby("Customer ID").InvoiceDate.min()
    w10 = c[(c.InvoiceDate >= "2010-01-01") & (c.InvoiceDate < "2010-12-10")]
    w11 = c[(c.InvoiceDate >= "2011-01-01") & (c.InvoiceDate < "2011-12-10")]
    new11 = first[(first >= "2011-01-01")].index
    rev11 = w11.groupby("Customer ID").rev.sum()
    rev10 = w10.groupby("Customer ID").rev.sum()
    both = rev10.index.intersection(rev11.index)
    churned = rev10.index.difference(rev11.index)
    out["customers_with_id_like_for_like"] = {
        "n_customers_2010": int(len(rev10)), "n_customers_2011": int(len(rev11)),
        "n_new_in_2011": int(rev11.index.isin(new11).sum()),
        "rev_2011_from_new_customers": r(rev11[rev11.index.isin(new11)].sum(), 0),
        "rev_2011_from_customers_seen_before": r(rev11[~rev11.index.isin(new11)].sum(), 0),
        "n_bought_both_years": int(len(both)),
        "retained_customers_rev_change": r(rev11[both].sum() - rev10[both].sum(), 0),
        "rev_2010_lost_from_customers_not_buying_2011": r(rev10[churned].sum(), 0),
        "pct_2010_customers_who_bought_again_2011": r(len(both) / len(rev10) * 100),
    }
    ctry = df[df["product"]].assign(y=df.InvoiceDate.dt.year)
    ctry = ctry[(ctry.InvoiceDate.dt.month * 100 + ctry.InvoiceDate.dt.day) < 1210]
    pv = ctry[ctry.y.isin([2010, 2011])].pivot_table(index="Country", columns="y", values="rev", aggfunc="sum").fillna(0)
    pv["chg"] = pv[2011] - pv[2010]
    out["top_country_changes_like_for_like"] = {k: r(v, 0) for k, v in pv.chg.sort_values().iloc[[0, 1, 2, -3, -2, -1]].items()}
    out["uk_share_of_2011_rev_pct"] = r(pv.loc["United Kingdom", 2011] / pv[2011].sum() * 100)
    return out


# ---------------------------------------------------------------------------
def student_perf() -> dict:
    keys = ["school", "sex", "age", "address", "famsize", "Pstatus", "Medu", "Fedu",
            "Mjob", "Fjob", "reason", "nursery", "internet"]
    m = pd.read_csv(D / "student_perf/student-mat.csv", sep=";")
    p = pd.read_csv(D / "student_perf/student-por.csv", sep=";")
    for t in (m, p):
        for g in ("G1", "G2", "G3"):
            t[g] = pd.to_numeric(t[g])
    both = m.merge(p, on=keys, suffixes=("_mat", "_por"))
    out = {"n_math": len(m), "n_por": len(p), "n_in_both_by_R_keys": len(both),
           "n_unique_students": len(m) + len(p) - len(both),
           "n_G3_zero_math": int((m.G3 == 0).sum()), "n_G3_zero_por": int((p.G3 == 0).sum()),
           "note_G3_zero": "G3=0 with G2>0 and 0 absences is most likely dropping out / not sitting the exam, not a real score"}
    res = {}
    for name, t in {"math": m, "portuguese": p}.items():
        for excl in (False, True):
            u = t[t.G3 > 0] if excl else t
            for a in ("Dalc", "Walc"):
                rho, pv = stats.spearmanr(u[a], u.G3)
                lo, hi = u[u[a] <= 2].G3, u[u[a] >= 4].G3
                U, pu = stats.mannwhitneyu(lo, hi)
                res[f"{name}|{a}|{'excl_G3=0' if excl else 'all'}"] = {
                    "spearman": r(rho, 3), "p": float(f"{pv:.3g}"), "mean_G3_low(1-2)": r(lo.mean()),
                    "mean_G3_high(4-5)": r(hi.mean()), "n_low": len(lo), "n_high": len(hi),
                    "rank_biserial": r(1 - 2 * U / (len(lo) * len(hi)), 3), "mwu_p": float(f"{pu:.3g}")}
    out["alcohol_vs_G3"] = res
    out["headline"] = ("Higher alcohol use is associated with lower final grades in both courses - clearest in Portuguese "
                       "(larger n); in Math weaker with G3=0 kept, stronger once G3=0 drop-outs are excluded. Effects are small (|rho| ~0.1-0.2). Observational: no causation; "
                       "confounders e.g. failures, studytime, sex, goout.")
    return out


# ---------------------------------------------------------------------------
def household_power() -> dict:
    df = pd.read_csv(D / "household_power/household_power_consumption.txt", sep=";", na_values="?",
                     usecols=["Date", "Time", "Global_active_power"], low_memory=False)
    df["ts"] = pd.to_datetime(df.Date + " " + df.Time, format="%d/%m/%Y %H:%M:%S")
    s = df.set_index("ts").Global_active_power
    out = {"first": str(s.index.min()), "last": str(s.index.max()), "n_minutes": len(s),
           "missing_minutes": int(s.isna().sum()), "missing_pct": r(s.isna().mean() * 100, 3)}
    # gaps (consecutive missing)
    na = s.isna().astype(int)
    grp = (na.diff() != 0).cumsum()
    runs = na.groupby(grp).agg(["sum", "size"])
    runs = runs[runs["sum"] > 0]
    starts = s.groupby(grp).apply(lambda v: v.index.min())
    top = runs.sort_values("size", ascending=False).head(4)
    out["longest_gaps"] = [{"start": str(starts[g]), "hours": r(sz / 60, 1)} for g, sz in top["size"].items()]
    kwh = s / 60  # kW averaged over 1 minute -> kWh
    daily = kwh.resample("D").sum(min_count=1)
    cover = s.notna().resample("D").mean()
    monthly = kwh.resample("MS").sum()
    mcover = s.notna().resample("MS").mean()
    monthly_adj = monthly / mcover  # scale up for missing minutes
    out["kwh_by_year_observed"] = {str(k.year): r(v, 0) for k, v in kwh.resample("YS").sum().items()}
    out["kwh_by_year_gap_adjusted"] = {str(k.year): r(v, 0) for k, v in (kwh.resample("YS").sum() / s.notna().resample("YS").mean()).items()}
    out["kwh_by_month_gap_adjusted"] = {str(k.date())[:7]: r(v, 0) for k, v in monthly_adj.items()}
    mm = monthly_adj[(monthly_adj.index >= "2007-01-01")]
    prof = mm.groupby(mm.index.month).mean()
    out["avg_month_profile_kwh_2007_2010"] = {int(k): r(v, 0) for k, v in prof.items()}
    out["lowest_avg_month"] = int(prof.idxmin()); out["highest_avg_month"] = int(prof.idxmax())
    dec = monthly_adj[monthly_adj.index.month == 12]
    out["december_kwh"] = {str(k.year): r(v, 0) for k, v in dec.items()}
    out["dec_2010_plausible_range_kwh"] = [r(dec[dec.index.year >= 2007].min() * 0.8, 0), r(dec[dec.index.year >= 2007].max() * 1.15, 0)]
    hourly = kwh.groupby(kwh.index.hour).mean() * 60
    out["avg_kw_by_hour_peak_hour"] = int(hourly.idxmax()); out["avg_kw_by_hour_low_hour"] = int(hourly.idxmin())
    dow = daily[cover > 0.9].groupby(daily[cover > 0.9].index.dayofweek).mean()
    out["avg_daily_kwh_weekday_vs_weekend"] = [r(dow[:5].mean(), 1), r(dow[5:].mean(), 1)]
    low = daily[(cover > 0.9)].nsmallest(20)
    out["unusual_low_days_sample"] = [str(d.date()) for d in low.index[:10]]
    out["note"] = ("kWh = sum(Global_active_power kW)/60. August is the low month (holidays - near-zero "
                   "consumption weeks e.g. Aug 2008), winter is high. '?' = missing; several multi-day gaps.")
    return out


# ---------------------------------------------------------------------------
def worldbank_health() -> dict:
    def load(sub):
        f = next((D / "worldbank_health" / sub).glob("API_*.csv"))
        mf = next((D / "worldbank_health" / sub).glob("Metadata_Country_*.csv"))
        return pd.read_csv(f, skiprows=4), pd.read_csv(mf)
    le, meta = load("life_expectancy")
    he, _ = load("health_expenditure_per_capita")
    gdp, _ = load("gdp_per_capita_ppp")
    countries = meta[meta.Region.notna()]["Country Code"]
    out = {"n_rows_in_file": len(le), "n_real_countries": int(len(countries)),
           "n_aggregates_to_drop": int(meta.Region.isna().sum())}
    years = [c for c in le.columns if c.isdigit()]
    cover = {}
    for y in years[-8:]:
        ok = (le.set_index("Country Code")[y].reindex(countries).notna()
              & he.set_index("Country Code")[y].reindex(countries).notna()
              & gdp.set_index("Country Code")[y].reindex(countries).notna())
        cover[y] = int(ok.sum())
    out["n_countries_with_all_3_by_year"] = cover
    res = {}
    for y in [y for y, n in cover.items() if n >= 150][-3:]:
        t = pd.DataFrame({"life": le.set_index("Country Code")[y], "he": he.set_index("Country Code")[y],
                          "gdp": gdp.set_index("Country Code")[y]}).reindex(countries).dropna()
        names = meta.set_index("Country Code").TableName
        rho, _ = stats.spearmanr(t.he, t.life)
        rl, _ = stats.pearsonr(np.log(t.he), t.life)
        # life expectancy ~ log(health exp) + log(gdp)
        X = np.column_stack([np.ones(len(t)), np.log(t.he), np.log(t.gdp)])
        beta, *_ = np.linalg.lstsq(X, t.life.values, rcond=None)
        resid = t.life - X @ beta
        X1 = np.column_stack([np.ones(len(t)), np.log(t.gdp)])
        b1, *_ = np.linalg.lstsq(X1, t.life.values, rcond=None)
        resid_gdp = t.life - X1 @ b1
        rk = resid.sort_values()
        res[y] = {
            "n": len(t), "spearman_he_le": r(rho, 3), "pearson_logHE_le": r(rl, 3),
            "coef_log_he": r(beta[1], 2), "coef_log_gdp": r(beta[2], 2),
            "r2_full": r(1 - resid.var() / t.life.var(), 3),
            "most_over_expected (resid vs logHE+logGDP)": [f"{names[c]} {r(v, 1)}" for c, v in rk[::-1].head(6).items()],
            "most_under_expected": [f"{names[c]} {r(v, 1)}" for c, v in rk.head(6).items()],
            "vietnam": {"le": r(t.life.get("VNM")), "he_usd": r(t.he.get("VNM"), 0), "gdp_ppp": r(t.gdp.get("VNM"), 0),
                        "resid_full_model": r(resid.get("VNM"), 2), "resid_gdp_only_model": r(resid_gdp.get("VNM"), 2),
                        "rank_resid_full_from_top": int((resid > resid.get("VNM", np.nan)).sum() + 1), "n": len(t)},
        }
    out["by_year"] = res
    return out


# ---------------------------------------------------------------------------
def himalaya() -> dict:
    m = pd.read_csv(D / "himalaya/members.csv")
    e = pd.read_csv(D / "himalaya/expeditions.csv")
    ev = m[m.peak_id == "EVER"].copy()
    ev["decade"] = (ev.year // 10) * 10
    g = ev.groupby(["decade", "hired"]).agg(n=("died", "size"), deaths=("died", "sum"), success=("success", "mean"))
    g["death_rate_pct"] = g.deaths / g.n * 100
    tab = {f"{int(d)}|{'hired' if h else 'member'}": {"n": int(v.n), "deaths": int(v.deaths),
           "death_rate_pct": r(v.death_rate_pct), "success_pct": r(v.success * 100)} for (d, h), v in g.iterrows()}
    era = ev.assign(era=np.where(ev.year < 1990, "pre-1990", "1990+")).groupby(["era", "hired"]).agg(
        n=("died", "size"), deaths=("died", "sum"), success=("success", "mean"), oxy=("oxygen_used", "mean"))
    era_t = {f"{a}|{'hired' if h else 'member'}": {"n": int(v.n), "deaths": int(v.deaths),
             "death_rate_pct": r(v.deaths / v.n * 100), "success_pct": r(v.success * 100),
             "oxygen_used_pct": r(v.oxy * 100)} for (a, h), v in era.iterrows()}
    ee = e[e.peak_id == "EVER"]
    cause = ev[ev.died].groupby(ev.year >= 1990).death_cause.value_counts().groupby(level=0).head(3)
    return {
        "n_everest_member_rows": len(ev), "n_everest_expeditions": int(len(ee)),
        "years": [int(ev.year.min()), int(ev.year.max())],
        "by_decade": tab, "by_era": era_t,
        "expeditions_per_decade": {int(k): int(v) for k, v in ee.groupby(ee.year // 10 * 10).size().items()},
        "top_death_causes_pre1990_vs_1990plus": {f"{'1990+' if k[0] else 'pre-1990'}|{k[1]}": int(v) for k, v in cause.items()},
        "headline": "Death rate per person on Everest fell sharply after 1990 while success rose; hired staff "
                    "(Sherpas) death rates fell too but remain notable; deaths concentrate in specific events "
                    "(e.g. 2014 icefall avalanche, 2015 earthquake) - year-level spikes, not a trend reversal.",
        "deaths_2014_2015": {int(y): int(v) for y, v in ev[ev.year.isin([2014, 2015])].groupby("year").died.sum().items()},
    }


# ---------------------------------------------------------------------------
def wine_quality() -> dict:
    rd = pd.read_csv(D / "wine_quality/winequality-red.csv", sep=";")
    wh = pd.read_csv(D / "wine_quality/winequality-white.csv", sep=";")
    a = pd.concat([rd.assign(color="red"), wh.assign(color="white")])
    corr = a.drop(columns="color").corr(method="spearman").quality.drop("quality").sort_values()
    return {
        "expected_decision": "Not relevant (refuse): no grape variety, no price, no country/region "
                             "(all wines are Portuguese Vinho Verde; names file says grape/brand/price omitted for privacy)",
        "missing_concepts": ["grape variety", "price", "country (France vs Portugal)"],
        "what_data_has": "11 physicochemical tests + sensory quality score 0-10, red (1599) and white (4898) Vinho Verde",
        "n_red": len(rd), "n_white": len(wh),
        "strongest_quality_correlate": corr.abs().idxmax(), "spearman_alcohol_quality": r(corr["alcohol"], 3),
        "acceptable_alternative": "e.g. which physicochemical properties are associated with higher quality (alcohol, volatile acidity), red vs white quality",
    }


# ---------------------------------------------------------------------------
def bank_marketing() -> dict:
    from sklearn.compose import ColumnTransformer
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import average_precision_score, roc_auc_score
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler

    df = pd.read_csv(D / "bank_marketing/bank-additional/bank-additional-full.csv", sep=";")
    y = (df.y == "yes").astype(int)
    cat = df.drop(columns="y").select_dtypes("object").columns.tolist()
    out = {"file": "bank-additional/bank-additional-full.csv", "n": len(df), "base_rate_pct": r(y.mean() * 100),
           "n_duplicate_rows": int(df.duplicated().sum()),
           "pct_pdays_999": r((df.pdays == 999).mean() * 100),
           "leakage_column": "duration (documented in bank-additional-names.txt)"}
    res = {}
    split = {"random_stratified_75_25": None, "time_ordered_last_25pct": int(len(df) * 0.75)}
    for sname, cut in split.items():
        if cut is None:
            from sklearn.model_selection import train_test_split
            tr, te = train_test_split(np.arange(len(df)), test_size=0.25, stratify=y, random_state=0)
        else:
            tr, te = np.arange(cut), np.arange(cut, len(df))
        for with_dur in (False, True):
            X = df.drop(columns=["y"] + ([] if with_dur else ["duration"]))
            num = [c for c in X.columns if c not in cat]
            pre = ColumnTransformer([("c", OneHotEncoder(handle_unknown="ignore"), cat), ("n", StandardScaler(), num)])
            for mname, mdl in {"logreg": LogisticRegression(max_iter=2000), "hgb": HistGradientBoostingClassifier(random_state=0)}.items():
                pipe = make_pipeline(pre, mdl).fit(X.iloc[tr], y.iloc[tr])
                pr = pipe.predict_proba(X.iloc[te])[:, 1]
                res[f"{sname}|{'WITH duration (leak)' if with_dur else 'no duration'}|{mname}"] = {
                    "roc_auc": r(roc_auc_score(y.iloc[te], pr), 3), "pr_auc": r(average_precision_score(y.iloc[te], pr), 3),
                    "test_base_rate": r(y.iloc[te].mean(), 3)}
    out["reference_models"] = res
    out["notes"] = ("Realistic no-duration ROC-AUC ~0.78-0.81 on random split; ROC-AUC >= 0.90 means duration (leak) was used. "
                    "Time-ordered split is harder (macro regime shift). Strongest signals: nr.employed / euribor3m / emp.var.rate "
                    "(macro), poutcome=success, pdays!=999, contact=cellular, month. Imbalanced: report PR-AUC / lift, not accuracy.")
    return out


REFS = {"retail_uk": retail_uk, "student_perf": student_perf, "household_power": household_power,
        "worldbank_health": worldbank_health, "himalaya": himalaya, "wine_quality": wine_quality,
        "bank_marketing": bank_marketing}


def main() -> None:
    path = ROOT / "ground_truth.json"
    truth = json.loads(path.read_text()) if path.exists() else {}
    for t in sys.argv[1:] or list(REFS):
        print(f"== {t}", flush=True)
        truth[t] = REFS[t]()
        print(json.dumps(truth[t], indent=1, ensure_ascii=False, default=str)[:3000])
    path.write_text(json.dumps(truth, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
