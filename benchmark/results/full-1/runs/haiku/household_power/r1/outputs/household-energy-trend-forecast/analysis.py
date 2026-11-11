"""Household electricity: trend, seasonality, gaps/abnormal weeks, Dec-2010 forecast.

Input : data/household_power_consumption.txt (minute-level, ';' separated, '?' = missing)
Output: CSVs, PNG charts and summary.json in this folder.
Energy: Global_active_power (kW, average over each minute) / 60 = kWh for that minute.
"""
from pathlib import Path
import json
import warnings

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]  # outputs/<slug>/ -> outputs -> project root
SRC = ROOT / "data" / "household_power_consumption.txt"
N_PER_DAY = 1440
TRAIN_START = pd.Timestamp("2007-01-01")
BLOCK = 7
NSIM = 4000
rng = np.random.default_rng(42)
summary = {}

# ---------------------------------------------------------------- load
raw = pd.read_csv(SRC, sep=";", na_values=["?"], low_memory=False)
raw["ts"] = pd.to_datetime(raw["Date"] + " " + raw["Time"], format="%d/%m/%Y %H:%M:%S")
summary["raw_rows"] = int(len(raw))
summary["duplicate_timestamps"] = int(raw["ts"].duplicated().sum())
raw = raw.drop_duplicates("ts").set_index("ts").sort_index()
summary["first_ts"] = str(raw.index.min())
summary["last_ts"] = str(raw.index.max())

grid = pd.date_range(raw.index.min(), raw.index.max(), freq="min")
kw = raw["Global_active_power"].reindex(grid)  # NaN = timestamp absent or '?'
kwh_min = kw / 60.0
na = kwh_min.isna()
summary["expected_minutes"] = int(len(grid))
summary["unavailable_minutes"] = int(na.sum())
summary["unavailable_pct"] = round(100 * na.mean(), 2)
summary["missing_timestamps"] = int(grid.difference(raw.index).size)

# ---------------------------------------------------------------- gaps
g = (na != na.shift()).cumsum()
tmp = pd.DataFrame({"na": na.values, "g": g.values, "ts": grid})
runs = tmp[tmp["na"]].groupby("g")["ts"].agg(start="min", end="max", minutes="count")
runs = runs.reset_index(drop=True).sort_values("minutes", ascending=False)
runs.to_csv(HERE / "gap_runs.csv", index=False)
summary["gap_runs_total"] = int(len(runs))
summary["gap_runs_ge_60min"] = int((runs["minutes"] >= 60).sum())
summary["gap_runs_ge_1day"] = int((runs["minutes"] >= N_PER_DAY).sum())
summary["longest_gap_minutes"] = int(runs["minutes"].max())
summary["longest_gap"] = [str(runs.iloc[0]["start"]), str(runs.iloc[0]["end"])]

# ---------------------------------------------------------------- daily
daily = pd.DataFrame({
    "kwh_raw": kwh_min.resample("D").sum(min_count=1),
    "n_avail": kwh_min.resample("D").count(),
})
daily["coverage"] = daily["n_avail"] / N_PER_DAY
daily["usable"] = daily["coverage"] >= 0.5
# gap-adjusted: scale the available minutes up to a full day
daily["kwh"] = np.where(daily["usable"], daily["kwh_raw"] / daily["coverage"], np.nan)
daily["dow"] = daily.index.dayofweek
daily["month"] = daily.index.month
daily["year"] = daily.index.year
daily.to_csv(HERE / "daily.csv")
summary["days_total"] = int(len(daily))
summary["days_usable"] = int(daily["usable"].sum())
summary["days_low_coverage"] = daily.index[~daily["usable"]].strftime("%Y-%m-%d").tolist()

# ---------------------------------------------------------------- monthly
monthly = daily.resample("MS").agg(
    kwh_adj=("kwh", "sum"),
    kwh_raw=("kwh_raw", "sum"),
    days_usable=("usable", "sum"),
    mean_coverage=("coverage", "mean"),
)
monthly["days_in_month"] = monthly.index.days_in_month
monthly["complete"] = monthly["days_usable"] == monthly["days_in_month"]
monthly["mean_daily_kwh"] = monthly["kwh_adj"] / monthly["days_usable"].replace(0, np.nan)
monthly.to_csv(HERE / "monthly.csv")

# ---------------------------------------------------------------- weekly
weekly = daily.loc[daily["usable"], "kwh"].resample("W-SUN").agg(["mean", "count"])
weekly = weekly[weekly["count"] >= 5]  # weeks with >= 5 usable days
weekly = weekly.rename(columns={"mean": "mean_daily_kwh", "count": "days"})

