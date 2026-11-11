"""Doanh thu thuần 2011 so với 2010 (so sánh cùng kỳ 1/1 - 9/12), phân rã theo khách mới/cũ và thị trường.

Chạy: python analysis.py   (đọc data/online_retail_II.xlsx ở thư mục gốc dự án, ghi kết quả vào thư mục này)
"""
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / "data" / "online_retail_II.xlsx"

COLS = ["Invoice", "StockCode", "Description", "Quantity", "InvoiceDate", "Price", "Customer ID", "Country"]
OVERLAP_START = pd.Timestamp("2010-12-01")
CLS_ORDER = ["Khách mới", "Khách cũ - giữ lại", "Khách cũ - quay lại", "Khách cũ - rời bỏ", "Không rõ khách hàng"]
COUNTRY_VI = {
    "United Kingdom": "Vương quốc Anh", "EIRE": "Ireland", "Germany": "Đức", "France": "Pháp",
    "Netherlands": "Hà Lan", "Spain": "Tây Ban Nha", "Switzerland": "Thụy Sĩ", "Belgium": "Bỉ",
    "Portugal": "Bồ Đào Nha", "Australia": "Úc", "Channel Islands": "Quần đảo Channel",
    "Italy": "Ý", "Norway": "Na Uy", "Sweden": "Thụy Điển", "Cyprus": "Síp", "Finland": "Phần Lan",
    "Austria": "Áo", "Denmark": "Đan Mạch", "Unspecified": "Không xác định", "Greece": "Hy Lạp",
    "Japan": "Nhật Bản", "USA": "Hoa Kỳ", "Poland": "Ba Lan", "United Arab Emirates": "UAE",
    "Hong Kong": "Hồng Kông", "Israel": "Israel", "Singapore": "Singapore", "Malta": "Malta",
    "Canada": "Canada", "RSA": "Nam Phi", "Thailand": "Thái Lan", "Korea": "Hàn Quốc",
    "European Community": "Cộng đồng châu Âu", "Lebanon": "Liban", "West Indies": "Tây Ấn",
    "Brazil": "Brazil", "Bahrain": "Bahrain", "Iceland": "Iceland", "Lithuania": "Lithuania",
    "Bermuda": "Bermuda",
}


def load() -> pd.DataFrame:
    xl = pd.ExcelFile(DATA)
    s1 = xl.parse("Year 2009-2010")
    s2 = xl.parse("Year 2010-2011")

    # Hai sheet trùng nhau trong 1/12 - 9/12/2010: kiểm tra rồi chỉ giữ một bản (sheet 2 từ 1/12/2010).
    ov1 = s1[s1.InvoiceDate >= OVERLAP_START]
    ov2 = s2[s2.InvoiceDate < pd.Timestamp("2010-12-10")]
    h1 = np.sort(pd.util.hash_pandas_object(ov1[COLS].astype(str), index=False).values)
    h2 = np.sort(pd.util.hash_pandas_object(ov2[COLS].astype(str), index=False).values)
    same = len(ov1) == len(ov2) and np.array_equal(h1, h2)
    print(f"[dedupe] vùng chồng 1-9/12/2010: sheet1={len(ov1):,} dòng, sheet2={len(ov2):,} dòng, giống hệt={same}")
    assert same, "Vùng chồng không khớp - cần xem lại quy tắc khử trùng"

    df = pd.concat([s1[s1.InvoiceDate < OVERLAP_START], s2], ignore_index=True)
    df["rev"] = df.Quantity * df.Price  # doanh thu thuần: hàng hoá trừ hàng trả/huỷ (số lượng âm)
    df["year"] = df.InvoiceDate.dt.year
    df["known"] = df["Customer ID"].notna()
    df["cid"] = df["Customer ID"].fillna(-1).astype("int64")
    df["is_return"] = df.Invoice.astype(str).str.startswith("C")
    df["Country"] = df["Country"].astype(str)
    return df


def window(df: pd.DataFrame) -> pd.DataFrame:
    """Cùng kỳ: 1/1 đến 9/12 của mỗi năm (dữ liệu 2011 kết thúc 9/12/2011)."""
    end = pd.to_datetime(df.year.astype(str) + "-12-10")
    return df[df.year.isin([2010, 2011]) & (df.InvoiceDate < end)].copy()


