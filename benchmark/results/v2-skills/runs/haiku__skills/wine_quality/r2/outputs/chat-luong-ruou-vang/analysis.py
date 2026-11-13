import os
import pandas as pd, numpy as np
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "..", "..", "data")
OUT = BASE

red = pd.read_csv(os.path.join(DATA, "winequality-red.csv"), sep=";")
white = pd.read_csv(os.path.join(DATA, "winequality-white.csv"), sep=";")
red["loai"] = "Vang do"
white["loai"] = "Vang trang"
df = pd.concat([red, white], ignore_index=True)
feats = [c for c in red.columns if c not in ("quality", "loai")]

lines = []
def out(s=""):
    print(s); lines.append(str(s))

out("== 1. Phan bo diem chat luong theo loai ==")
out(df.groupby("loai")["quality"].describe().round(3).to_string())
out("\nTy le >=7 diem:")
out(df.assign(hi=df.quality >= 7).groupby("loai")["hi"].mean().round(4).to_string())
out("\nDiem cao nhat theo loai:")
out(df.groupby("loai")["quality"].max().to_string())
out("\nSo luong moi diem theo loai:")
out(pd.crosstab(df.quality, df.loai).to_string())

out("\n== 2. So sanh do - trang (Mann-Whitney, raw va da loai trung lap) ==")
r_raw = df[df.loai=="Vang do"].quality; w_raw = df[df.loai=="Vang trang"].quality
u, p = stats.mannwhitneyu(w_raw, r_raw)
out(f"raw: n do={len(r_raw)}, n trang={len(w_raw)}; mean do={r_raw.mean():.3f}, trang={w_raw.mean():.3f}, p={p:.2e}")
dd = df.drop_duplicates(subset=feats+["quality","loai"])
r_d = dd[dd.loai=="Vang do"].quality; w_d = dd[dd.loai=="Vang trang"].quality
u2, p2 = stats.mannwhitneyu(w_d, r_d)
out(f"dedup: n do={len(r_d)}, n trang={len(w_d)}; mean do={r_d.mean():.3f}, trang={w_d.mean():.3f}, p={p2:.2e}")

out("\n== 3. Tuong quan Spearman voi quality (trong tung loai, raw) ==")
rows = []
for loai, g in df.groupby("loai"):
    for f in feats:
        rho, pv = stats.spearmanr(g[f], g["quality"])
        rows.append((loai, f, round(rho,3), pv))
corr = pd.DataFrame(rows, columns=["loai","dac_trung","rho","p"])
corr.to_csv(os.path.join(OUT,"tuong_quan_spearman.csv"), index=False)
for loai in corr.loai.unique():
    sub = corr[corr.loai==loai]
    sub = sub.reindex(sub.rho.abs().sort_values(ascending=False).index)
    out(f"-- {loai} --")
    out(sub.head(6).to_string(index=False))

out("\n== 4. Diem chat luong theo nong do con (alcohol) ==")
df["alcohol_nhom"] = pd.cut(df.alcohol, [8,9,10,11,12,16], labels=["8-9","9-10","10-11","11-12","12+"])
t = df.groupby(["loai","alcohol_nhom"], observed=True)["quality"].agg(["mean","count"]).round(3)
out(t.to_string())
t.to_csv(os.path.join(OUT,"chat_luong_theo_alcohol.csv"))

out("\n== 5. Ho so median: quality >= 7 vs con lai, theo loai ==")
prof = df.assign(hi=df.quality>=7).groupby(["loai","hi"])[feats].median().round(3)
out(prof.T.to_string())
prof.to_csv(os.path.join(OUT,"ho_so_chat_luong_cao.csv"))

out("\n== 6. Ruou quality >= 8 ==")
top = df[df.quality>=8]
out(top.groupby("loai").size().to_string())
out(top.groupby("loai")[["alcohol","volatile acidity","sulphates","density"]].median().round(3).to_string())

out("\nKhong co cot gia ban, giong nho, vung/quoc gia trong du lieu -> khong tra loi duoc phan do gia va giong nho/Phap.")

# Chart 1: quality distribution by type
fig, ax = plt.subplots(figsize=(8,5))
for loai, c, off in [("Vang do","#8B1E3F",-0.2),("Vang trang","#C9A227",0.2)]:
    s = df[df.loai==loai].quality
    vc = s.value_counts(normalize=True).sort_index()
    ax.bar(vc.index + off, vc.values, width=0.4, label=f"{loai} (n={len(s)})", color=c)
ax.set_xlabel("Điểm chất lượng (0-10, đánh giá cảm quan)")
ax.set_ylabel("Tỷ lệ mẫu")
ax.set_title("Rượu vang trắng có tỷ lệ đạt từ 7 điểm trở lên cao hơn (21,6%) so với rượu vang đỏ (13,6%)")
ax.legend()
fig.tight_layout(); fig.savefig(os.path.join(OUT,"phan_bo_diem_chat_luong.png"), dpi=150); plt.close(fig)

# Chart 2: alcohol vs mean quality
fig, ax = plt.subplots(figsize=(8,5))
for loai, c in [("Vang do","#8B1E3F"),("Vang trang","#C9A227")]:
    g = df[df.loai==loai].groupby("alcohol_nhom", observed=True)["quality"].mean()
    ax.plot(g.index.astype(str), g.values, marker="o", label=loai, color=c)
ax.set_xlabel("Nồng độ cồn (% thể tích), nhóm")
ax.set_ylabel("Điểm chất lượng trung bình")
ax.set_title("Nồng độ cồn càng cao, điểm chất lượng trung bình càng cao ở cả rượu đỏ và rượu trắng")
ax.legend()
fig.tight_layout(); fig.savefig(os.path.join(OUT,"alcohol_va_chat_luong.png"), dpi=150); plt.close(fig)

with open(os.path.join(OUT,"ket_qua_thong_ke.txt"),"w") as f:
    f.write("\n".join(lines))