# ---------------------------------------------------------------- Jan-Nov26 same-period comparison
idx = daily.index
same_period = ((idx.month < 11) | ((idx.month == 11) & (idx.day <= 26)))
ytd = daily[same_period & daily["usable"]].groupby("year")["kwh"].agg(["sum", "count", "mean"])
ytd.columns = ["kwh_jan_to_nov26", "usable_days", "mean_daily_kwh"]
ytd.to_csv(HERE / "same_period_by_year.csv")
full_years = daily[daily["usable"] & daily["year"].isin([2007, 2008, 2009])].groupby("year")["kwh"].agg(["sum", "count", "mean"])
full_years.columns = ["kwh_adj_total", "usable_days", "mean_daily_kwh"]
full_years.to_csv(HERE / "calendar_year_totals.csv")
summary["calendar_year_totals"] = {int(k): round(v, 1) for k, v in full_years["kwh_adj_total"].items()}
summary["jan_nov26_totals"] = {int(k): round(v, 1) for k, v in ytd["kwh_jan_to_nov26"].items()}

# ---------------------------------------------------------------- seasonality
dow_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
mod = daily[(daily["coverage"] >= 0.9) & (daily.index >= TRAIN_START)]
dow_mean = mod.groupby("dow")["kwh"].mean()
month_mean = mod.groupby("month")["kwh"].mean()
dow_mean.index = [dow_names[i] for i in dow_mean.index]
dow_mean.round(2).to_csv(HERE / "seasonality_dow.csv", header=["mean_daily_kwh"])
month_mean.round(2).to_csv(HERE / "seasonality_month.csv", header=["mean_daily_kwh"])
summary["dow_mean_daily_kwh"] = {k: round(v, 2) for k, v in dow_mean.items()}
summary["month_mean_daily_kwh"] = {int(k): round(v, 2) for k, v in month_mean.items()}


# ---------------------------------------------------------------- model (log daily, trend + annual Fourier + DOW)
def design(index):
    t = (index - TRAIN_START).days.values / 365.25
    doy = index.dayofyear.values / 365.25
    cols = [np.ones(len(index)), t]
    for k in (1, 2, 3):
        cols += [np.sin(2 * np.pi * k * doy), np.cos(2 * np.pi * k * doy)]
    dow = index.dayofweek.values
    for d in range(1, 7):
        cols.append((dow == d).astype(float))
    return np.column_stack(cols)


def fit_upto(train_end):
    tr = daily.loc[TRAIN_START:train_end]
    tr = tr[tr["coverage"] >= 0.9]
    y = np.log(tr["kwh"].values)
    X = design(tr.index)
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    r = y - X @ b
    return tr, X, y, b, r


def forecast(train_end, target_idx, nsim=NSIM):
    tr, X, y, b, r = fit_upto(train_end)
    s2 = (r @ r) / (len(y) - X.shape[1])
    cov_b = s2 * np.linalg.inv(X.T @ X)
    Xf = design(target_idx)
    n = len(target_idx)
    nb = int(np.ceil(n / BLOCK))
    bs_all = rng.multivariate_normal(b, cov_b, size=nsim)
    sims = np.empty(nsim)
    for i in range(nsim):
        starts = rng.integers(0, len(r) - BLOCK, size=nb)
        e = np.concatenate([r[s:s + BLOCK] for s in starts])[:n]  # block-bootstrapped residuals
        sims[i] = np.exp(Xf @ bs_all[i] + e).sum()
    return sims, b, len(y)


# trend from full model (fit on all modelable days)
_, _, _, b_full, r_full = fit_upto(daily.index.max())
trend_per_year_pct = 100 * (np.exp(b_full[1]) - 1)
summary["model_trend_pct_per_year"] = round(float(trend_per_year_pct), 2)

# daily anomalies vs. model (fitted for all usable days)
Xall = design(daily.index[daily["usable"]])
fitted = pd.Series(np.nan, index=daily.index)
fitted[daily["usable"]] = np.exp(Xall @ b_full)
resid_all = np.log(daily["kwh"]) - np.log(fitted)
mad = 1.4826 * np.nanmedian(np.abs(resid_all - np.nanmedian(resid_all)))
z_day = resid_all / mad
anom_days = pd.DataFrame({"kwh": daily["kwh"], "expected": fitted, "z": z_day, "coverage": daily["coverage"]})
anom_days = anom_days[anom_days["z"].abs() > 3.5].sort_values("z")
anom_days.round(3).to_csv(HERE / "anomalous_days.csv")
summary["anomalous_days_n"] = int(len(anom_days))
top_days = anom_days.reindex(anom_days["z"].abs().sort_values(ascending=False).index).head(12)
summary["anomalous_days_top"] = [
    [d.strftime("%Y-%m-%d"), round(float(v), 1), round(float(e), 1), round(float(z), 1)]
    for d, v, e, z in top_days[["kwh", "expected", "z"]].itertuples()
]

