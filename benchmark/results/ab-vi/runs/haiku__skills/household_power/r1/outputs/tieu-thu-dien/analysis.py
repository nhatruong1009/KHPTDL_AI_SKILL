"""Phân tích tiêu thụ điện năng hộ gia đình (dữ liệu phút, 16/12/2006 - 26/11/2010).

Chạy từ thư mục gốc workspace:  python outputs/tieu-thu-dien/analysis.py
Dữ liệu gốc chỉ đọc. Mọi kết quả ghi vào outputs/tieu-thu-dien/.
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

OUT = "outputs/tieu-thu-dien"
os.makedirs(OUT, exist_ok=True)
DATA = "data/household_power_consumption.txt"

# ---------------------------------------------------------------- 1. Nạp dữ liệu
raw = pd.read_csv(DATA, sep=";", na_values="?", low_memory=False)
raw["dt"] = pd.to_datetime(raw["Date"] + " " + raw["Time"], format="%d/%m/%Y %H:%M:%S")
df = raw[["dt", "Global_active_power"]].rename(columns={"Global_active_power": "kW"}).set_index("dt")
df = df.sort_index()
full_idx = pd.date_range(df.index.min(), df.index.max(), freq="min")
n_expected = len(full_idx)
n_missing_minutes = int(df["kW"].isna().sum())
print(f"Số phút kỳ vọng: {n_expected:,}; số dòng: {len(df):,}; phút thiếu giá trị: {n_missing_minutes:,}")

# Chuỗi phút đầy đủ, đánh dấu NaN
s = df["kW"].reindex(full_idx)

# Khoảng trống dữ liệu liên tục (run of NaN)
is_na = s.isna().astype(int)
run_id = (is_na.diff() != 0).cumsum()
runs = (
    pd.DataFrame({"na": is_na, "run": run_id, "t": s.index.to_series()})
    .query("na == 1")
    .groupby("run")
    .agg(bat_dau=("t", "min"), ket_thuc=("t", "max"), so_phut=("t", "size"))
    .sort_values("so_phut", ascending=False)
)
runs["so_gio"] = (runs["so_phut"] / 60).round(2)
runs.to_csv(f"{OUT}/khoang_trong_du_lieu.csv", index=False)
print("Top 10 khoảng trống dài nhất:")
print(runs.head(10).to_string())
print(f"Số khoảng trống >= 60 phút: {(runs['so_phut'] >= 60).sum()}; "
      f"tổng phút trong khoảng >=60 phút: {runs.loc[runs['so_phut']>=60,'so_phut'].sum():,}")

# ---------------------------------------------------------------- 2. Ngày
# kWh/ngày ước lượng = 24 * trung bình công suất (kW) trên các phút có dữ liệu.
# Cách này không phụ thuộc vào tỉ lệ phút thiếu (giả định thiếu ngẫu nhiên).
daily = pd.DataFrame({
    "kwh_ngay": s.resample("D").mean() * 24,
    "phut_co_so_lieu": s.resample("D").count(),
})
daily["do_phu"] = daily["phut_co_so_lieu"] / 1440
daily_full = daily[daily["do_phu"] >= 0.5].copy()  # loại ngày phủ dữ liệu <50%
daily_full.to_csv(f"{OUT}/tong_hop_ngay.csv")
print(f"Số ngày: {len(daily)}; ngày phủ >=50%: {len(daily_full)}; ngày phủ <50%: {len(daily)-len(daily_full)}")
gap_days = daily[daily["do_phu"] < 0.5]
print("Các ngày phủ <50% (dữ liệu thiếu):")
print(gap_days.index.strftime("%Y-%m-%d").tolist())

# ---------------------------------------------------------------- 3. Tháng
monthly = pd.DataFrame({
    "kwh_trung_binh_ngay": daily_full["kwh_ngay"].resample("MS").mean(),
    "so_ngay_du_lieu": daily_full["kwh_ngay"].resample("MS").count(),
})
monthly["so_ngay_thang"] = monthly.index.days_in_month
monthly["ngay_co_du_lieu_het_thang"] = monthly["so_ngay_du_lieu"] == monthly["so_ngay_thang"]
monthly["tong_kwh_uoc_luong"] = monthly["kwh_trung_binh_ngay"] * monthly["so_ngay_thang"]
# Tháng đầy đủ: không có ngày nào bị loại và không phải tháng đầu/cuối bị cắt
first_month, last_month = monthly.index.min(), monthly.index.max()
monthly["day_du"] = monthly["so_ngay_du_lieu"] == monthly["so_ngay_thang"]
monthly.loc[monthly.index == first_month, "day_du"] = False  # tháng 12/2006 bắt đầu 16/12
monthly.loc[monthly.index == last_month, "day_du"] = False   # tháng 11/2010 kết thúc 26/11
monthly.round(3).to_csv(f"{OUT}/tong_hop_thang.csv")
print(monthly.round(2).to_string())

# ---------------------------------------------------------------- 4. Xu hướng
mfull = monthly[monthly["day_du"]].copy()
mfull["t"] = np.arange(len(mfull))
slope, intercept = np.polyfit(mfull["t"], mfull["kwh_trung_binh_ngay"], 1)
# Trend KHÔNG dùng OLS trên mọi tháng (bị nhiễu bởi mùa vụ và tháng bị cắt).
# So sánh cùng kỳ: các tháng 1-10 đầy đủ của mỗi năm 2007-2010.
jan_oct = monthly[(monthly.index.month <= 10) & (monthly.index.year >= 2007) & (monthly.index.year <= 2010)]
jan_oct = jan_oct[jan_oct["so_ngay_du_lieu"] >= 20]
pv = pd.DataFrame({"nam": jan_oct.index.year, "thang": jan_oct.index.month,
                   "v": jan_oct["kwh_trung_binh_ngay"].values}).pivot(index="thang", columns="nam", values="v")
pv_common = pv.dropna()
yearly = pv_common.mean()
yearly_ratio = yearly / yearly.loc[2007]
pv.round(3).to_csv(f"{OUT}/so_sanh_cung_ky_thang_1_10.csv")
print("TB kWh/ngày cùng kỳ tháng 1-10 theo năm:")
print(yearly.round(2).to_string())
print("Tỉ lệ so với 2007:", yearly_ratio.round(3).to_dict())
print(f"OLS trên mọi tháng (tham khảo, không dùng để kết luận): {slope:.4f} kWh/ngày mỗi tháng")

# Chỉ số mùa vụ tháng (tỉ lệ so với TB tháng cả giai đoạn) - cần cân bằng theo xu hướng
mfull["tb_nam_theo_thang"] = mfull.groupby(mfull.index.year)["kwh_trung_binh_ngay"].transform("mean")
mfull["chi_so_thang"] = mfull["kwh_trung_binh_ngay"] / mfull["tb_nam_theo_thang"]
season_month = mfull.groupby(mfull.index.month)["chi_so_thang"].mean()
season_month.index = ["T%02d" % m for m in season_month.index]
print("Chỉ số mùa vụ theo tháng (1 = trung bình năm):")
print(season_month.round(3).to_string())

# ---------------------------------------------------------------- 5. Mùa vụ ngày / tuần
dfull = daily_full.copy()
dfull["thu"] = dfull.index.dayofweek  # 0=Thứ Hai
dow_names = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]
dow = dfull.groupby("thu")["kwh_ngay"].agg(["mean", "median", "count"])
dow.index = dow_names
dow.round(3).to_csv(f"{OUT}/mua_vu_thu_trong_tuan.csv")
print("kWh/ngày theo thứ:")
print(dow.round(2).to_string())

# Giờ trong ngày (công suất TB theo giờ và thứ) - dùng toàn bộ phút
hourly_df = pd.DataFrame({"kW": s.dropna()})
hourly_df["gio"] = hourly_df.index.hour
hourly_df["thu"] = hourly_df.index.dayofweek
hour_profile = hourly_df.groupby("gio")["kW"].mean()
hour_profile.round(4).to_csv(f"{OUT}/mua_vu_gio_trong_ngay.csv", header=["kW_trung_binh"])
heat = hourly_df.groupby(["thu", "gio"])["kW"].mean().unstack("gio")
heat.index = dow_names
print("Giờ cao điểm (kW TB):", hour_profile.idxmax(), round(hour_profile.max(), 3),
      "; giờ thấp nhất:", hour_profile.idxmin(), round(hour_profile.min(), 3))

# Chuỗi tuần (Thứ Hai - Chủ Nhật) - ngày đầy đủ
weekly = dfull["kwh_ngay"].resample("W-SUN").agg(["mean", "count"])
weekly.columns = ["kwh_trung_binh_ngay", "so_ngay"]
weekly = weekly[weekly["so_ngay"] == 7]  # chỉ tuần đủ 7 ngày
med = weekly["kwh_trung_binh_ngay"].median()
mad = (weekly["kwh_trung_binh_ngay"] - med).abs().median() * 1.4826
weekly["z_robust"] = (weekly["kwh_trung_binh_ngay"] - med) / mad
weekly["bat_thuong"] = weekly["z_robust"].abs() > 2.5
weekly.round(3).to_csv(f"{OUT}/tuan_bat_thuong.csv")
print(f"Tuần đủ 7 ngày: {len(weekly)}; median={med:.2f}; MAD*1.4826={mad:.2f}")
print("Tuần bất thường (|z|>2.5):")
print(weekly[weekly["bat_thuong"]].round(2).to_string())

# Ngày bất thường (z robust theo tuần-thứ, bỏ ngày trong tuần bất thường không cần thiết)
dfull["z_robust"] = np.nan
for thu_i in range(7):
    sub = dfull[dfull["thu"] == thu_i]["kwh_ngay"]
    m_ = sub.median()
    md = (sub - m_).abs().median() * 1.4826
    dfull.loc[dfull["thu"] == thu_i, "z_robust"] = (sub - m_) / md
ngay_bat_thuong = dfull[dfull["z_robust"].abs() > 3][["kwh_ngay", "thu", "z_robust"]]
ngay_bat_thuong.round(3).to_csv(f"{OUT}/ngay_bat_thuong.csv")
print(f"Số ngày bất thường (|z|>3 trong cùng thứ): {len(ngay_bat_thuong)}")
print(ngay_bat_thuong.sort_values("kwh_ngay", ascending=False).head(15).round(2).to_string())

# ---------------------------------------------------------------- 6. Dự báo tháng 12/2010
# Phương pháp: kWh/ngày(t) = kWh/ngày(cùng tháng năm trước) * tỉ lệ YoY,
# tỉ lệ YoY = tổng(TB ngày các tháng đã biết trong năm) / tổng(cùng tháng năm trước).
# Backtest cùng phương pháp để ước lượng sai số và khoảng bất định.
# Tháng bất thường (vắng nhà, tiêu thụ nền ~0.19 kW suốt 6-30/08/2008): loại khỏi ratio và backtest
ANOMALY_MONTHS = {(2008, 8)}
EXCLUDE_TARGETS = {(2008, 8), (2009, 8)}  # 09/2009 dùng 08/2008 làm mốc YoY nên cũng bị loại

def yoy_forecast(mdaily, year, month):
    """Dự báo kWh/ngày trung bình tháng (year, month) từ dữ liệu trước đó."""
    prev = mdaily.copy()
    base_key = (year - 1, month)
    if base_key not in prev.index or base_key in ANOMALY_MONTHS:
        return np.nan
    same_year_known = [(year, m) for m in range(1, month) if (year, m) in prev.index]
    pairs = [(y, m) for (y, m) in same_year_known if (y - 1, m) in prev.index
             and (y, m) not in ANOMALY_MONTHS and (y - 1, m) not in ANOMALY_MONTHS]
    if len(pairs) < 3:
        return np.nan
    cur = np.array([prev.loc[p] for p in pairs])
    base = np.array([prev.loc[(p[0] - 1, p[1])] for p in pairs])
    ratio = cur.sum() / base.sum()
    return prev.loc[base_key] * ratio

# Chuỗi tháng: dùng mọi tháng có ít nhất 20 ngày dữ liệu (để xử lý tháng 12/2006 & 11/2010)
mdaily = (
    monthly[monthly["so_ngay_du_lieu"] >= 20]["kwh_trung_binh_ngay"]
)
mdaily.index = pd.MultiIndex.from_arrays([mdaily.index.year, mdaily.index.month])
mdaily.index.names = ["nam", "thang"]

bt = []
for (y, m) in mdaily.index:
    if (y, m) < (2008, 2) or (y, m) > (2010, 11) or (y, m) in EXCLUDE_TARGETS:
        continue
    fc = yoy_forecast(mdaily, y, m)
    if np.isnan(fc):
        continue
    actual = mdaily.loc[(y, m)]
    bt.append({"nam": y, "thang": m, "thuc_te_kwh_ngay": actual, "du_bao_kwh_ngay": fc,
               "log_sai_so": np.log(actual / fc)})
bt = pd.DataFrame(bt)
bt.round(4).to_csv(f"{OUT}/backtest_du_bao.csv", index=False)
q05, q95 = bt["log_sai_so"].quantile([0.05, 0.95])
sd_log = bt["log_sai_so"].std()
print(f"Backtest: {len(bt)} tháng; sai số log: TB={bt['log_sai_so'].mean():.4f}, "
      f"SD={sd_log:.4f}, 5%={q05:.4f}, 95%={q95:.4f}")
print(f"MAPE backtest: {(np.abs(np.exp(bt['log_sai_so'])-1)).mean()*100:.2f}%")
# Độ nhạy: chỉ các tháng mùa đông/đầu-cuối năm (10-2), gần với tháng 12
bt_w = bt[bt["thang"].isin([10, 11, 12, 1, 2])]
q05w, q95w = bt_w["log_sai_so"].quantile([0.05, 0.95])
sd_w = bt_w["log_sai_so"].std()
print(f"Backtest mùa đông ({len(bt_w)} tháng): SD={sd_w:.4f}, 5%={q05w:.4f}, 95%={q95w:.4f}, "
      f"MAPE={(np.abs(np.exp(bt_w['log_sai_so'])-1)).mean()*100:.2f}%")
print(bt.round(3).to_string())

target = (2010, 12)
fc_daily = yoy_forecast(mdaily, *target)
ndays_dec = 31
point_kwh = fc_daily * ndays_dec
# Khoảng 90% dựa trên phân vị thực nghiệm của sai số backtest
lo_kwh = point_kwh * np.exp(q05)
hi_kwh = point_kwh * np.exp(q95)
# Thêm khoảng bất định chuẩn (log-normal) để so sánh
lo_norm = point_kwh * np.exp(-1.645 * sd_log)
hi_norm = point_kwh * np.exp(1.645 * sd_log)

# Các thành phần để minh bạch
ratio_2010 = mdaily.loc[[(2010, m) for m in range(1, 12) if (2010, m) in mdaily.index]].sum() / \
             mdaily.loc[[(2009, m) for m in range(1, 12) if (2010, m) in mdaily.index]].sum()
base_dec09 = mdaily.loc[(2009, 12)]
forecast = pd.DataFrame([{
    "muc_tieu": "Tháng 12/2010",
    "kwh_trung_binh_ngay_TB_12_2009": round(base_dec09, 3),
    "ty_le_YoY_2010_vs_2009": round(ratio_2010, 4),
    "kwh_ngay_du_bao": round(fc_daily, 3),
    "tong_kwh_du_bao_31_ngay": round(point_kwh, 1),
    "khoang_90pct_empirical_thap": round(lo_kwh, 1),
    "khoang_90pct_empirical_cao": round(hi_kwh, 1),
    "khoang_90pct_lognormal_thap": round(lo_norm, 1),
    "khoang_90pct_lognormal_cao": round(hi_norm, 1),
    "so_thang_backtest": len(bt),
    "MAPE_backtest_pct": round((np.abs(np.exp(bt['log_sai_so'])-1)).mean()*100, 2),
}])
forecast.to_csv(f"{OUT}/du_bao_thang_12_2010.csv", index=False)
print(forecast.T.to_string())

# Các ngày thực tế tháng 12 đã có (kiểm tra sanity): Dec 2006 chỉ 16-31; Dec 2007-2009
dec_actual = monthly[monthly.index.month == 12][["kwh_trung_binh_ngay", "tong_kwh_uoc_luong", "so_ngay_du_lieu"]]
print("Các tháng 12 trước đó:")
print(dec_actual.round(2).to_string())

# ---------------------------------------------------------------- 7. Biểu đồ
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False})

# (a) Tổng kWh theo tháng (chuẩn hoá theo số ngày)
fig, ax = plt.subplots(figsize=(11, 4.6))
mm = monthly[monthly["so_ngay_du_lieu"] >= 1]
colors = np.where(mm["day_du"], "#2b6cb0", "#a0aec0")
ax.bar(mm.index, mm["tong_kwh_uoc_luong"], width=24, color=colors)
ax.plot(mm.index, mm["tong_kwh_uoc_luong"], color="#1a365d", lw=1, alpha=0.6)
ax.set_title("Tổng điện năng theo tháng (kWh, ước lượng cho đủ số ngày)")
ax.set_ylabel("kWh / tháng")
ax.set_xlabel("Tháng")
ax.text(0.99, 0.95, "Xám: tháng bị cắt (đầu 12/2006, cuối 11/2010)", transform=ax.transAxes,
        ha="right", va="top", fontsize=8, color="#4a5568")
fig.tight_layout()
fig.savefig(f"{OUT}/bieu_do_tong_thang.png", dpi=140)
plt.close(fig)

# (b) Chuỗi ngày + trung bình trượt 30 ngày + ngày bất thường
fig, ax = plt.subplots(figsize=(11, 4.6))
ax.plot(daily_full.index, daily_full["kwh_ngay"], color="#a0aec0", lw=0.6, label="kWh/ngày")
roll = daily_full["kwh_ngay"].rolling(30, center=True, min_periods=15).mean()
ax.plot(roll.index, roll, color="#1a365d", lw=2, label="Trung bình trượt 30 ngày")
out = ngay_bat_thuong.index
ax.scatter(out, ngay_bat_thuong["kwh_ngay"], color="#e53e3e", s=14, zorder=3, label="Ngày bất thường (|z|>3)")
gaps = gap_days.index
ax.scatter(gaps, np.zeros(len(gaps)) + 0.2, marker="|", color="#dd6b20", s=40, label="Ngày thiếu dữ liệu (<50%)")
ax.set_title("Điện năng hằng ngày và xu hướng")
ax.set_ylabel("kWh / ngày")
ax.set_xlabel("Ngày")
ax.legend(loc="upper right", fontsize=8, frameon=False)
fig.tight_layout()
fig.savefig(f"{OUT}/bieu_do_ngay.png", dpi=140)
plt.close(fig)

# (c) Mùa vụ tháng và thứ trong tuần
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
axes[0].bar(season_month.index, season_month.values, color="#2b6cb0")
axes[0].axhline(1, color="#4a5568", lw=0.8, ls="--")
axes[0].set_title("Mùa vụ theo tháng (chỉ số, 1 = TB năm)")
axes[0].set_ylabel("Chỉ số")
axes[0].tick_params(axis="x", rotation=0)
axes[1].bar(dow.index, dow["mean"], color="#2c7a7b")
axes[1].set_title("kWh/ngày theo thứ trong tuần")
axes[1].set_ylabel("kWh / ngày (TB)")
fig.tight_layout()
fig.savefig(f"{OUT}/bieu_do_mua_vu.png", dpi=140)
plt.close(fig)

# (d) Heatmap thứ x giờ
fig, ax = plt.subplots(figsize=(10, 3.8))
im = ax.imshow(heat.values, aspect="auto", cmap="YlOrRd")
ax.set_xticks(range(24))
ax.set_xticklabels(range(24))
ax.set_yticks(range(7))
ax.set_yticklabels(dow_names)
ax.set_xlabel("Giờ trong ngày")
ax.set_title("Công suất trung bình (kW) theo thứ và giờ")
cb = fig.colorbar(im, ax=ax)
cb.set_label("kW")
fig.tight_layout()
fig.savefig(f"{OUT}/bieu_do_heatmap_thu_gio.png", dpi=140)
plt.close(fig)

# (e) Dự báo tháng 12/2010 cùng lịch sử tháng 12 và backtest
fig, ax = plt.subplots(figsize=(10, 4.4))
hist = mdaily.copy()
idx = [pd.Timestamp(y, m, 1) for (y, m) in hist.index]
ax.plot(idx, hist.values, color="#2b6cb0", marker="o", ms=3, lw=1, label="TB kWh/ngày (thực tế)")
ax.scatter([pd.Timestamp(2010, 12, 1)], [fc_daily], color="#dd6b20", s=60, zorder=4, label="Dự báo 12/2010")
ax.vlines(pd.Timestamp(2010, 12, 1), fc_daily * np.exp(q05), fc_daily * np.exp(q95), color="#dd6b20", lw=2)
ax.set_title("Trung bình kWh/ngày theo tháng và dự báo tháng 12/2010")
ax.set_ylabel("kWh / ngày (TB tháng)")
ax.set_xlabel("Tháng")
ax.legend(fontsize=8, frameon=False)
fig.tight_layout()
fig.savefig(f"{OUT}/bieu_do_du_bao.png", dpi=140)
plt.close(fig)

print("Hoàn tất. File đầu ra:", sorted(os.listdir(OUT)))
