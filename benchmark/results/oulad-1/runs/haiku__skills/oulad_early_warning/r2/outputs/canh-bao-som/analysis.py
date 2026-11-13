"""Cảnh báo sớm sinh viên OULAD (mốc ra quyết định: cuối ngày 28).

Chạy từ thư mục dự án:  python outputs/canh-bao-som/analysis.py
Đầu vào: data/aq3_model_table.csv, data/aq1_student_week.csv (chỉ đọc).
Đầu ra: CSV, PNG, metrics.json trong thư mục chứa script.
"""
import os
import json
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score, average_precision_score

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = HERE
ROOT = os.path.dirname(os.path.dirname(HERE))
DATA = os.path.join(ROOT, "data")
K = ["code_module", "code_presentation", "id_student"]
Y = "target_noncompletion"          # 1 = Fail hoặc Withdrawn
CAP = 200                           # sinh viên tối đa / module-kỳ
RECALL_TARGET = 0.70
SEED = 0

m = pd.read_csv(os.path.join(DATA, "aq3_model_table.csv"))
assert not m.duplicated(K).any(), "trùng khóa"
assert len(m) == 13020, len(m)     # quần thể: còn active tại ngày 28
# kết quả cuối kỳ (final_result, label3) chỉ có ở bảng đăng ký đầy đủ; ghép theo khóa
ctx = pd.read_csv(os.path.join(DATA, "context_all_registrations.csv"))
m = m.merge(ctx[K + ["final_result", "label3"]], on=K, how="left", validate="one_to_one")
assert m.final_result.notna().all() and len(m) == 13020
assert (m.final_result.isin(["Fail", "Withdrawn"]).astype(int) == m[Y]).all()  # nhãn mục tiêu khớp kết quả
metrics = {}

# ---------- helpers ----------
def bh(p):
    p = np.asarray(p, float)
    n = len(p)
    o = np.argsort(p)
    q = p[o] * n / (np.arange(n) + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]
    out = np.empty(n)
    out[o] = np.minimum(q, 1)
    return out

def delta_from_u(u, n1, n2):
    # Cliff's delta = P(X>Y) - P(X<Y), với U tính cho mẫu X
    return 2 * u / (n1 * n2) - 1

WEEKS = [1, 2, 3, 4]
GROUPS = ["Pass", "Fail", "Withdrawn"]
NAME = {"homepage": "trang chủ", "oucontent": "nội dung học phần", "resource": "tài liệu",
        "subpage": "trang con", "forumng": "diễn đàn", "quiz": "bài kiểm tra trắc nghiệm", "url": "liên kết"}
EDU = {0: "chưa có bằng cấp chính thức", 1: "dưới A Level", 2: "A Level hoặc tương đương",
       3: "bằng đại học", 4: "sau đại học"}

# ---------- Câu 1: ba nhóm Pass / Fail / Withdrawn trong 4 tuần đầu ----------
q1 = m[m.final_result.isin(GROUPS)].copy()
metrics["q1_n_by_group"] = q1.final_result.value_counts().to_dict()
metrics["n_distinction_excluded_q1"] = int((m.final_result == "Distinction").sum())
cols1 = [f"clicks_w{w}" for w in WEEKS] + [f"active_days_w{w}" for w in WEEKS] + ["clicks_0_28", "active_days_0_28"]
rows = []
for c in cols1:
    g = [q1.loc[q1.final_result == k, c] for k in GROUPS]
    row = {"chi_tieu": c}
    for k, s in zip(GROUPS, g):
        row[f"{k}_trung_vi"] = float(s.median())
        row[f"{k}_tb"] = round(float(s.mean()), 2)
        row[f"{k}_q25"] = float(s.quantile(0.25))
        row[f"{k}_q75"] = float(s.quantile(0.75))
    row["kruskal_p"] = stats.kruskal(*g).pvalue
    rows.append(row)
