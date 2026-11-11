"""Kiểm tra độ phù hợp của dữ liệu với câu hỏi về giống nho, mức giá và xuất xứ (Pháp / Bồ Đào Nha).

Chạy từ thư mục gốc dự án:  python outputs/giong-nho-va-gia-ruou-vang/analysis.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
OUT = Path(__file__).resolve().parent

files = {
    "red": DATA / "winequality-red.csv",
    "white": DATA / "winequality-white.csv",
}

frames = []
for wine_type, path in files.items():
    df = pd.read_csv(path, sep=";")
    df["wine_type"] = wine_type
    frames.append(df)
    print(f"{wine_type}: {df.shape[0]} dòng, {df.shape[1] - 1} cột (không tính wine_type)")

all_wines = pd.concat(frames, ignore_index=True)

# 1. Kiểm tra cột: có cột nào mô tả giống nho, giá, xuất xứ/quốc gia/vùng, nhãn hiệu không?
keywords = ["grape", "variety", "varietal", "cultivar", "price", "cost", "country",
            "origin", "region", "france", "portugal", "brand", "producer", "winery"]
cols = [c for c in all_wines.columns if c != "wine_type"]
rows = []
for kw in keywords:
    hits = [c for c in cols if kw in c.lower()]
    rows.append({"keyword": kw, "matching_columns": ", ".join(hits) if hits else "(không có)"})
check = pd.DataFrame(rows)
check.to_csv(OUT / "column_check.csv", index=False, encoding="utf-8-sig")
print("\nKết quả kiểm tra cột:")
print(check.to_string(index=False))

# 2. Danh sách đầy đủ cột để đối chiếu
pd.DataFrame({"column": cols}).to_csv(OUT / "columns.csv", index=False, encoding="utf-8-sig")

# 3. Phân bố điểm chất lượng theo loại rượu (biến duy nhất ngoài đặc tính lý-hóa có thể đối chiếu)
q_by_type = (all_wines.groupby("wine_type")["quality"]
             .agg(["count", "mean", "median", "min", "max"])
             .round(3))
q_by_type.to_csv(OUT / "quality_by_type.csv", encoding="utf-8-sig")
print("\nĐiểm chất lượng theo loại rượu:")
print(q_by_type.to_string())

print("\nCó cột Pháp/Bồ Đào Nha/quốc gia nào không?",
      any(k in " ".join(cols).lower() for k in ["france", "portugal", "country", "origin"]))
