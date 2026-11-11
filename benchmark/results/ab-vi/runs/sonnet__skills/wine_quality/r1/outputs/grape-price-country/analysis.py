import os
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

here = os.path.dirname(os.path.abspath(__file__))
data = os.path.join(here, "..", "..", "data")
r = pd.read_csv(os.path.join(data, "winequality-red.csv"), sep=";")
w = pd.read_csv(os.path.join(data, "winequality-white.csv"), sep=";")
r["loai"] = "đỏ"
w["loai"] = "trắng"
d = pd.concat([r, w])

s = d.groupby("loai").quality.agg(["count", "mean", "median", lambda x: (x >= 7).mean()])
s.columns = ["n", "mean", "median", "ty_le_>=7"]
s.to_csv(os.path.join(here, "so_sanh_do_trang.csv"))
print(s)
print(stats.mannwhitneyu(r.quality, w.quality))

c = d.drop(columns="loai").corr()["quality"].drop("quality").sort_values()
c.to_csv(os.path.join(here, "tuong_quan_chat_luong.csv"))
print(c)

d["alc"] = pd.cut(d.alcohol, [0, 9.5, 10.5, 11.5, 20], labels=["<9.5", "9.5-10.5", "10.5-11.5", ">11.5"])
a = d.groupby(["loai", "alc"], observed=True).quality.mean().unstack(0)
a.to_csv(os.path.join(here, "chat_luong_theo_con.csv"))
print(a)
a.plot(marker="o")
plt.title("Chất lượng trung bình theo nồng độ cồn (%)")
plt.ylabel("Điểm chất lượng TB")
plt.xlabel("Nhóm nồng độ cồn")
plt.tight_layout()
plt.savefig(os.path.join(here, "chat_luong_theo_con.png"), dpi=120)