q1_sum = pd.DataFrame(rows)
pairs = [("Pass", "Fail"), ("Pass", "Withdrawn"), ("Fail", "Withdrawn")]
pw = []
for c in cols1:
    for a, b in pairs:
        xa = q1.loc[q1.final_result == a, c]
        xb = q1.loc[q1.final_result == b, c]
        u, p = stats.mannwhitneyu(xb, xa, alternative="two-sided")
        pw.append({"chi_tieu": c, "so_sanh": f"{b} so với {a}", "delta": delta_from_u(u, len(xa), len(xb)), "p": p})
pw = pd.DataFrame(pw)
pw["q_BH"] = bh(pw.p)
q1_sum.to_csv(os.path.join(OUT, "q1_tuong_tac_4_tuan_theo_nhom.csv"), index=False)
pw.to_csv(os.path.join(OUT, "q1_so_sanh_cap_nhom.csv"), index=False)

fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
colors = {"Pass": "#2a9d8f", "Fail": "#e9c46a", "Withdrawn": "#e76f51"}
for ax, prefix, title in [(axes[0], "clicks_w", "Số lượt truy cập mỗi tuần"),
                          (axes[1], "active_days_w", "Số ngày có truy cập mỗi tuần")]:
    for k in GROUPS:
        sub = q1[q1.final_result == k]
        med = [sub[f"{prefix}{w}"].median() for w in WEEKS]
        q25 = [sub[f"{prefix}{w}"].quantile(0.25) for w in WEEKS]
        q75 = [sub[f"{prefix}{w}"].quantile(0.75) for w in WEEKS]
        ax.plot(WEEKS, med, marker="o", color=colors[k], label=k)
        ax.fill_between(WEEKS, q25, q75, color=colors[k], alpha=0.15)
    ax.set_xticks(WEEKS)
    ax.set_xlabel("Tuần học (tuần 1–4, tức ngày 0–27)")
    ax.set_title(title, fontsize=11)
    ax.grid(alpha=0.3)
axes[0].set_ylabel("Trung vị (vùng: phân vị 25–75)")
axes[0].legend(title="Kết quả cuối kỳ")
fig.suptitle("Tương tác 4 tuần đầu theo kết quả: Pass, Fail, Withdrawn", fontsize=12)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "q1_tuong_tac_theo_tuan.png"), dpi=150)
plt.close(fig)

# ---------- Câu 2: chỉ báo khác biệt giữa hoàn thành và không hoàn thành ----------
m2 = m.copy()
m2["clicks_luy_ke_w2"] = m2.clicks_w1 + m2.clicks_w2
m2["clicks_luy_ke_w3"] = m2.clicks_w1 + m2.clicks_w2 + m2.clicks_w3
m2["clicks_luy_ke_w4"] = m2.clicks_w1 + m2.clicks_w2 + m2.clicks_w3 + m2.clicks_w4
m2["clicks_luy_ke_w1"] = m2.clicks_w1
comp = m2[m2[Y] == 0]     # Pass + Distinction (hoàn thành)
non = m2[m2[Y] == 1]      # Fail + Withdrawn (không hoàn thành)
CONT = (["clicks_w1", "clicks_w2", "clicks_w3", "clicks_w4", "active_days_w1", "active_days_w2",
         "active_days_w3", "active_days_w4", "clicks_luy_ke_w1", "clicks_luy_ke_w2", "clicks_luy_ke_w3",
         "clicks_luy_ke_w4", "clicks_0_28", "active_days_0_28", "n_sites_0_28", "days_since_last_active_d28",
         "clicks_pre_start", "active_days_pre_start", "clicks_change_w1_w4", "clicks_quiz_0_28",
         "clicks_forumng_0_28", "clicks_oucontent_0_28", "clicks_resource_0_28", "tma1_score",
         "tma1_days_before_deadline", "num_of_prev_attempts", "studied_credits", "highest_education_ord",
         "registration_lead_days"])
BIN = ["tma1_submitted_by_d28", "tma1_on_time", "no_vle_activity_0_28", "seen_in_earlier_presentation",
       "late_registration_1_28"]
