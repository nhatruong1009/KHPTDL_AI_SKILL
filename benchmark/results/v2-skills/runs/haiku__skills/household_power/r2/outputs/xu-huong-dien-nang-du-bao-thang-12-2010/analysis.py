"""Xu hướng, mùa vụ, bất thường và dự báo tổng điện năng tháng 12/2010.

Dữ liệu: household_power_consumption.txt (phút, 12/2006 - 11/2010).
Global_active_power là công suất trung bình (kW) trong 1 phút.
=> năng lượng 1 phút = kW / 60 (kWh); năng lượng ngày ước tính = kW trung bình ngày × 24 (kWh).
"""
import os
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DATA = os.path.join(ROOT, "data", "household_power_consumption.txt")
GOOD_COV = 0.8      # ngày "đủ dữ liệu" nếu >= 80% số phút có giá trị
FULL_MONTH_COV = 0.9  # tháng "đủ" để dùng cho xu hướng nếu >= 90% số ngày đủ dữ liệu

# ---------------------------------------------------------------- 1. Nạp dữ liệu
raw = pd.read_csv(DATA, sep=";", na_values=["?"], low_memory=False)
raw["ts"] = pd.to_datetime(raw["Date"] + " " + raw["Time"], format="%d/%m/%Y %H:%M:%S")
n_dup = int(raw["ts"].duplicated().sum())
df = raw.drop(columns=["Date", "Time"]).set_index("ts").sort_index()

grid = pd.date_range(df.index.min(), df.index.max(), freq="min")
absent = ~grid.isin(df.index)          # phút hoàn toàn không có dòng
full = df.reindex(grid)
kw = full["Global_active_power"]
valid = kw.notna()

summary = {
    "rows_raw": int(len(raw)),
    "duplicate_timestamps": n_dup,
    "start": str(grid[0]), "end": str(grid[-1]),
    "minutes_expected": int(len(grid)),
    "minutes_absent": int(absent.sum()),
    "minutes_nan_value": int((~absent & ~valid.values).sum()),
    "pct_minutes_valid": float(valid.mean() * 100),
}

# ---------------------------------------------------------------- 2. Khoảng trống (gap)
bad = ~valid
run_id = (bad != bad.shift()).cumsum()
runs = pd.DataFrame({"bad": bad.values, "absent": absent, "run": run_id.values, "ts": grid})
g = runs.groupby("run").agg(bad=("bad", "first"), absent=("absent", "mean"),
                            start=("ts", "first"), end=("ts", "last"), minutes=("ts", "size"))
gaps = g[g["bad"].astype(bool) & (g["minutes"] >= 60)].copy()
gaps["loai"] = np.where(gaps["absent"] > 0.5, "không có dòng dữ liệu", "giá trị thiếu (NaN)")
gaps = gaps.sort_values("minutes", ascending=False)
gaps["ngay"] = (gaps["minutes"] / 1440).round(2)
gaps[["start", "end", "minutes", "ngay", "loai"]].to_csv(os.path.join(HERE, "gaps_ge_1h.csv"))
summary["gaps_ge_1h_count"] = int(len(gaps))
summary["gaps_ge_1h_total_days"] = float(gaps["ngay"].sum())

# ---------------------------------------------------------------- 3. Chuỗi ngày
daily = pd.DataFrame({
    "kw_tb": kw.resample("D").mean(),
    "cov": valid.resample("D").mean(),
})
daily["kwh"] = daily["kw_tb"] * 24
good = daily[daily["cov"] >= GOOD_COV].copy()
good["dow"] = good.index.dayofweek
good["thang"] = good.index.month
daily.to_csv(os.path.join(HERE, "daily_all.csv"))
summary["days_total"] = int(len(daily))
summary["days_good"] = int(len(good))