def totals(w: pd.DataFrame, y: int) -> dict:
    d = w[w.year == y]
    return {
        "doanh_thu": d.rev.sum(),
        "so_khach_co_ma": d.loc[d.known, "cid"].nunique(),
        "so_don": d.loc[~d.is_return, "Invoice"].nunique(),
        "doanh_thu_hoan_huy": d.loc[d.is_return, "rev"].sum(),
        "ty_le_dt_khong_ro_khach": d.loc[~d.known, "rev"].sum() / d.rev.sum(),
    }


def classify(df: pd.DataFrame, w: pd.DataFrame) -> pd.DataFrame:
    """Gán nhóm khách theo hành vi. 'Khách mới' = lần mua đầu tiên trong dữ liệu rơi vào 2011."""
    known = df[df.known]
    first = known.groupby("cid").InvoiceDate.min()
    act10 = set(w.loc[(w.year == 2010) & w.known, "cid"])
    act11 = set(w.loc[(w.year == 2011) & w.known, "cid"])
    cust = pd.DataFrame({"first": first})
    cust["act10"] = cust.index.isin(act10)
    cust["act11"] = cust.index.isin(act11)
    cust["cls"] = np.select(
        [
            cust.act11 & (cust["first"] >= pd.Timestamp("2011-01-01")),
            cust.act10 & cust.act11,
            cust.act10 & ~cust.act11,
            ~cust.act10 & cust.act11,
        ],
        ["Khách mới", "Khách cũ - giữ lại", "Khách cũ - rời bỏ", "Khách cũ - quay lại"],
        default="Ngoài cùng kỳ",
    )
    return cust