rows2 = []
for c in CONT:
    a = comp[c].dropna()
    b = non[c].dropna()
    u, p = stats.mannwhitneyu(b, a, alternative="two-sided")
    rows2.append({"chi_tieu": c, "loai": "liên tục", "hoan_thanh": float(a.median()),
                  "khong_hoan_thanh": float(b.median()), "hieu_do": delta_from_u(u, len(a), len(b)), "p": p})
for c in BIN:
    a = comp[c].fillna(0)
    b = non[c].fillna(0)
    ct = [[(a == 1).sum(), (a == 0).sum()], [(b == 1).sum(), (b == 0).sum()]]
    p = stats.chi2_contingency(ct)[1]
    rows2.append({"chi_tieu": c, "loai": "nhị phân (tỉ lệ có)", "hoan_thanh": float(a.mean()),
                  "khong_hoan_thanh": float(b.mean()), "hieu_do": float(b.mean() - a.mean()), "p": p})
q2 = pd.DataFrame(rows2)
q2["q_BH"] = bh(q2.p)
q2["co_y_nghia"] = (q2.q_BH < 0.05) & (
    ((q2.loai == "liên tục") & (q2.hieu_do.abs() >= 0.147)) | ((q2.loai != "liên tục") & (q2.hieu_do.abs() >= 0.05)))
q2.to_csv(os.path.join(OUT, "q2_chi_bao_hoan_thanh_vs_khong.csv"), index=False)

def onset(prefix):
    flags = [bool(q2.loc[q2.chi_tieu == f"{prefix}{w}", "co_y_nghia"].iloc[0]) for w in WEEKS]
    first = next((w for w, f in zip(WEEKS, flags) if f), None)
    sustained = first is not None and all(flags[WEEKS.index(first):])
    return {"tuan_dau_co_y_nghia": first, "duy_tri_den_cuoi": sustained, "co_y_nghia_theo_tuan": flags}

metrics["q2_onset"] = {
    "clicks_theo_tuan": onset("clicks_w"),
    "active_days_theo_tuan": onset("active_days_w"),
    "clicks_luy_ke": onset("clicks_luy_ke_w"),
}
metrics["q2_n_significant_indicators"] = int(q2.co_y_nghia.sum())
metrics["q2_n_tested"] = int(len(q2))

wk_rows = q2[q2.chi_tieu.str.match(r"^(clicks_w|active_days_w)\d$")]
fig, ax = plt.subplots(figsize=(8, 4.2))
x = np.arange(len(WEEKS))
w_ = 0.38
for i, pref in enumerate(["clicks_w", "active_days_w"]):
    vals = [wk_rows.loc[wk_rows.chi_tieu == f"{pref}{w}", "hieu_do"].iloc[0] for w in WEEKS]
    sig = [bool(wk_rows.loc[wk_rows.chi_tieu == f"{pref}{w}", "co_y_nghia"].iloc[0]) for w in WEEKS]
    bars = ax.bar(x + (i - 0.5) * w_, vals, w_, label=("Lượt truy cập" if i == 0 else "Số ngày truy cập"),
                  color=["#264653" if i == 0 else "#8ab17d"] * 4)
    for b_, s_ in zip(bars, sig):
        if not s_:
            b_.set_alpha(0.35)
ax.axhline(0, color="black", lw=0.8)
ax.axhline(-0.147, color="grey", ls="--", lw=0.8)
ax.set_xticks(x)
ax.set_xticklabels([f"Tuần {w}" for w in WEEKS])
ax.set_ylabel("Hiệu độ (Cliff's delta)\nâm = thấp hơn ở nhóm không hoàn thành")
ax.set_title("Khác biệt tương tác giữa hoàn thành và không hoàn thành (cột nhạt: không có ý nghĩa)", fontsize=10)
ax.legend()
ax.grid(alpha=0.3, axis="y")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "q2_hieu_do_theo_tuan.png"), dpi=150)
plt.close(fig)

# ---------- Câu 3: dự báo chỉ bằng dữ liệu đến ngày 28 ----------
FEATS = [c for c in m.columns if c not in K + ["split", "final_result", "label3", Y,
                                                "flag_high_activity", "log_clicks_0_28"]]
