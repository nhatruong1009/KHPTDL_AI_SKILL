"""Danh sach vuot/duoi ky vong on dinh qua nam 2019 va 2023.

Chay: python robust_lists.py (can analysis.py cung thu muc)
"""
import os
import importlib.util as u
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
spec = u.spec_from_file_location("analysis", os.path.join(HERE, "analysis.py"))
A = u.module_from_spec(spec)
spec.loader.exec_module(A)

YEARS = [2019, 2023]
frames = []
for y in YEARS:
    d, _ = A.analyse(y)
    d = d.sort_values("gap_le", ascending=False).reset_index(drop=True)
    d["year"] = y
    frames.append(d)
both = pd.concat(frames)

gap = both.pivot_table(index=["Country Code", "Country Name"], columns="year", values="gap_le").dropna()
gap["min_gap"] = gap[YEARS].min(axis=1)
gap["max_gap"] = gap[YEARS].max(axis=1)

top_sets = [set(both[both.year == y].head(15)["Country Code"]) for y in YEARS]
bot_sets = [set(both[both.year == y].tail(15)["Country Code"]) for y in YEARS]
stable_top = top_sets[0] & top_sets[1]
stable_bot = bot_sets[0] & bot_sets[1]

out = gap.reset_index()
out["stable_top15_both_years"] = out["Country Code"].isin(stable_top)
out["stable_bottom15_both_years"] = out["Country Code"].isin(stable_bot)
out = out.sort_values("min_gap", ascending=False)
out.to_csv(os.path.join(HERE, "stable_over_under_2019_2023.csv"), index=False)

print("Vuot ky vong on dinh (top 15 ca 2019 va 2023):")
print(out[out.stable_top15_both_years][["Country Name", 2019, 2023]].round(2).to_string(index=False))
print("Duoi ky vong on dinh (bottom 15 ca 2019 va 2023):")
print(out[out.stable_bottom15_both_years][["Country Name", 2019, 2023]].round(2).to_string(index=False))
