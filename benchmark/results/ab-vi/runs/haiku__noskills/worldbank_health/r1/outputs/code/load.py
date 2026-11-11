"""Đọc và làm sạch dữ liệu World Bank (định dạng wide: một cột cho mỗi năm)."""
import csv

DATA = "data/"
LE = DATA + "life_expectancy/API_SP.DYN.LE00.IN_DS2_en_csv_v2_259172.csv"
HE = DATA + "health_expenditure_per_capita/API_SH.XPD.CHEX.PC.CD_DS2_en_csv_v2_3808.csv"
GD = DATA + "gdp_per_capita_ppp/API_NY.GDP.PCAP.PP.CD_DS2_en_csv_v2_1247.csv"
META = DATA + "life_expectancy/Metadata_Country_API_SP.DYN.LE00.IN_DS2_en_csv_v2_259172.csv"


def load_wide(path):
    """Trả về dict: {mã_nước: {năm: giá_trị_float_hoặc_None}}."""
    rows = list(csv.reader(open(path, encoding="utf-8-sig")))
    hdr = None
    out = {}
    for r in rows:
        if len(r) > 4 and r[0] == "Country Name":
            hdr = r
            continue
        if hdr is None or len(r) < 5:
            continue
        code = r[1]
        vals = {}
        for i in range(4, len(hdr)):
            if not hdr[i]:
                continue
            try:
                vals[hdr[i]] = float(r[i])
            except (ValueError, IndexError):
                vals[hdr[i]] = None
        out[code] = {"name": r[0], "vals": vals}
    return out


def load_meta():
    out = {}
    for r in csv.DictReader(open(META, encoding="utf-8-sig")):
        out[r["Country Code"]] = r
    return out


def panel():
    """Trả về (meta, le, he, gd). Chỉ giữ các mã có IncomeGroup (loại tổng hợp khu vực)."""
    meta = load_meta()
    le = load_wide(LE)
    he = load_wide(HE)
    gd = load_wide(GD)
    codes = [c for c in le if meta.get(c, {}).get("IncomeGroup")]
    return meta, le, he, gd, codes