metrics["n_features"] = len(FEATS)
tr = m[m.split == "train"]
va = m[m.split == "validation"]
te = m[m.split == "test"]
metrics["n_train_val_test"] = [len(tr), len(va), len(te)]
metrics["prevalence_train_val_test"] = [round(d[Y].mean(), 4) for d in (tr, va, te)]

def make_lr():
    return make_pipeline(SimpleImputer(strategy="median", add_indicator=True), StandardScaler(),
                         LogisticRegression(C=1.0, max_iter=5000))

def make_hgb():
    return HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_leaf_nodes=15,
                                          min_samples_leaf=40, l2_regularization=1.0, random_state=SEED)

def thr_for_recall(yt, score, target):
    """Ngưỡng cao nhất đạt recall >= target (ít sinh viên bị gắn cờ nhất)."""
    o = np.argsort(-score)
    s = score[o]
    tp = np.cumsum(yt[o])
    rec = tp / yt.sum()
    idx = np.argmax(rec >= target)
    return s[idx]

def k_share_for_recall(yt, score, target):
    o = np.argsort(-score)
    rec = np.cumsum(yt[o]) / yt.sum()
    return (np.argmax(rec >= target) + 1) / len(yt)

lr = make_lr().fit(tr[FEATS], tr[Y])
hgb = make_hgb().fit(tr[FEATS], tr[Y])
scores = {
    "Hồi quy logistic (chọn)": {"val": lr.predict_proba(va[FEATS])[:, 1], "test": lr.predict_proba(te[FEATS])[:, 1]},
    "Gradient boosting (so sánh)": {"val": hgb.predict_proba(va[FEATS])[:, 1], "test": hgb.predict_proba(te[FEATS])[:, 1]},
    "Cơ sở: ít lượt truy cập đến ngày 28": {"val": -va.clicks_0_28.values.astype(float),
                                             "test": -te.clicks_0_28.values.astype(float)},
}
rows3 = []
for name, s in scores.items():
    thr = thr_for_recall(va[Y].values, s["val"], RECALL_TARGET)
    pred = s["test"] >= thr
    tp = int((pred & (te[Y].values == 1)).sum())
    rows3.append({
        "mo_hinh": name,
        "auc_validation": roc_auc_score(va[Y], s["val"]),
        "auc_test": roc_auc_score(te[Y], s["test"]),
        "ap_test": average_precision_score(te[Y], s["test"]),
        "ap_ngau_nhien_test": te[Y].mean(),
        "nguong_chon_tren_validation": float(thr),
        "test_so_gan_co": int(pred.sum()),
        "test_ti_le_gan_co": float(pred.mean()),
        "test_recall_tai_nguong": tp / te[Y].sum(),
        "test_precision_tai_nguong": tp / max(pred.sum(), 1),
        "ti_le_sv_can_lien_he_de_dat_70pct_test": k_share_for_recall(te[Y].values, s["test"], RECALL_TARGET),
    })
q3 = pd.DataFrame(rows3)
q3.to_csv(os.path.join(OUT, "q3_do_luong_du_bao.csv"), index=False)
metrics["q3"] = q3.round(4).to_dict(orient="records")

fig, ax = plt.subplots(figsize=(7.5, 5))
for name, s in scores.items():
    o = np.argsort(-s["test"])
    cum = np.cumsum(te[Y].values[o]) / te[Y].sum()
    xs = np.arange(1, len(o) + 1) / len(o)
    ax.plot(xs, cum, label=name)
cap_share = float(np.mean([CAP / n for n in m.groupby(["code_module", "code_presentation"]).size()]))
ax.axhline(RECALL_TARGET, color="grey", ls="--", lw=1)
ax.text(0.98, RECALL_TARGET + 0.02, "Mục tiêu 70%", ha="right", fontsize=9, color="grey")
ax.axvline(cap_share, color="#e76f51", ls=":", lw=1.2)
ax.text(cap_share + 0.01, 0.05, f"Giới hạn nhân lực\n(~{cap_share:.0%} sinh viên)", color="#e76f51", fontsize=9)
ax.set_xlabel("Tỉ lệ sinh viên được liên hệ (xếp theo rủi ro giảm dần)")
ax.set_ylabel("Tỉ lệ sinh viên không hoàn thành được bắt")
ax.set_title("Tập test (2014J): bắt được bao nhiêu sinh viên không hoàn thành?", fontsize=11)
ax.legend(fontsize=8, loc="lower right")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "q3_duong_bat_duoc_tren_test.png"), dpi=150)
plt.close(fig)