# Tháng: trung bình kWh/ngày × số ngày trong tháng (ước tính đã hiệu chỉnh thiếu)
good["ym"] = good.index.to_period("M")
all_months = pd.period_range(grid[0].to_period("M"), grid[-1].to_period("M"), freq="M")
mon = good.groupby("ym").agg(kwh_tb=("kwh", "mean"), ngay_du=("kwh", "size")).reindex(all_months)
mon["ngay_trong_thang"] = [p.days_in_month for p in mon.index]
mon["tong_kwh"] = mon["kwh_tb"] * mon["ngay_trong_thang"]
mon["ty_le_ngay_du"] = mon["ngay_du"] / mon["ngay_trong_thang"]
mon["thang_du"] = mon["ty_le_ngay_du"] >= FULL_MONTH_COV
mon.to_csv(os.path.join(HERE, "monthly.csv"))

# Khối 12 tháng bắt đầu từ tháng 12 (để so sánh cùng mùa vụ)
blk = np.where(good.index.month == 12, good.index.year, good.index.year - 1)
good["khoi"] = blk
blocks = good.groupby("khoi").agg(kwh_ngay_tb=("kwh", "mean"), ngay_du=("kwh", "size"))
blocks["nhan"] = [f"12/{y} - 11/{y + 1}" for y in blocks.index]
blocks.to_csv(os.path.join(HERE, "yearly_blocks.csv"))

# Xu hướng tuyến tính theo tháng đủ dữ liệu (tham khảo, có lẫn mùa vụ)
mf = mon[mon["thang_du"]].copy()
t_years = (mf.index.to_timestamp() - pd.Timestamp("2006-12-01")).days.values / 365.25
slope, intercept = np.polyfit(t_years, mf["tong_kwh"].values, 1)
summary["trend_kwh_per_year"] = float(slope)
summary["trend_pct_per_year"] = float(slope / mf["tong_kwh"].mean() * 100)

# ---------------------------------------------------------------- 4. Mùa vụ
seas_month = good.groupby("thang")["kwh"].mean()
seas_dow = good.groupby("dow")["kwh"].mean()
hourly = kw.groupby(kw.index.hour).mean()   # kW trung bình = kWh/giờ
seas_month.to_csv(os.path.join(HERE, "seasonal_month.csv"))
seas_dow.to_csv(os.path.join(HERE, "seasonal_weekday.csv"))
hourly.to_csv(os.path.join(HERE, "seasonal_hour.csv"))

# ---------------------------------------------------------------- 5. Bất thường
# 5a. Ngày: so với trung vị cùng thứ trong tuần (cửa sổ 9 tuần), z robust
good["nen"] = good.groupby("dow")["kwh"].transform(
    lambda s: s.rolling(9, center=True, min_periods=5).median())
good["resid"] = good["kwh"] - good["nen"]
mad = 1.4826 * np.nanmedian(np.abs(good["resid"] - np.nanmedian(good["resid"])))
good["z"] = good["resid"] / mad
anom_d = good[good["z"].abs() > 3][["kwh", "nen", "z", "cov"]].copy()
anom_d = anom_d.reindex(anom_d["z"].abs().sort_values(ascending=False).index)
anom_d.to_csv(os.path.join(HERE, "anomalies_daily.csv"))
summary["anom_daily_count"] = int(len(anom_d))

# 5b. Tuần: trung bình kWh/ngày theo tuần, so với trung vị 9 tuần
wk = good.resample("W-SUN").agg(kwh_ngay_tb=("kwh", "mean"), ngay_du=("kwh", "size"))
wk = wk[wk["ngay_du"] >= 5].copy()
wk["nen"] = wk["kwh_ngay_tb"].rolling(9, center=True, min_periods=5).median()
wk["resid"] = wk["kwh_ngay_tb"] - wk["nen"]
mad_w = 1.4826 * np.nanmedian(np.abs(wk["resid"] - np.nanmedian(wk["resid"])))
wk["z"] = wk["resid"] / mad_w
anom_w = wk[wk["z"].abs() > 3].copy()
anom_w = anom_w.reindex(anom_w["z"].abs().sort_values(ascending=False).index)
anom_w.to_csv(os.path.join(HERE, "anomalies_weekly.csv"))
summary["anom_weekly_count"] = int(len(anom_w))

