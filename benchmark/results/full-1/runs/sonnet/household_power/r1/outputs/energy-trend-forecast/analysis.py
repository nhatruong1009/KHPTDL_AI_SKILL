import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
O = "outputs/energy-trend-forecast/"
df = pd.read_csv("data/household_power_consumption.txt", sep=";", na_values="?", low_memory=False)
df.index = pd.to_datetime(df.Date + " " + df.Time, format="%d/%m/%Y %H:%M:%S")
g = df.Global_active_power
print("rows", len(df), "missing", g.isna().sum(), "dups", df.index.duplicated().sum())
full = pd.date_range(df.index.min(), df.index.max(), freq="min")
print("expected minutes", len(full), "absent rows", len(full) - len(df))
kwh = (g / 60).reindex(full)  # kW avg per minute -> kWh
miss = kwh.isna()
grp = (miss != miss.shift()).cumsum()
rows = []
for k, s in miss[miss].groupby(grp[miss]):
    rows.append((s.index[0], s.index[-1], len(s)))
gaps = pd.DataFrame(rows, columns=["start", "end", "minutes"]).sort_values("minutes", ascending=False)
gaps.to_csv(O + "gaps.csv", index=False)
print(gaps[gaps.minutes >= 60].to_string())
print("total missing min", miss.sum(), round(miss.mean() * 100, 2), "%")

d = pd.DataFrame({"kwh": kwh.resample("D").sum(min_count=1), "miss": miss.resample("D").sum()})
d["cov"] = 1 - d.miss / 1440
d["kwh_adj"] = d.kwh / d["cov"].where(d["cov"] > 0)
d.loc[d["cov"] < 0.5, "kwh_adj"] = np.nan
d.to_csv(O + "daily.csv")
d["month"] = d.index.to_period("M")
m = d.groupby("month").agg(kwh_obs=("kwh", "sum"), days=("kwh_adj", "count"), mean_day=("kwh_adj", "mean"))
m["kwh_full"] = m.mean_day * m.index.days_in_month
m.to_csv(O + "monthly.csv")
print(m.round(1).to_string())

h = kwh.groupby(kwh.index.hour).mean() * 60
print("hourly kW\n", h.round(2).to_string()); h.to_csv(O + "hourly_profile.csv")
dd = d.dropna(subset=["kwh_adj"])
dow = dd.groupby(dd.index.dayofweek).kwh_adj.mean()
print("dow\n", dow.round(2).to_string()); dow.to_csv(O + "dow_profile.csv")
mm = m[m.days >= 20]
mon = mm[mm.index.year.isin([2007, 2008, 2009])].groupby(mm[mm.index.year.isin([2007, 2008, 2009])].index.month).mean_day.mean()
print("month seasonal (2007-09)\n", mon.round(2).to_string()); mon.to_csv(O + "month_profile.csv")
print("year mean daily\n", dd.groupby(dd.index.year).kwh_adj.mean().round(2).to_string())
jn = {}
for y in range(2007, 2011):
    jn[y] = d[(d.index.year == y) & (d.index.month <= 11)].kwh_adj.mean()
    print(y, "Jan-Nov mean kWh/day", round(jn[y], 2))

# weekly anomalies vs calendar-month median of weekly means
w = d.kwh_adj.resample("W").agg(["mean", "count"])
w = w[w["count"] >= 5]
sea = w["mean"].groupby(w.index.month).transform("median")
r = np.log(w["mean"] / sea)
z = (r - r.median()) / (1.4826 * (r - r.median()).abs().median())
w["z"] = z
ab = w[abs(z) > 2.5]
ab.to_csv(O + "abnormal_weeks.csv"); print("abnormal weeks\n", ab.round(2).to_string())

# Forecast Dec 2010
P = pd.Period
dm = {y: m.loc[P(str(y) + "-12"), "mean_day"] for y in (2006, 2007, 2008, 2009)}
print("Dec mean/day", dm, "Dec kwh", {y: round(m.loc[P(str(y) + "-12"), "kwh_full"]) for y in dm})


def lvl(y, mo):
    return d[(d.index.year == y) & (d.index.month <= mo)].kwh_adj.mean()


def est(target, priors):
    # scale prior-year Decembers by ratio of Jan-Nov level
    return [dm[p] * lvl(target, 11) / lvl(p, 11) * 31 for p in priors]


e1 = est(2010, (2007, 2008, 2009))
# alternative: last-3-months level ratio
def lvl3(y):
    return d[(d.index.year == y) & (d.index.month.isin([9, 10, 11]))].kwh_adj.mean()
e2 = [dm[p] * lvl3(2010) / lvl3(p) * 31 for p in (2007, 2008, 2009)]
print("Jan-Nov ratio ests", np.round(e1), "Sep-Nov ratio ests", np.round(e2))
bt = []
for ty, prior in ((2008, [2007]), (2009, [2007, 2008])):
    pred = np.mean(est(ty, prior)); act = m.loc[P(str(ty) + "-12"), "kwh_full"]
    bt.append((ty, pred, act, pred / act - 1))
print("backtest", bt)
# point: 2008-09 Decembers scaled to the 2010 level (Dec 2007 looks atypically high)
point = np.mean(e1[1:] + e2[1:])
ratio = np.array([dm[y] / lvl(y, 11) for y in (2007, 2008, 2009)])
cv = ratio.std(ddof=1) / ratio.mean()
print("Dec/level ratios", ratio, "cv", cv)
sd_tot = cv * point
lo, hi = point - 1.96 * sd_tot, point + 1.96 * sd_tot
print("POINT", point, "sd", sd_tot, "range", lo, hi)
pd.DataFrame({"point": [point], "lo95": [lo], "hi95": [hi], "sd": [sd_tot]}).to_csv(O + "forecast.csv", index=False)

fig, ax = plt.subplots(2, 1, figsize=(11, 7))
ax[0].plot(m.index.to_timestamp(), m.kwh_full, marker="o", ms=3, color="#2a6fb0")
ax[0].errorbar([pd.Timestamp("2010-12-01")], [point], yerr=[[point - lo], [hi - point]], fmt="s", color="#d1495b", capsize=5, label="Dec 2010 forecast (95%)")
ax[0].set_title("Monthly energy (kWh; missing minutes filled at the month's mean daily use)"); ax[0].set_ylabel("kWh"); ax[0].legend()
ax[1].plot(d.index, d.kwh_adj, lw=.4, color="#555")
ax[1].plot(d.kwh_adj.rolling(28, min_periods=14).mean(), color="#d1495b", lw=1.5, label="28-day mean")
ax[1].set_title("Daily energy (kWh)"); ax[1].legend()
plt.tight_layout(); plt.savefig(O + "trend.png", dpi=120); plt.close()
fig, ax = plt.subplots(1, 3, figsize=(14, 4))
ax[0].bar(h.index, h.values, color="#2a6fb0"); ax[0].set_title("Avg power by hour (kW)")
ax[1].bar(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], dow.values, color="#2a6fb0"); ax[1].set_title("Avg kWh/day by weekday")
ax[2].bar(mon.index, mon.values, color="#2a6fb0"); ax[2].set_title("Avg kWh/day by month (2007-09)"); ax[2].set_xticks(range(1, 13))
plt.tight_layout(); plt.savefig(O + "seasonality.png", dpi=120)