# ---------- Câu 4: ưu tiên 200 sinh viên mỗi module-kỳ ----------
def eval_topk(df, score, label):
    d = df.copy()          # giữ đủ cột đặc trưng để giải thích ở câu 5
    d["score"] = score
    out, picks = [], []
    for (mod, pres), g in d.groupby(["code_module", "code_presentation"]):
        top = g.sort_values(["score", "clicks_0_28"], ascending=[False, True]).head(CAP).copy()
        top["thu_hang"] = np.arange(1, len(top) + 1)
        top["module_ky"] = f"{mod}-{pres}"
        picks.append(top)
        hits = int(top[Y].sum())
        tot = int(g[Y].sum())
        out.append({"mo_hinh": label, "module": mod, "ky": pres, "n_quan_the": len(g),
                    "n_khong_hoan_thanh": tot, "ti_le_nen": tot / len(g), "so_lien_he": len(top),
                    "trung": hits, "ti_le_trung": hits / len(top), "recall_tren_module_ky": hits / tot,
                    "ky_vong_ngau_nhien": CAP * tot / len(g)})
    return pd.DataFrame(out), pd.concat(picks)

s_test_lr = scores["Hồi quy logistic (chọn)"]["test"]
q4_test, picks_test = eval_topk(te, s_test_lr, "Hồi quy logistic, tập test 2014J")
q4_test_base, _ = eval_topk(te, -te.clicks_0_28.values.astype(float), "Cơ sở: ít lượt truy cập đến ngày 28")
q4_test_rand_base_hits = float(CAP * te[Y].mean())

# kiểm định chéo theo kỳ (leave-one-presentation-out): mỗi kỳ là một lần kiểm tra
lopo_rows, lopo_base_rows = [], []
lopo_auc = []
for pres in sorted(m.code_presentation.unique()):
    trn = m[m.code_presentation != pres]
    tst = m[m.code_presentation == pres].copy()
    mdl = make_lr().fit(trn[FEATS], trn[Y])
    s = mdl.predict_proba(tst[FEATS])[:, 1]
    lopo_auc.append({"ky": pres, "auc_mo_hinh": roc_auc_score(tst[Y], s),
                     "auc_co_so_it_click": roc_auc_score(tst[Y], -tst.clicks_0_28.values.astype(float)),
                     "ti_le_nen": tst[Y].mean()})
    res, _ = eval_topk(tst, s, f"Kiểm định chéo, giữ kỳ {pres} ra")
    lopo_rows.append(res)
    resb, _ = eval_topk(tst, -tst.clicks_0_28.values.astype(float), f"Cơ sở, giữ kỳ {pres} ra")
    lopo_base_rows.append(resb)
q4_lopo = pd.concat(lopo_rows, ignore_index=True)
q4_lopo_base = pd.concat(lopo_base_rows, ignore_index=True)
lopo_auc = pd.DataFrame(lopo_auc)
# trần lý thuyết: nếu xếp hạng hoàn hảo, 200 đầu bắt được tối đa min(200, tổng) không hoàn thành
q4_lopo["tran_recall_ly_thuyet"] = np.minimum(CAP, q4_lopo.n_khong_hoan_thanh) / q4_lopo.n_khong_hoan_thanh
metrics["q4_lopo_base_total_hits"] = int(q4_lopo_base.trung.sum())
metrics["q4_lopo_max_recall_possible"] = float(np.minimum(CAP, q4_lopo.n_khong_hoan_thanh).sum() / q4_lopo.n_khong_hoan_thanh.sum())

