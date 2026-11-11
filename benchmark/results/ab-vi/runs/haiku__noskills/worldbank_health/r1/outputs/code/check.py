"""Kiểm tra độ tin cậy: (a) chuỗi tuổi thọ của CAF, (b) sai số chuẩn hệ số ln CHE,
(c) kết quả khi bỏ CAF (điểm ngoại lai)."""
import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load import panel  # noqa: E402
from analysis import build  # noqa: E402

meta, le, he, gd, codes = panel()
print("CAF LE 2015-2023:", [round(le["CAF"]["vals"][str(y)], 2) for y in range(2015, 2024)])
print("CAF CHE 2019:", he["CAF"]["vals"]["2019"])

df = build("2019")
X = np.column_stack([np.ones(len(df)), df.ln_gdp, df.ln_gdp ** 2, df.ln_che])
y = df.life_exp.values
b, *_ = np.linalg.lstsq(X, y, rcond=None)
r = y - X @ b
n, k = X.shape
s2 = (r @ r) / (n - k)
se = np.sqrt(np.diag(s2 * np.linalg.inv(X.T @ X)))
t = b[3] / se[3]
print(f"ln CHE: coef={b[3]:.3f}, SE={se[3]:.3f}, t={t:.2f}, n={n}")

m = (df.code != "CAF").values
b2, *_ = np.linalg.lstsq(X[m], y[m], rcond=None)
print(f"Bỏ CAF: coef ln CHE={b2[3]:.3f}")
d2 = df[m]
print(f"Bỏ CAF: r(LE, ln CHE)={np.corrcoef(d2.ln_che, d2.life_exp)[0, 1]:.3f}")