# weekly anomalies: mean of daily residuals per week vs expected pattern
wk_res = resid_all.resample("W-SUN").agg(["mean", "count"])
wk_res = wk_res[wk_res["count"] >= 5]
wmad = 1.4826 * np.median(np.abs(wk_res["mean"] - wk_res["mean"].median()))
wk_res["z"] = (wk_res["mean"] - wk_res["mean"].median()) / wmad
wk_res["actual_mean_daily_kwh"] = weekly["mean_daily_kwh"].reindex(wk_res.index)
wk_res["expected_mean_daily_kwh"] = np.exp(
    np.log(wk_res["actual_mean_daily_kwh"]) - wk_res["mean"])
wk_res["abnormal"] = wk_res["z"].abs() > 3
wk_res.round(3).to_csv(HERE / "weekly_vs_expected.csv")
abn_weeks = wk_res[wk_res["abnormal"]].sort_values("z")
summary["abnormal_weeks_n"] = int(len(abn_weeks))
summary["abnormal_weeks"] = [
    [d.strftime("%Y-%m-%d"), round(float(a), 1), round(float(e), 1), round(float(z), 1)]
    for d, a, e, z in abn_weeks[["actual_mean_daily_kwh", "expected_mean_daily_kwh", "z"]].itertuples()
]

# ---------------------------------------------------------------- backtests (1-month-ahead, rolling)
bt_rows = []
for m in pd.date_range("2008-01-01", "2010-11-01", freq="MS"):
    tidx = pd.date_range(m, m + pd.offsets.MonthEnd(0), freq="D")
    if tidx.max() > daily.index.max() or not daily.loc[tidx, "usable"].all():
        continue  # skip months that run past the data end or contain low-coverage days
    sims, _, _ = forecast(m - pd.Timedelta(days=1), tidx, nsim=2000)
    actual = daily.loc[tidx, "kwh"].sum()
    lo, hi = np.percentile(sims, [5, 95])
    bt_rows.append({"month": m.strftime("%Y-%m"), "actual": actual, "forecast_mean": sims.mean(),
                    "p05": lo, "p95": hi, "pct_err": 100 * (sims.mean() - actual) / actual,
                    "in_90pct": lo <= actual <= hi})
bt = pd.DataFrame(bt_rows)
bt.round(2).to_csv(HERE / "backtest_monthly.csv", index=False)
summary["backtest_months"] = int(len(bt))
summary["backtest_mape_pct"] = round(float(bt["pct_err"].abs().mean()), 2)
summary["backtest_bias_pct"] = round(float(bt["pct_err"].mean()), 2)
summary["backtest_coverage_90"] = round(float(bt["in_90pct"].mean()), 3)
bt_late = bt[bt["month"] >= "2009-01"]  # targets with >= 2 years of training history
summary["backtest_late_months"] = int(len(bt_late))
summary["backtest_late_mape_pct"] = round(float(bt_late["pct_err"].abs().mean()), 2)
summary["backtest_late_coverage_90"] = round(float(bt_late["in_90pct"].mean()), 3)
summary["backtest_late_pct_err_range"] = [round(float(bt_late["pct_err"].min()), 1),
                                          round(float(bt_late["pct_err"].max()), 1)]

# ---------------------------------------------------------------- forecast Dec 2010
dec_idx = pd.date_range("2010-12-01", "2010-12-31", freq="D")
train_end = daily.index[daily["usable"]].max()  # last usable day in data
sims, b_dec, n_train = forecast(train_end, dec_idx, nsim=NSIM)
f_mean = sims.mean()
f_p05, f_p50, f_p95 = np.percentile(sims, [5, 50, 95])
forecast_df = pd.DataFrame({
    "quantity": ["Dec 2010 total kWh (mean)", "5th pct", "median", "95th pct"],
    "kwh": [f_mean, f_p05, f_p50, f_p95],
})
forecast_df.round(1).to_csv(HERE / "forecast_dec2010.csv", index=False)
summary["forecast_dec2010"] = {"mean": round(f_mean, 1), "p05": round(f_p05, 1),
                               "p50": round(f_p50, 1), "p95": round(f_p95, 1),
                               "train_end": str(train_end.date()), "train_days": int(n_train)}