def main() -> None:
    raw = load()
    w = window(raw)
    cust = classify(raw, w)
    w["cls"] = np.where(w.known, w.cid.map(cust.cls).astype(object), "Không rõ khách hàng")
    w["signed"] = w.rev * np.where(w.year == 2011, 1, -1)  # đóng góp vào Δ: 2011 (+), 2010 (-)

    # 1. Tổng quan cùng kỳ
    t10, t11 = totals(w, 2010), totals(w, 2011)
    d_total = t11["doanh_thu"] - t10["doanh_thu"]
    summary = pd.DataFrame(
        {
            "chi_so": ["doanh_thu_thuan", "so_khach_co_ma", "so_don", "doanh_thu_hoan_huy", "ty_le_dt_khong_ro_khach"],
            "cung_ky_2010": [t10[k] for k in t10],
            "cung_ky_2011": [t11[k] for k in t11],
        }
    )
    summary["thay_doi"] = summary.cung_ky_2011 - summary.cung_ky_2010
    summary["thay_doi_pct"] = summary.thay_doi / summary.cung_ky_2010.abs() * 100
    summary.to_csv(HERE / "tong_quan_cung_ky.csv", index=False)
    print("\n[1] Tổng quan cùng kỳ 1/1-9/12")
    print(summary.to_string(index=False))

    # 2. Cầu nối theo nhóm khách
    br = w.groupby("cls").agg(dong_gop=("signed", "sum"))
    br["so_khach_2010"] = w[w.known & (w.year == 2010)].groupby("cls").cid.nunique()
    br["so_khach_2011"] = w[w.known & (w.year == 2011)].groupby("cls").cid.nunique()
    br["dt_2010"] = w[w.year == 2010].groupby("cls").rev.sum()
    br["dt_2011"] = w[w.year == 2011].groupby("cls").rev.sum()
    br = br.reindex(CLS_ORDER).fillna(0)
    br["ty_trong_thay_doi"] = br.dong_gop / d_total
    br.index.name = "nhom_khach"
    assert abs(br.dong_gop.sum() - d_total) < 1e-3, "Cầu nối không khớp tổng Δ"
    br.to_csv(HERE / "cau_noi_khach_moi_cu.csv")
    print("\n[2] Cầu nối theo nhóm khách (Δ = {:,.0f} £)".format(d_total))
    print(br.round(3).to_string())

    # Chỉ số giữ chân khách cũ
    base = cust[cust.act10]
    ret = cust[cust.cls == "Khách cũ - giữ lại"]
    ret_rate = len(ret) / len(base)
    rev_base10 = w[(w.year == 2010) & w.known & w.cid.isin(base.index)].rev.sum()
    rev_ret11 = w[(w.year == 2011) & (w.cls == "Khách cũ - giữ lại")].rev.sum()
    rev_ret10 = w[(w.year == 2010) & (w.cls == "Khách cũ - giữ lại")].rev.sum()
    n_new = int(cust.cls.eq("Khách mới").sum())
    retention = {
        "khach_co_mua_2010": len(base),
        "khach_giu_lai_2011": len(ret),
        "ty_le_giu_chan_khach": ret_rate,
        "dt_2010_cua_khach_co_mua_2010": rev_base10,
        "dt_2011_cua_nhom_giu_lai": rev_ret11,
        "dt_2010_cua_nhom_giu_lai": rev_ret10,
        "ty_le_giu_doanh_thu_nhom_giu_lai": rev_ret11 / rev_ret10,
        "chi_tieu_trung_binh_2010_moi_khach_cu": rev_base10 / len(base),
        "so_khach_moi_2011": n_new,
        "chi_tieu_trung_binh_2011_moi_khach_moi": w[(w.year == 2011) & (w.cls == "Khách mới")].rev.sum() / max(n_new, 1),
    }
    pd.Series(retention).to_csv(HERE / "chi_so_giu_chan.csv", header=["gia_tri"])
    print("\n[2b] Giữ chân:")
    for k, v in retention.items():
        print(f"   {k}: {v:,.4f}" if isinstance(v, float) else f"   {k}: {v:,}")

    # 3. Thị trường
    mk = w.pivot_table(index="Country", columns="year", values="rev", aggfunc="sum", fill_value=0)
    mk.columns = ["dt_2010", "dt_2011"]
    mk["thay_doi"] = mk.dt_2011 - mk.dt_2010
    mk["thay_doi_pct"] = mk.thay_doi / mk.dt_2010.where(mk.dt_2010 > 0) * 100
    mk["ty_trong_thay_doi"] = mk.thay_doi / d_total
    by_cls = w.pivot_table(index="Country", columns="cls", values="signed", aggfunc="sum", fill_value=0)
    by_cls = by_cls.reindex(columns=CLS_ORDER, fill_value=0)
    by_cls.columns = [f"dong_gop_{c}" for c in CLS_ORDER]
    mk = mk.join(by_cls)
    mk["khach_2010"] = w[w.known & (w.year == 2010)].groupby("Country").cid.nunique()
    mk["khach_2011"] = w[w.known & (w.year == 2011)].groupby("Country").cid.nunique()
    mk = mk.fillna(0)
    assert np.allclose(mk.thay_doi, mk[[c for c in mk.columns if c.startswith("dong_gop_")]].sum(axis=1))
    mk["ten_vi"] = [COUNTRY_VI.get(c, c) for c in mk.index]
    mk = mk.sort_values("thay_doi")
    mk.index.name = "quoc_gia"
    mk.to_csv(HERE / "thi_truong_thay_doi.csv")
    print(f"\n[3] Thị trường: {len(mk)} quốc gia; top giảm/tăng theo £:")
    cols = ["dt_2010", "dt_2011", "thay_doi", "thay_doi_pct", "ty_trong_thay_doi"]
    print(mk[cols].head(6).round(3).to_string())
    print("   ...")
    print(mk[cols].tail(6).round(3).to_string())
    uk = mk.loc["United Kingdom"]
    ex = mk.drop("United Kingdom")
    print(f"   Vương quốc Anh Δ={uk.thay_doi:,.0f}; ngoài Anh Δ={ex.thay_doi.sum():,.0f}")

    # 4. Kiểm tra độ nhạy
    def growth(a: pd.DataFrame, b: pd.DataFrame) -> tuple:
        x, y = a.rev.sum(), b.rev.sum()
        return x, y, y - x, (y - x) / abs(x) * 100

    rows = [("Cùng kỳ 1/1-9/12 (chính)",) + growth(w[w.year == 2010], w[w.year == 2011])]
    m_nov = raw[raw.year.isin([2010, 2011]) & (raw.InvoiceDate < pd.to_datetime(raw.year.astype(str) + "-12-01"))]
    rows.append(("Cùng kỳ 1/1-30/11 (kiểm tra)",) + growth(m_nov[m_nov.year == 2010], m_nov[m_nov.year == 2011]))
    rows.append(("Sai: cả năm 2010 vs 2011 chưa đủ",) + growth(raw[raw.year == 2010], raw[raw.year == 2011]))
    pos = w[~w.is_return]
    rows.append(("Chỉ giao dịch bán (không hàng trả)",) + growth(pos[pos.year == 2010], pos[pos.year == 2011]))
    kn = w[w.known]
    rows.append(("Chỉ dòng có mã khách",) + growth(kn[kn.year == 2010], kn[kn.year == 2011]))
    rob = pd.DataFrame(rows, columns=["kich_ban", "dt_2010", "dt_2011", "thay_doi", "thay_doi_pct"])
    rob.to_csv(HERE / "kiem_tra_do_nhay.csv", index=False)
    print("\n[4] Độ nhạy:")
    print(rob.round(1).to_string(index=False))

    # 5. Biểu đồ
    plot_bridge(br, t10["doanh_thu"], t11["doanh_thu"])
    plot_markets(mk)
    print("\nXong. Kết quả ghi tại:", HERE)