# ---------------------------------------------------------------- 6. Dự báo
ORIGIN = pd.Timestamp("2006-12-01")
K = 3

def features(idx):
    t = (idx - ORIGIN).days.values / 365.25
    doy = idx.dayofyear.values
    cols = [np.ones(len(idx)), t]
    for k in range(1, K + 1):
        cols += [np.sin(2 * np.pi * k * doy / 365.25), np.cos(2 * np.pi * k * doy / 365.25)]
    dow = idx.dayofweek.values
    for d in range(1, 7):
        cols.append((dow == d).astype(float))
    return np.column_stack(cols)

def fit_predict(train, future_idx):
    beta, *_ = np.linalg.lstsq(features(train.index), train["kwh"].values, rcond=None)
    return features(future_idx) @ beta

# Backtest: mỗi tháng từ 01/2008 đến 10/2010 làm gốc dự báo cho cả tháng kế tiếp
rows = []
for o in pd.date_range("2008-01-01", "2010-10-01", freq="MS"):
    train = good[good.index < o]
    m_end = o + pd.offsets.MonthEnd(0)
    fut = pd.date_range(o, m_end, freq="D")
    act = good[(good.index >= o) & (good.index <= m_end)]
    if len(train) < 365 or len(act) < 0.9 * len(fut):
        continue
    actual = act["kwh"].mean() * len(fut)
    pred = fit_predict(train, fut).sum()
    prev = mon["tong_kwh"].get(o.to_period("M") - 12, np.nan)   # cùng tháng năm trước
    base_last30 = train["kwh"].tail(30).mean() * len(fut)
    rows.append({"thang": o.strftime("%Y-%m"), "thuc_te": actual, "du_bao": pred,
                 "naive_cung_thang_nam_truoc": prev, "naive_30_ngay": base_last30})
bt = pd.DataFrame(rows).set_index("thang")
for c, lab in [("du_bao", "mo_hinh"), ("naive_cung_thang_nam_truoc", "naive_nam_truoc"),
               ("naive_30_ngay", "naive_30_ngay")]:
    bt[f"pe_{lab}"] = (bt[c] - bt["thuc_te"]) / bt["thuc_te"]
bt.to_csv(os.path.join(HERE, "backtest.csv"))
mape = {lab: float(bt[f"pe_{lab}"].abs().mean() * 100)
        for lab in ["mo_hinh", "naive_nam_truoc", "naive_30_ngay"]}
mape_dec = {lab: float(bt.loc[bt.index.str.endswith("-12") | bt.index.str.endswith("-11"), f"pe_{lab}"].abs().mean() * 100)
            for lab in []}
pe = bt["pe_mo_hinh"]
q05, q95 = float(pe.quantile(0.05)), float(pe.quantile(0.95))
summary["backtest_n"] = int(len(bt))
summary["backtest_mape_pct"] = mape
summary["backtest_pe_q05_q95"] = [q05, q95]
# Độ nhạy: bỏ tháng 08/2008 (ngoại lệ, ~6.6 kWh/ngày) và chỉ dùng gốc dự báo từ 2009
ex = bt.drop(index="2008-08")
summary["sens_ex_aug2008_mape_pct"] = {lab: float(ex[f"pe_{lab}"].abs().mean() * 100)
                                       for lab in ["mo_hinh", "naive_nam_truoc", "naive_30_ngay"]}
summary["sens_ex_aug2008_pe_q05_q95"] = [float(ex["pe_mo_hinh"].quantile(0.05)),
                                         float(ex["pe_mo_hinh"].quantile(0.95))]
late = bt[bt.index >= "2009-01"]
summary["sens_from2009_n"] = int(len(late))
summary["sens_from2009_mape_pct"] = float(late["pe_mo_hinh"].abs().mean() * 100)
summary["sens_from2009_pe_q05_q95"] = [float(late["pe_mo_hinh"].quantile(0.05)),
                                       float(late["pe_mo_hinh"].quantile(0.95))]