# đối chiếu trên validation (2014B) với mô hình huấn luyện trên train
q4_val, _ = eval_topk(va, scores["Hồi quy logistic (chọn)"]["val"], "Hồi quy logistic, validation 2014B")
q4_val_base, _ = eval_topk(va, -va.clicks_0_28.values.astype(float), "Cơ sở, validation 2014B")
metrics["q4_val_hits_lr"] = int(q4_val.trung.sum())
metrics["q4_val_hits_base"] = int(q4_val_base.trung.sum())
metrics["q4_val_contacts"] = int(q4_val.so_lien_he.sum())
q4_val_all = pd.concat([q4_val, q4_val_base], ignore_index=True)
q4_val_all.to_csv(os.path.join(OUT, "q4_hieu_qua_200_tren_validation.csv"), index=False)

q4_all = pd.concat([q4_test, q4_test_base], ignore_index=True)
q4_all.to_csv(os.path.join(OUT, "q4_hieu_qua_200_tren_test.csv"), index=False)
q4_lopo.to_csv(os.path.join(OUT, "q4_kiem_dinh_cheo_8_module_ky.csv"), index=False)
q4_lopo_base.to_csv(os.path.join(OUT, "q4_kiem_dinh_cheo_co_so_it_click.csv"), index=False)
lopo_auc.to_csv(os.path.join(OUT, "q4_auc_kiem_dinh_cheo.csv"), index=False)
metrics["q4_test_total_hits"] = int(q4_test.trung.sum())
metrics["q4_test_total_contacts"] = int(q4_test.so_lien_he.sum())
metrics["q4_test_total_noncompletion"] = int(q4_test.n_khong_hoan_thanh.sum())
metrics["q4_test_recall_200"] = float(q4_test.trung.sum() / q4_test.n_khong_hoan_thanh.sum())
metrics["q4_test_precision_200"] = float(q4_test.trung.sum() / q4_test.so_lien_he.sum())
metrics["q4_test_baseline_precision_200"] = float(q4_test_base.trung.sum() / q4_test_base.so_lien_he.sum())
metrics["q4_test_random_expected_hits"] = round(q4_test_rand_base_hits * len(q4_test), 1)
metrics["q4_test_baseline_clicks_hits"] = int(q4_test_base.trung.sum())
metrics["q4_lopo_total_hits"] = int(q4_lopo.trung.sum())
metrics["q4_lopo_total_contacts"] = int(q4_lopo.so_lien_he.sum())
metrics["q4_lopo_total_noncompletion"] = int(q4_lopo.n_khong_hoan_thanh.sum())
metrics["q4_lopo_auc"] = lopo_auc.round(4).to_dict(orient="records")

fig, ax = plt.subplots(figsize=(10, 4.6))
lab = [f"{r.module}\n{r.ky}" for r in q4_lopo.itertuples()]
xx = np.arange(len(lab))
ax.bar(xx - 0.25, q4_lopo.so_lien_he, 0.25, color="#d3d3d3", label="Số liên hệ (giới hạn 200)")
ax.bar(xx, q4_lopo.trung, 0.25, color="#264653", label="Trúng (không hoàn thành trong danh sách)")
ax.bar(xx + 0.25, q4_lopo.n_khong_hoan_thanh, 0.25, color="#e76f51", alpha=0.5,
       label="Tổng sinh viên không hoàn thành trong module-kỳ")
ax.set_xticks(xx)
ax.set_xticklabels(lab, fontsize=8)
ax.set_title("Danh sách 200 mỗi module-kỳ (kiểm định chéo theo kỳ): trúng bao nhiêu?", fontsize=11)
ax.set_ylabel("Số sinh viên")
ax.legend(fontsize=8)
ax.grid(alpha=0.3, axis="y")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "q4_trung_theo_module_ky.png"), dpi=150)
plt.close(fig)

# ---------- Câu 5: yếu tố đóng góp nhiều nhất cho từng sinh viên trong danh sách ----------
imp = lr.named_steps
names = imp[next(iter(imp))].get_feature_names_out(FEATS)
Xs = imp["standardscaler"].transform(imp["simpleimputer"].transform(picks_test[FEATS]))
coef = imp["logisticregression"].coef_[0]
contrib = Xs * coef
med = tr[FEATS].median()

