"""Phân tích tiêu thụ điện hộ gia đình (12/2006 - 11/2010).

Nội dung: xu hướng, mùa vụ (ngày/tuần/năm), khoảng trống dữ liệu, tuần/ngày bất thường,
và dự báo tổng điện năng tháng 12/2010 kèm khoảng bất định.

Đơn vị: Global_active_power là công suất trung bình (kW) trong 1 phút
-> năng lượng của phút đó = kW / 60 (kWh).
Chạy: python outputs/tieu-thu-dien-du-bao-2010-12/analysis.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from scipy import stats  # noqa: E402

HERE = Path(__file__).resolve().parent
WS = HERE.parents[1]
SRC = WS / "data" / "household_power_consumption.txt"
DOW_VI = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]
MON_VI = ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10", "T11", "T12"]


def load():
    raw = pd.read_csv(SRC, sep=";", na_values=["?"], low_memory=False)
    raw.index = pd.to_datetime(raw["Date"] + " " + raw["Time"], format="%d/%m/%Y %H:%M:%S")
    raw = raw.drop(columns=["Date", "Time"]).sort_index()
    n_raw = len(raw)
    n_dup = int(raw.index.duplicated().sum())
    raw = raw[~raw.index.duplicated(keep="first")]
    grid = pd.date_range(raw.index.min(), raw.index.max(), freq="min", name="dt")
    n_absent = int((~grid.isin(raw.index)).sum())
    df = raw.reindex(grid)
    return df, n_raw, n_dup, n_absent


def build_daily(df):
    kwh = df["Global_active_power"] / 60.0
    expected = pd.Series(1, index=df.index).resample("D").sum()
    n_ok = kwh.resample("D").count()
    daily = pd.DataFrame({"n_min": n_ok, "exp_min": expected})
    daily["cov"] = daily["n_min"] / daily["exp_min"]
    daily["valid"] = daily["cov"] >= 0.9
    # Ngày có phút thiếu (<10%): hiệu chỉnh tổng theo tỉ lệ phút có dữ liệu
    daily["kwh"] = np.where(daily["valid"], kwh.resample("D").sum(min_count=1) / daily["cov"], np.nan)
    daily["dow"] = daily.index.dayofweek
    return daily


def build_monthly(daily):
    v = daily[daily["valid"]]
    m = pd.DataFrame({
        "ngay_co_du_lieu": daily["valid"].resample("MS").sum(),
        "so_ngay_trong_thang": daily.index.to_series().resample("MS").size(),
        "tb_kwh_moi_ngay": v["kwh"].resample("MS").mean(),
    })
    m["ngay_lich"] = m.index.days_in_month
    m["complete"] = m["ngay_co_du_lieu"] == m["ngay_lich"]
    m["tong_kwh_uoc_tinh"] = m["tb_kwh_moi_ngay"] * m["ngay_lich"]
    return m


def X_of(t, mon):
    cols = [np.ones(len(t)), t] + [(mon == k).astype(float) for k in range(2, 13)]
    return np.column_stack(cols)


def fit(d):
    X = X_of(d["t"].to_numpy(float), d["mon"].to_numpy())
    y = d["y"].to_numpy(float)
    XtX_inv = np.linalg.inv(X.T @ X)
    b = XtX_inv @ X.T @ y
    res = y - X @ b
    dof = len(y) - X.shape[1]
    s = np.sqrt(res @ res / dof)
    return b, s, XtX_inv, dof


def predict(model, t0, mon0):
    b, s, XtX_inv, dof = model
    x0 = X_of(np.array([t0], float), np.array([mon0]))[0]
    mu = float(x0 @ b)
    se = float(s * np.sqrt(1 + x0 @ XtX_inv @ x0))
    tc = float(stats.t.ppf(0.975, dof))
    return mu, se, tc


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    df, n_raw, n_dup, n_absent = load()
    daily = build_daily(df)
    m = build_monthly(daily)
    facts = {}
    facts["so_dong_goc"] = n_raw
    facts["so_dong_trung_lap"] = n_dup
    facts["so_phut_bi_thieu_timestamp"] = n_absent
    facts["so_phut_tong"] = len(df)
    facts["ty_le_gia_tri_thieu_%"] = round(100 * df["Global_active_power"].isna().mean(), 2)
    facts["so_ngay_co_du_lieu_hop_le"] = int(daily["valid"].sum())
    facts["so_ngay_tong"] = len(daily)
    facts["so_thang_day_du"] = int(m["complete"].sum())

    # ---------- Khoảng trống dữ liệu ----------
    na = df["Global_active_power"].isna()
    run = (na != na.shift()).cumsum()
    tmp = pd.DataFrame({"na": na, "run": run, "t": df.index.to_series()})
    g = tmp[tmp["na"]].groupby("run").agg(bat_dau=("t", "min"), ket_thuc=("t", "max"), so_phut=("t", "size"))
    gaps = g[g["so_phut"] >= 60].sort_values("so_phut", ascending=False)
    gaps.to_csv(HERE / "khoang_trong_>=60phut.csv")
    facts["so_khoang_trong_>=60phut"] = int(len(gaps))
    facts["tong_phut_trong_>=60phut"] = int(gaps["so_phut"].sum())

    # ---------- Ngày / tuần bất thường ----------
    s_day = daily.loc[daily["valid"], "kwh"]
    base_d = s_day.rolling(15, center=True, min_periods=8).median()
    r_d = np.log(s_day) - np.log(base_d)
    r_d = r_d.dropna()
    z_d = (r_d - r_d.median()) / (1.4826 * (r_d - r_d.median()).abs().median())
    anom_days = pd.DataFrame({"kwh": s_day.loc[z_d.index], "nen_kwh": base_d.loc[z_d.index], "z": z_d})
    anom_days = anom_days[anom_days["z"].abs() > 3.5].sort_values("z")
    anom_days.to_csv(HERE / "ngay_bat_thuong.csv")

    wk = daily.loc[daily["valid"], "kwh"].resample("W-SUN").agg(["mean", "count"])
    wk = wk[wk["count"] == 7]["mean"]
    base_w = wk.rolling(9, center=True, min_periods=5).median()
    r_w = (np.log(wk) - np.log(base_w)).dropna()
    z_w = (r_w - r_w.median()) / (1.4826 * (r_w - r_w.median()).abs().median())
    anom_weeks = pd.DataFrame({"tb_kwh_ngay_trong_tuan": wk.loc[z_w.index],
                               "nen_kwh_ngay": base_w.loc[z_w.index], "z": z_w})
    anom_weeks = anom_weeks[anom_weeks["z"].abs() > 3].sort_values("z")
    anom_weeks.to_csv(HERE / "tuan_bat_thuong.csv")
    facts["so_ngay_bat_thuong"] = int(len(anom_days))
    facts["so_tuan_bat_thuong"] = int(len(anom_weeks))

    # ---------- Xu hướng ----------
    cm = m[m["complete"]].copy()
    cm["t"] = (cm.index.year - 2007) * 12 + cm.index.month - 1
    cm["mon"] = cm.index.month
    cm["y"] = np.log(cm["tb_kwh_moi_ngay"])
    ts = stats.theilslopes(cm["tb_kwh_moi_ngay"].to_numpy(), cm["t"].to_numpy())
    mean_all = cm["tb_kwh_moi_ngay"].mean()
    facts["xu_huong_%_moi_nam_theil_sen"] = round(100 * ts[0] * 12 / mean_all, 2)
    facts["xu_huong_khoang_tin_cay_%_low"] = round(100 * ts[2] * 12 / mean_all, 2)
    facts["xu_huong_khoang_tin_cay_%_high"] = round(100 * ts[3] * 12 / mean_all, 2)
    yr = daily.loc[daily["valid"]].groupby(daily.loc[daily["valid"]].index.year)["kwh"].agg(["mean", "count"])
    yr.columns = ["tb_kwh_moi_ngay", "so_ngay_hop_le"]
    yr.to_csv(HERE / "tong_hop_theo_nam.csv")

    # ---------- Mùa vụ ----------
    mo = cm.groupby("mon")["tb_kwh_moi_ngay"].mean()
    facts["thang_cao_nhat"] = MON_VI[int(mo.idxmax()) - 1]
    facts["tb_thang_cao_nhat_kwh_ngay"] = round(float(mo.max()), 2)
    facts["thang_thap_nhat"] = MON_VI[int(mo.idxmin()) - 1]
    facts["tb_thang_thap_nhat_kwh_ngay"] = round(float(mo.min()), 2)
    v = daily[daily["valid"]]
    dw = v.groupby("dow")["kwh"].mean()
    facts["tb_kwh_ngay_theo_thu"] = {DOW_VI[i]: round(float(dw[i]), 2) for i in range(7)}
    mask = daily["valid"].reindex(df.index.normalize()).fillna(False).to_numpy(dtype=bool)
    hr = df.loc[mask, "Global_active_power"].groupby(df.index[mask].hour).mean()  # kW trung bình
    facts["gio_cao_diem"] = int(hr.idxmax())
    facts["cong_suat_TB_gio_cao_diem_kW"] = round(float(hr.max()), 3)
    facts["gio_thap_diem"] = int(hr.idxmin())
    facts["cong_suat_TB_gio_thap_diem_kW"] = round(float(hr.min()), 3)
    mo.to_csv(HERE / "mua_vu_theo_thang.csv", header=["tb_kwh_moi_ngay"])
    dw.to_csv(HERE / "mua_vu_theo_thu.csv", header=["tb_kwh_moi_ngay"])
    hr.to_csv(HERE / "mua_vu_theo_gio.csv", header=["tb_kW"])

    # ---------- Dự báo tháng 12/2010 ----------
    # Mô hình: log(TB kWh/ngày) ~ xu hướng tuyến tính + hiệu ứng tháng (chỉ dùng tháng đủ dữ liệu)
    mdl_all = fit(cm)
    t_dec10 = (2010 - 2007) * 12 + 12 - 1
    mu, se, tc = predict(mdl_all, t_dec10, 12)

    # Backtest: dự báo trước 2 tháng (cuối tháng trước đó có dữ liệu đến tháng T-2)
    rows = []
    for target in cm.index[cm.index >= "2009-01-01"]:
        origin = target - pd.DateOffset(months=2)
        train = cm[cm.index <= origin]
        if len(train) < 24:
            continue
        mdl = fit(train)
        t0 = (target.year - 2007) * 12 + target.month - 1
        mu_b, se_b, tc_b = predict(mdl, t0, target.month)
        act = float(cm.loc[target, "y"])
        rows.append({"thang": target.strftime("%Y-%m"), "du_bao_tb_kwh_ngay": float(np.exp(mu_b)),
                     "thuc_te_tb_kwh_ngay": float(np.exp(act)), "sai_so_log": act - mu_b,
                     "tong_du_bao_kwh": float(np.exp(mu_b) * target.days_in_month),
                     "tong_thuc_te_kwh": float(np.exp(act) * target.days_in_month)})
    bt = pd.DataFrame(rows)
    bt.to_csv(HERE / "backtest_horizon2.csv", index=False)
    rmse_log = float(np.sqrt((bt["sai_so_log"] ** 2).mean()))
    mape_total = float(((bt["tong_du_bao_kwh"] - bt["tong_thuc_te_kwh"]).abs() / bt["tong_thuc_te_kwh"]).mean() * 100)
    facts["backtest_so_thang"] = int(len(bt))
    facts["backtest_rmse_log"] = round(rmse_log, 4)
    facts["backtest_MAPE_tong_%"] = round(mape_total, 2)

    point = float(np.exp(mu) * 31)
    half_model = tc * se
    half_bt = 1.96 * rmse_log
    half = max(half_model, half_bt)
    lo = float(np.exp(mu - half) * 31)
    hi = float(np.exp(mu + half) * 31)
    lo_model = float(np.exp(mu - half_model) * 31)
    hi_model = float(np.exp(mu + half_model) * 31)

    # Độ nhạy: tỉ lệ tiêu thụ 1–26/11/2010 so với 1–26/11/2009, áp dụng lên tháng 12/2009
    def mean_valid(a, b):
        return float(daily.loc[a:b].loc[lambda x: x["valid"], "kwh"].mean())
    ratio_nov = mean_valid("2010-11-01", "2010-11-26") / mean_valid("2009-11-01", "2009-11-26")
    dec09_total = float(cm.loc["2009-12-01", "tb_kwh_moi_ngay"] * 31)
    alt_nov = dec09_total * ratio_nov
    facts["ty_le_11_2010_vs_11_2009_1_26"] = round(ratio_nov, 4)
    facts["sensitivity_du_bao_theo_ty_le_thang_11"] = round(alt_nov, 1)

    dec_hist = cm[cm.index.month == 12][["tb_kwh_moi_ngay", "tong_kwh_uoc_tinh"]]
    dec_hist.to_csv(HERE / "thang_12_lich_su.csv")
    fc = pd.DataFrame([{
        "thang": "2010-12",
        "du_bao_tong_kwh": point, "khoang_95_thap": lo, "khoang_95_cao": hi,
        "khoang_95_chi_tu_mo_hinh": [lo_model, hi_model],
        "tb_kwh_ngay": float(np.exp(mu)), "se_log_mo_hinh": se, "rmse_log_backtest": rmse_log,
        "du_bao_theo_ty_le_thang_11": alt_nov,
    }])
    fc.to_csv(HERE / "du_bao_thang_12_2010.csv", index=False)
    m.to_csv(HERE / "tong_hop_theo_thang.csv")
    daily.to_csv(HERE / "tong_hop_theo_ngay.csv")

    facts["du_bao_dec2010_kwh"] = round(point, 1)
    facts["du_bao_dec2010_khoang95"] = [round(lo, 1), round(hi, 1)]
    facts["du_bao_dec2010_khoang95_chi_mo_hinh"] = [round(lo_model, 1), round(hi_model, 1)]
    facts["dec2009_kwh_uoc_tinh"] = round(dec09_total, 1)
    facts["dec_hist_tong_kwh"] = {str(k.year): round(float(v), 1) for k, v in dec_hist["tong_kwh_uoc_tinh"].items()}
    with open(HERE / "so_lieu_chinh.json", "w", encoding="utf-8") as f:
        json.dump(facts, f, ensure_ascii=False, indent=2, default=str)

    # ---------- Biểu đồ ----------
    fig, ax = plt.subplots(figsize=(11, 5))
    ok = m[m["complete"]]
    bad = m[(~m["complete"]) & m["tb_kwh_moi_ngay"].notna()]
    ax.plot(ok.index, ok["tb_kwh_moi_ngay"], "o-", color="#1f77b4", label="Tháng đủ dữ liệu")
    ax.plot(bad.index, bad["tb_kwh_moi_ngay"], "o", mfc="white", color="#999", label="Tháng thiếu ngày (không dùng để dự báo)")
    xt = (ok.index.year - 2007) * 12 + ok.index.month - 1
    ax.plot(ok.index, ts[1] + ts[0] * xt, "--", color="#d62728", label="Xu hướng (Theil-Sen)")
    ax.set_title(f"Điện tiêu thụ trung bình/ngày đỉnh vào mùa đông ({facts['thang_cao_nhat']}: {mo.max():.1f} kWh), "
                 f"xu hướng {facts['xu_huong_%_moi_nam_theil_sen']:+.1f}%/năm", fontsize=12)
    ax.set_ylabel("kWh / ngày")
    ax.set_xlabel("Tháng")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(HERE / "xu_huong_thang.png", dpi=130)
    plt.close(fig)

    fig, axs = plt.subplots(1, 3, figsize=(15, 4.6))
    axs[0].bar(MON_VI, mo.values, color="#1f77b4")
    axs[0].set_title(f"Mùa đông ({facts['thang_cao_nhat']}) cao hơn mùa hè ({facts['thang_thap_nhat']}) "
                     f"khoảng {mo.max() / mo.min():.1f} lần", fontsize=11)
    axs[0].set_ylabel("kWh / ngày (trung bình các năm)")
    axs[1].bar([d.replace("Chủ nhật", "CN") for d in DOW_VI], dw.values, color="#2ca02c")
    axs[1].set_title(f"Cuối tuần {'cao hơn' if dw[5:].mean() > dw[:5].mean() else 'thấp hơn'} ngày thường "
                     f"{abs(dw[5:].mean() / dw[:5].mean() - 1) * 100:.0f}%", fontsize=11)
    axs[1].set_ylabel("kWh / ngày")
    axs[2].plot(hr.index, hr.values, "o-", color="#ff7f0e")
    axs[2].set_title(f"Đỉnh công suất lúc {facts['gio_cao_diem']}h, đáy lúc {facts['gio_thap_diem']}h", fontsize=11)
    axs[2].set_xlabel("Giờ trong ngày")
    axs[2].set_ylabel("Công suất TB (kW)")
    for a in axs:
        a.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(HERE / "mua_vu.png", dpi=130)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(13, 5))
    sd = daily.loc[daily["valid"], "kwh"]
    ax.plot(sd.index, sd.values, lw=0.6, color="#1f77b4", label="kWh/ngày (ngày đủ dữ liệu)")
    for _, r in gaps[gaps["so_phut"] >= 1440].iterrows():
        ax.axvspan(r["bat_dau"], r["ket_thuc"], color="#bbbbbb", alpha=0.6)
    if len(anom_weeks):
        ax.scatter(anom_weeks.index, anom_weeks["tb_kwh_ngay_trong_tuan"],
                   color="#d62728", zorder=5, s=28, label="Tuần bất thường (|z|>3)")
    n_aug = int((anom_weeks.index.month == 8).sum())
    ax.set_title(f"{len(gaps[gaps['so_phut'] >= 1440])} khoảng trống ≥1 ngày (vùng xám); {len(anom_weeks)} tuần bất thường, "
                 f"trong đó {n_aug} tuần rơi vào tháng 8 (mức tiêu thụ thấp)", fontsize=12)
    ax.set_ylabel("kWh / ngày")
    ax.legend(loc="upper right")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(HERE / "ngay_tuan_bat_thuong.png", dpi=130)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(11, 5))
    hist = cm[cm.index.month == 12]
    labels = [f"12/{d.year}" for d in hist.index] + ["12/2010 (dự báo)"]
    vals = list(hist["tong_kwh_uoc_tinh"].values) + [point]
    colors = ["#1f77b4"] * len(hist) + ["#ff7f0e"]
    ax.bar(labels, vals, color=colors)
    ax.errorbar([len(labels) - 1], [point], yerr=[[point - lo], [hi - point]], fmt="none", ecolor="k", capsize=6)
    for i, v_ in enumerate(vals):
        ax.text(i, v_ + 15, f"{v_:,.0f}", ha="center", fontsize=10)
    ax.set_title(f"Dự báo tháng 12/2010 khoảng {point:,.0f} kWh (95%: {lo:,.0f}–{hi:,.0f}), "
                 f"{(point / dec09_total - 1) * 100:+.0f}% so với 12/2009", fontsize=12)
    ax.set_ylabel("Tổng kWh trong tháng")
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(HERE / "du_bao_thang_12_2010.png", dpi=130)
    plt.close(fig)

    print(json.dumps(facts, ensure_ascii=False, indent=2, default=str))
    print("\nBacktest:\n", bt.round(3).to_string(index=False))
    print("\nMonthly (first/last rows):\n", m.round(2).head(3).to_string(), "\n...\n", m.round(2).tail(4).to_string())
    print("\nLong gaps:\n", gaps.head(12).to_string())
    print("\nAnomalous weeks:\n", anom_weeks.round(2).to_string())
    print("\nAnomalous days (top 15):\n", anom_days.head(15).round(2).to_string())
    print("\nYearly:\n", yr.round(2).to_string())


if __name__ == "__main__":
    main()
