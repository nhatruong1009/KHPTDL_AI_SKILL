import pandas as pd

BASE = "/root/.cache/skill-bench/runs/v2-skills/haiku__skills/worldbank_health/r1/workspace/data"
files = {
    "le": f"{BASE}/life_expectancy/API_SP.DYN.LE00.IN_DS2_en_csv_v2_70864.csv",
    "hx": f"{BASE}/health_expenditure_per_capita/API_SH.XPD.CHEX.PC.CD_DS2_en_csv_v2_57.csv",
    "gdp": f"{BASE}/gdp_per_capita_ppp/API_NY.GDP.PCAP.PP.CD_DS2_en_csv_v2_60730.csv",
}
show = ["2010", "2015", "2018", "2019", "2020", "2021", "2022", "2023", "2024"]
for k, f in files.items():
    df = pd.read_csv(f, skiprows=4, encoding="utf-8-sig")
    print(k, df.shape)
    print({y: int(df[y].notna().sum()) for y in show if y in df.columns})