# cross-check: seasonal naive x same-period YoY ratio
dec09 = daily.loc["2009-12-01":"2009-12-31", "kwh"].sum()
ratio = summary["jan_nov26_totals"][2010] / summary["jan_nov26_totals"][2009]
naive = dec09 * ratio
summary["crosscheck_dec2009_actual"] = round(float(dec09), 1)
summary["crosscheck_yoy_ratio_jan_nov26"] = round(float(ratio), 4)
summary["crosscheck_naive_dec2010"] = round(float(naive), 1)
summary["dec_actuals"] = {int(y): round(float(daily.loc[f"{y}-12-01":f"{y}-12-31", "kwh"].sum()), 1)
                          for y in (2007, 2008, 2009)}

# ---------------------------------------------------------------- charts
plt.rcParams.update({"figure.dpi": 120, "axes.spines.top": False, "axes.spines.right": False})
BLUE, GREY, RED = "#2b6cb0", "#8a94a6", "#c53030"

# 1. monthly totals
fig, ax = plt.subplots(figsize=(11, 4.5))
c = monthly["complete"]
ax.bar(monthly.index[c], monthly["kwh_adj"][c], width=20, color=BLUE, label="complete month")
ax.bar(monthly.index[~c], monthly["kwh_adj"][~c], width=20, facecolor="white", edgecolor=BLUE,
       hatch="//", label="partial month (data edge or gaps)")
ax.set_ylabel("kWh per month (gap-adjusted)")
ax.set_title("Monthly electricity use, Dec 2006 - Nov 2010")
ax.legend(frameon=False, loc="upper right")
fig.tight_layout()
fig.savefig(HERE / "chart_monthly_kwh.png")
plt.close(fig)

# 2. seasonality: DOW + month-of-year
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
axes[0].bar(dow_mean.index, dow_mean.values, color=BLUE)
axes[0].set_title("Average daily kWh by weekday")
axes[0].set_ylabel("kWh per day")
mnames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
axes[1].bar([mnames[i - 1] for i in month_mean.index], month_mean.values, color=BLUE)
axes[1].set_title("Average daily kWh by month (2007-2010)")
fig.tight_layout()
fig.savefig(HERE / "chart_seasonality.png")
plt.close(fig)

# 3. weekly actual vs expected with abnormal weeks flagged
fig, ax = plt.subplots(figsize=(11, 4.5))
ax.plot(wk_res.index, wk_res["actual_mean_daily_kwh"], color=GREY, lw=1, label="actual weekly mean daily kWh")
ax.plot(wk_res.index, wk_res["expected_mean_daily_kwh"], color=BLUE, lw=1.5, label="expected (trend + seasonality + weekday)")
ab = wk_res[wk_res["abnormal"]]
ax.scatter(ab.index, ab["actual_mean_daily_kwh"], color=RED, zorder=3, label="abnormal week (|z|>3)")
ax.set_ylabel("kWh per day")
ax.set_title("Weekly usage vs expected pattern")
ax.legend(frameon=False, loc="upper right", fontsize=8)
fig.tight_layout()
fig.savefig(HERE / "chart_weekly_anomalies.png")
plt.close(fig)

# 4. forecast: Dec totals history + Dec 2010 forecast
fig, ax = plt.subplots(figsize=(8, 4.5))
dec_hist = {y: daily.loc[f"{y}-12-01":f"{y}-12-31", "kwh"].sum() for y in (2007, 2008, 2009)}
xs = list(dec_hist.keys()) + [2010]
ax.bar([str(x) for x in dec_hist], list(dec_hist.values()), color=GREY, label="actual December")
ax.bar(["2010"], [f_mean], color=BLUE, alpha=0.8, label="forecast December 2010 (mean)")
ax.errorbar(["2010"], [f_mean], yerr=[[f_mean - f_p05], [f_p95 - f_mean]], color="black", capsize=6,
            label="90% interval")
ax.set_ylabel("kWh in month")
ax.set_title("December totals and Dec 2010 forecast")
ax.set_ylim(0, 1450)
ax.legend(frameon=False, fontsize=8, loc="upper center", ncol=3)
fig.tight_layout()
fig.savefig(HERE / "chart_forecast_dec2010.png")
plt.close(fig)

with open(HERE / "summary.json", "w") as fh:
    json.dump(summary, fh, indent=2, default=str)

print(json.dumps(summary, indent=2, default=str))
print("\nBacktest (1-month ahead):")
print(bt.round(1).to_string(index=False))
print("\nTop gap runs:")
print(runs.head(8).to_string(index=False))
print("\nSame-period totals:")
print(ytd.round(1).to_string())
print("\nMonthly (adj):")
print(monthly[["kwh_adj", "days_usable", "days_in_month", "complete", "mean_daily_kwh"]].round(1).to_string())