def phrase(feat, v, mv):
    if feat.startswith("missingindicator_"):
        base = feat.replace("missingindicator_", "")
        if base.startswith("tma1"):
            return "chưa có dữ liệu bài đánh giá TMA1 (chưa nộp trước ngày 28)"
        return f"thiếu dữ liệu {base}"
    if pd.isna(v):
        return f"thiếu {feat}"
    if feat.startswith("clicks_w") or feat.startswith("active_days_w") or feat in [
            "clicks_0_28", "active_days_0_28", "n_sites_0_28", "clicks_pre_start", "active_days_pre_start",
            "clicks_luy_ke_w1"]:
        label = {"clicks_0_28": "tổng lượt truy cập đến ngày 28", "active_days_0_28": "số ngày có truy cập đến ngày 28",
                 "n_sites_0_28": "số loại tài nguyên đã dùng đến ngày 28", "clicks_pre_start": "lượt truy cập trước khai giảng",
                 "active_days_pre_start": "số ngày truy cập trước khai giảng"}.get(feat)
        if label is None:
            wk = feat[-1]
            label = (f"số lượt truy cập tuần {wk}" if feat.startswith("clicks") else f"số ngày truy cập tuần {wk}")
        return f"{label} là {v:.0f} (trung vị {mv:.0f})"
    if feat == "days_since_last_active_d28":
        return f"đã {v:.0f} ngày chưa truy cập lại tính đến ngày 28 (trung vị {mv:.0f})"
    if feat == "clicks_change_w1_w4":
        return "lượng truy cập từ tuần 1 đến tuần 4 " + ("giảm" if v < 0 else "tăng")
    if feat == "no_vle_activity_0_28":
        return "chưa có hoạt động nào trên hệ thống học trực tuyến đến ngày 28" if v == 1 else \
            "vẫn có hoạt động trên hệ thống học trực tuyến"
    if feat.startswith("clicks_") and feat.endswith("_0_28"):
        key = feat[len("clicks_"):-len("_0_28")]
        return f"lượt vào {NAME.get(key, key)} đến ngày 28 là {v:.0f} (trung vị {mv:.0f})"
    if feat == "tma1_submitted_by_d28":
        return "đã nộp bài đánh giá TMA1 trước ngày 28" if v == 1 else "chưa nộp bài đánh giá TMA1 trước ngày 28"
    if feat == "tma1_on_time":
        return "nộp TMA1 đúng hạn" if v == 1 else "nộp TMA1 trễ hạn"
    if feat == "tma1_days_before_deadline":
        return (f"nộp TMA1 trước hạn {v:.0f} ngày" if v >= 0 else f"nộp TMA1 trễ {abs(v):.0f} ngày so với hạn")
    if feat == "tma1_score":
        return f"điểm TMA1 là {v:.0f} (trung vị {mv:.0f})"
    if feat == "num_of_prev_attempts":
        return f"đã từng học lại {v:.0f} lần trước đây"
    if feat == "studied_credits":
        return f"đăng ký {v:.0f} tín chỉ (trung vị {mv:.0f})"
    if feat == "highest_education_ord":
        return f"trình độ học vấn ban đầu: {EDU.get(int(v), v)}"
    if feat == "registration_lead_days":
        return f"đăng ký {v:.0f} ngày trước khai giảng (trung vị {mv:.0f})"
    if feat == "seen_in_earlier_presentation":
        return "đã từng học module này ở kỳ trước" if v == 1 else "lần đầu học module này"
    if feat == "late_registration_1_28":
        return "đăng ký muộn sau ngày 1" if v == 1 else "đăng ký đúng thời gian"
    if feat == "days_observable_0_28":
        return f"chỉ được theo dõi {v:.0f} ngày (đăng ký muộn)"
    return f"{feat} = {v:.2f} (trung vị {mv:.2f})"