summary["backtest_dec_rows"] = bt.loc[[i for i in bt.index if i.endswith("-12")], ["thuc_te", "du_bao", "pe_mo_hinh"]].round(4).to_dict("index") if any(i.endswith("-12") for i in bt.index) else {}

# Dự báo tháng 12/2010 dùng toàn bộ ngày đủ dữ liệu
fut12 = pd.date_range("2010-12-01", "2010-12-31", freq="D")
pred12 = fit_predict(good, fut12)
total12 = float(pred12.sum())
# Khoảng: từ sai số backtest (actual ≈ pred / (1+pe))
lo12 = total12 / (1 + q95)
hi12 = total12 / (1 + q05)
f12 = pd.DataFrame({"ngay": fut12.strftime("%Y-%m-%d"), "du_bao_kwh": pred12})
f12.to_csv(os.path.join(HERE, "forecast_dec2010_daily.csv"), index=False)
summary["forecast_dec2010"] = {"diem": total12, "khoang_90_lo": lo12, "khoang_90_hi": hi12,
                              "kwh_ngay_tb_du_bao": total12 / 31,
                              "ngay_du_lieu_cuoi_dung_de_huan_luyen": str(good.index.max().date()),
                              "so_ngay_huan_luyen": int(len(good))}
pd.DataFrame([{"thang": "2010-12", "du_bao_kwh": total12, "khoang_lo_90": lo12, "khoang_hi_90": hi12}]) \
    .to_csv(os.path.join(HERE, "forecast_dec2010.csv"), index=False)

# ---------------------------------------------------------------- 7. Biểu đồ
plt.rcParams.update({"figure.dpi": 110, "axes.spines.top": False, "axes.spines.right": False})

# Biểu đồ 1: chuỗi ngày + trung bình trượt + bất thường
fig, ax = plt.subplots(figsize=(12, 4.8))
ax.plot(good.index, good["kwh"], color="#b0b8c4", lw=0.6, label="kWh/ngày (ngày đủ dữ liệu)")
roll = good["kwh"].rolling("28D", min_periods=14).mean()
ax.plot(roll.index, roll, color="#1f4e79", lw=2, label="Trung bình trượt 28 ngày")
ax.scatter(anom_d.index, anom_d["kwh"], color="#c00000", s=18, zorder=3, label=f"Ngày bất thường (|z|>3): {len(anom_d)}")
ax.set_ylabel("kWh/ngày")
ax.legend(frameon=False, ncol=3, loc="upper right", fontsize=9)
ax.set_title("Mức điện/ngày mùa đông ~35–36 kWh, mùa hè ~14–17 kWh; "
             "cả giai đoạn gần như đi ngang (~26 kWh/ngày mỗi năm)", fontsize=11, loc="left")
fig.tight_layout()
fig.savefig(os.path.join(HERE, "chart1_xu_huong_ngay.png"))
plt.close(fig)

# Biểu đồ 2: tổng tháng
fig, ax = plt.subplots(figsize=(12, 4.8))
x = mon.index.to_timestamp()
colors = np.where(mon["thang_du"].fillna(False), "#2e75b6", "#bdd7ee")
ax.bar(x, mon["tong_kwh"], width=25, color=colors)
for xi, yi, ok in zip(x, mon["tong_kwh"], mon["thang_du"].fillna(False)):
    if not ok and not np.isnan(yi):
        ax.text(xi, yi, "*", ha="center", va="bottom", fontsize=10)
ax.set_ylabel("kWh/tháng (ước tính)")
ax.set_title("Tổng điện năng tháng: tháng 12–2 thường 820–1.210 kWh, tháng 7–8 thường 440–600 kWh; "
             "riêng tháng 8/2008 chỉ ~206 kWh", fontsize=11, loc="left")
fig.text(0.01, 0.01, "Ô sáng: tháng đủ dữ liệu ít nhất 90% số ngày; ô nhạt là tháng thiếu/đầu-cuối chuỗi.",
         fontsize=8, color="#555")
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig(os.path.join(HERE, "chart2_thang.png"))
plt.close(fig)