def plot_bridge(br: pd.DataFrame, dt10: float, dt11: float) -> None:
    m = 1e6
    steps = [
        ("Doanh thu\ncùng kỳ 2010", dt10 / m, "total"),
        ("Khách cũ\nrời bỏ", br.loc["Khách cũ - rời bỏ", "dong_gop"] / m, "delta"),
        ("Khách cũ giữ lại\n(đổi chi tiêu)", br.loc["Khách cũ - giữ lại", "dong_gop"] / m, "delta"),
        ("Khách cũ\nquay lại", br.loc["Khách cũ - quay lại", "dong_gop"] / m, "delta"),
        ("Khách mới\n(2011)", br.loc["Khách mới", "dong_gop"] / m, "delta"),
        ("Không rõ\nmã khách", br.loc["Không rõ khách hàng", "dong_gop"] / m, "delta"),
        ("Doanh thu\ncùng kỳ 2011", dt11 / m, "total"),
    ]
    fig, ax = plt.subplots(figsize=(11, 6))
    running = 0.0
    for i, (label, v, kind) in enumerate(steps):
        if kind == "total":
            ax.bar(i, v, color="#4a4a4a", width=0.6)
            ax.text(i, v + 0.15, f"{v:,.2f}", ha="center", va="bottom", fontsize=10, fontweight="bold")
            running = v
        else:
            bottom = running if v >= 0 else running + v
            ax.bar(i, abs(v), bottom=bottom, color="#2e8b57" if v >= 0 else "#c0392b", width=0.6)
            sign = "+" if v >= 0 else "−"
            ax.text(i, max(running, running + v) + 0.15, f"{sign}{abs(v):,.2f}", ha="center", va="bottom", fontsize=10)
            running += v
    ax.set_xticks(range(len(steps)))
    ax.set_xticklabels([s[0] for s in steps], fontsize=9)
    ax.set_ylabel("Doanh thu thuần (triệu £)")
    ax.set_title("Cầu nối doanh thu thuần cùng kỳ 1/1-9/12: 2010 → 2011, theo nhóm khách", fontsize=12, loc="left")
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_ylim(0, max(dt10, dt11) / m * 1.15)
    fig.tight_layout()
    fig.savefig(HERE / "cau_noi_doanh_thu.png", dpi=150)
    plt.close(fig)


def plot_markets(mk: pd.DataFrame) -> None:
    top = mk.reindex(mk.thay_doi.abs().sort_values(ascending=False).index).head(10).sort_values("thay_doi")
    rest = mk.drop(top.index).thay_doi.sum()
    labels = list(top.ten_vi) + ["Các thị trường khác"]
    vals = list(top.thay_doi / 1e3) + [rest / 1e3]  # đơn vị: nghìn £
    pcts = list(top.thay_doi_pct) + [np.nan]
    colors = ["#2e8b57" if v >= 0 else "#c0392b" for v in vals]
    fig, ax = plt.subplots(figsize=(10, 6.5))
    y = np.arange(len(vals))
    ax.barh(y, vals, color=colors, height=0.6)
    ax.axvline(0, color="#333", lw=0.8)
    lo, hi = min(vals + [0]), max(vals + [0])
    ax.set_xlim(lo * 2.4 if lo < 0 else 0, hi * 2.0 if hi > 0 else 0)  # chừa chỗ cho nhãn
    for i, (v, p) in enumerate(zip(vals, pcts)):
        txt = f"{v:+,.0f} nghìn £"
        if not np.isnan(p):
            txt += f"  ({p:+.0f}%)"
        ax.text(v + (hi * 0.02 if v >= 0 else lo * 0.02), i, txt, va="center",
                ha="left" if v >= 0 else "right", fontsize=9)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Thay đổi doanh thu thuần 2011 so với 2010, cùng kỳ (nghìn £)")
    ax.set_title("Thị trường kéo doanh thu tăng/giảm nhiều nhất (top 10 theo |Δ|)", fontsize=12, loc="left")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(HERE / "thi_truong_thay_doi.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