expl_rows = []
picks_test = picks_test.reset_index(drop=True)
raw = picks_test[FEATS]
for i in range(len(picks_test)):
    c = pd.Series(contrib[i], index=names)
    c = c[c > 0].sort_values(ascending=False).head(3)
    drivers = []
    for nm, val in c.items():
        base = nm.replace("missingindicator_", "")
        v = np.nan if nm.startswith("missingindicator_") else raw.at[i, base]
        drivers.append({"feat": nm, "dong_gop_log_odds": float(val), "mo_ta": phrase(nm, v, med.get(base, np.nan))})
    expl_rows.append(drivers)

# xác suất dự báo của các sinh viên trong danh sách (cùng thứ tự picks_test)
te_idx = te.reset_index(drop=True)
pos = {(r.code_module, r.code_presentation, r.id_student): i for i, r in te_idx.iterrows()}
p_list = [float(s_test_lr[pos[(r.code_module, r.code_presentation, r.id_student)]]) for r in picks_test.itertuples()]

def sentence_block(r, drivers, p):
    # Không đưa xác suất thô vào câu cho cố vấn: xác suất có thể lệch khi tỉ lệ không hoàn thành đổi theo kỳ.
    head = (f"Sinh viên {r.id_student} (module {r.code_module}, kỳ {r.code_presentation}) nằm trong nhóm "
            f"ưu tiên cao nhất của module-kỳ này (hạng {r.thu_hang} trong {CAP}).")
    if not drivers:
        mid = "Không có yếu tố nào nổi bật đẩy nguy cơ lên so với sinh viên trung bình."
    else:
        mid = "Các yếu tố đẩy nguy cơ lên nhiều nhất là: " + "; ".join(d["mo_ta"] for d in drivers) + "."
    tail = ("Đây là mối liên hệ trong dữ liệu, không phải nguyên nhân chắc chắn; "
            "nên trò chuyện trực tiếp để hiểu hoàn cảnh trước khi kết luận.")
    return f"{head} {mid} {tail}"

out5 = []
for i, r in enumerate(picks_test.itertuples()):
    drv = expl_rows[i]
    out5.append({"code_module": r.code_module, "code_presentation": r.code_presentation, "id_student": r.id_student,
                 "thu_hang": r.thu_hang, "xac_suat_khong_hoan_thanh": p_list[i],
                 "ket_qua_thuc_te_chi_de_danh_gia": r.final_result,
                 "yeu_to_1": drv[0]["mo_ta"] if len(drv) > 0 else "",
                 "yeu_to_2": drv[1]["mo_ta"] if len(drv) > 1 else "",
                 "yeu_to_3": drv[2]["mo_ta"] if len(drv) > 2 else "",
                 "giai_thich_cho_co_van": sentence_block(r, drv, p_list[i])})
q5 = pd.DataFrame(out5)
q5.to_csv(os.path.join(OUT, "q4_danh_sach_uu_tien_test_2014J_kem_giai_thich.csv"), index=False)

# tần suất các yếu tố đứng đầu trong danh sách
from collections import Counter
cnt = Counter()
for drv in expl_rows:
    for d in drv:
        cnt[d["feat"]] += 1
freq = pd.DataFrame([{"yeu_to": k,
                      "mo_ta_ngan": ("chưa có điểm TMA1" if k == "missingindicator_tma1_score" else k),
                      "so_sinh_vien_co_trong_top3": v, "ti_le": v / len(expl_rows)}
                     for k, v in cnt.most_common()])
freq.to_csv(os.path.join(OUT, "q5_tan_suat_yeu_to_trong_danh_sach.csv"), index=False)
metrics["q5_n_students"] = len(expl_rows)
metrics["q5_top_drivers"] = freq.head(8).round(3).to_dict(orient="records")

# hệ số lr để kiểm tra chiều tác động
coef_df = pd.DataFrame({"dac_trung": names, "he_so_chuan_hoa": coef}).sort_values("he_so_chuan_hoa", ascending=False)
coef_df.to_csv(os.path.join(OUT, "q3_he_so_hoi_quy_logistic.csv"), index=False)

with open(os.path.join(OUT, "metrics.json"), "w", encoding="utf-8") as f:
    json.dump(metrics, f, ensure_ascii=False, indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o))
print(json.dumps(metrics, ensure_ascii=False, indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o))[:6000])