# Biểu đồ 3: mùa vụ (tháng, thứ, giờ)
fig, axes = plt.subplots(1, 3, figsize=(14, 4.2))
mnames = ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10", "T11", "T12"]
axes[0].bar(seas_month.index, seas_month.values, color="#2e75b6")
axes[0].set_xticks(range(1, 13)); axes[0].set_xticklabels(mnames, fontsize=8)
axes[0].set_title("Theo tháng trong năm (kWh/ngày)", fontsize=10)
dnames = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]
axes[1].bar(range(7), seas_dow.values, color="#2e75b6")
axes[1].set_xticks(range(7)); axes[1].set_xticklabels(dnames)
axes[1].set_title("Theo thứ trong tuần (kWh/ngày)", fontsize=10)
axes[2].plot(hourly.index, hourly.values, color="#2e75b6", lw=2)
axes[2].set_xticks(range(0, 24, 3)); axes[2].set_title("Theo giờ trong ngày (kW trung bình)", fontsize=10)
fig.suptitle("Mùa vụ: đỉnh buổi tối (17–21h) và mùa đông; cuối tuần cao hơn ngày thường",
             fontsize=11, x=0.01, ha="left")
fig.tight_layout(rect=(0, 0, 1, 0.93))
fig.savefig(os.path.join(HERE, "chart3_mua_vu.png"))
plt.close(fig)

# Biểu đồ 4: dự báo tháng 12/2010 so với các tháng 12 trước
fig, ax = plt.subplots(figsize=(10, 4.8))
dec_hist = mon[(mon.index.month == 12) & mon["thang_du"]]
labels = [str(p) for p in dec_hist.index] + ["2010-12 (dự báo)"]
vals = list(dec_hist["tong_kwh"].values)
ax.bar(labels[:-1], vals, color="#2e75b6", label="Thực tế (ước tính)")
ax.bar(labels[-1:], [total12], color="#ed7d31", label="Dự báo")
ax.errorbar([labels[-1]], [total12], yerr=[[total12 - lo12], [hi12 - total12]],
            fmt="none", ecolor="black", capsize=6, lw=1.5, label="Khoảng 90%")
for i, v in enumerate(vals + [total12]):
    ax.text(i, v, f"{v:,.0f}", ha="center", va="bottom", fontsize=9)
ax.set_ylabel("kWh trong tháng 12")
ax.set_title(f"Dự báo tháng 12/2010 khoảng {total12:,.0f} kWh (khoảng 90%: {lo12:,.0f}–{hi12:,.0f}), "
             "gần bằng tháng 12/2009 (1.015 kWh)", fontsize=11, loc="left")
ax.set_ylim(0, max(max(vals), hi12) * 1.3)
ax.legend(frameon=False, fontsize=9, loc="upper right", ncol=3)
fig.tight_layout()
fig.savefig(os.path.join(HERE, "chart4_du_bao_thang12_2010.png"))
plt.close(fig)

with open(os.path.join(HERE, "summary.json"), "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2, default=str)

print(json.dumps(summary, ensure_ascii=False, indent=2, default=str))
print("\nBlocks:\n", blocks.round(3).to_string())
print("\nSeasonal month:\n", seas_month.round(2).to_string())
print("\nSeasonal weekday:\n", seas_dow.round(2).to_string())
print("\nHourly kW:\n", hourly.round(3).to_string())
print("\nMonthly:\n", mon[["kwh_tb", "ngay_du", "ngay_trong_thang", "tong_kwh", "ty_le_ngay_du"]].round(2).to_string())
print("\nGaps (>=1h):\n", gaps[["start", "end", "minutes", "ngay", "loai"]].head(20).to_string())
print("\nAnomalies daily:\n", anom_d.head(20).round(2).to_string())
print("\nAnomalies weekly:\n", anom_w.round(2).to_string())
print("\nBacktest:\n", bt.round(3).to_string())
