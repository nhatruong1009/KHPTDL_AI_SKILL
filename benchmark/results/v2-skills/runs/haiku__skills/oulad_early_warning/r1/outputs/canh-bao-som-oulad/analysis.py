"""Phân tích cảnh báo sớm OULAD (module BBB/FFF, 4 kỳ), mốc quyết định: cuối ngày 28.

Chạy từ thư mục workspace:  python outputs/canh-bao-som-oulad/analysis.py
Dữ liệu đọc từ ./data (chỉ đọc). Kết quả ghi vào thư mục của script.
"""
from pathlib import Path
import json

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, roc_curve

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / "data"
K = ["code_module", "code_presentation", "id_student"]
GROUPS = ["Pass", "Fail", "Withdrawn"]
TARGET_RECALL = 0.70
SEED = 0

# ---------------------------------------------------------------- load
m = pd.read_csv(DATA / "aq3_model_table.csv")          # 13,020 lượt đăng ký còn học đến ngày 28
a2 = pd.read_csv(DATA / "aq2_diagnostic_table.csv")    # cùng lượt đăng ký, có label3 và thuộc tính
aud = pd.read_csv(DATA / "aq3_audit_attributes.csv")   # thuộc tính nhạy cảm: CHỈ dùng để kiểm toán
w = pd.read_csv(DATA / "aq1_student_week.csv")         # tương tác theo tuần 1-4
params = json.loads((DATA / "aq4_decision_params.json").read_text(encoding="utf-8"))

m = m.merge(a2[K + ["label3", "final_result"]], on=K, how="left", validate="one_to_one")
assert len(m) == 13020 and m["label3"].notna().all()
aud_ok = aud.merge(m[K], on=K, how="inner", validate="one_to_one")
assert len(aud_ok) == 13020

# kiểm tra: số liệu theo tuần trong aq3 khớp với aq1
wk_clicks = w.pivot_table(index=K, columns="week", values="clicks")
wk_active = w.pivot_table(index=K, columns="week", values="active_days")
mi = m.set_index(K)
for i in range(1, 5):
    assert (mi[f"clicks_w{i}"] == wk_clicks[i]).all(), f"clicks tuần {i} không khớp"
    assert (mi[f"active_days_w{i}"] == wk_active[i]).all(), f"active tuần {i} không khớp"
print("Kiểm tra khớp aq1/aq3: OK")

# nhãn nhị phân: không hoàn thành = Fail hoặc Withdrawn
m["nc"] = m["target_noncompletion"].astype(int)
print("Phân bố nhãn label3 (13,020 lượt):", m["label3"].value_counts().to_dict())
print("Tỷ lệ không hoàn thành:", round(m["nc"].mean(), 4))


def holm(p):
    p = np.asarray(p, dtype=float)
    n = len(p)
    order = np.argsort(p)
    adj = np.empty(n)
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, (n - rank) * p[idx])
        adj[idx] = min(running, 1.0)
    return adj


def mw_auc(x1, x0):
    """p-value (Mann-Whitney) và AUC = P(x1 > x0) (ràng buộc hòa = 0.5)."""
    res = stats.mannwhitneyu(x1, x0, alternative="two-sided")
    return res.pvalue, res.statistic / (len(x1) * len(x0))


# ---------------------------------------------------------------- Q1
WEEK_CLICKS = [f"clicks_w{i}" for i in range(1, 5)]
WEEK_ACTIVE = [f"active_days_w{i}" for i in range(1, 5)]
Q1_COLS = WEEK_CLICKS + WEEK_ACTIVE + ["clicks_0_28", "active_days_0_28", "n_sites_0_28",
                                       "days_since_last_active_d28"]
rows = []
for g in GROUPS:
    s = m[m.label3 == g]
    r = {"nhom": g, "so_luot": len(s)}
    for c in Q1_COLS:
        r[f"tb_{c}"] = round(s[c].mean(), 2)
        r[f"tv_{c}"] = round(s[c].median(), 1)
    r["ty_le_nop_tma1_truoc_ngay28"] = round(s["tma1_submitted_by_d28"].mean(), 3)
    r["ty_le_khong_hoat_dong_vle_0_28"] = round(s["no_vle_activity_0_28"].mean(), 3)
    rows.append(r)
q1 = pd.DataFrame(rows)
q1.to_csv(OUT := HERE / "q1_tuong_tac_4_tuan_theo_nhom.csv", index=False)

kw_rows = []
for c in Q1_COLS:
    samples = [m.loc[m.label3 == g, c] for g in GROUPS]
    kw_rows.append({"chi_bao": c, "p_kruskal_wallis": stats.kruskal(*samples).pvalue})
pair_rows = []
for a, b in [("Pass", "Fail"), ("Pass", "Withdrawn"), ("Fail", "Withdrawn")]:
    for c in ["clicks_0_28", "active_days_0_28", "clicks_w1", "active_days_w1"]:
        pval, auc = mw_auc(m.loc[m.label3 == a, c], m.loc[m.label3 == b, c])
        pair_rows.append({"nhom_1": a, "nhom_2": b, "chi_bao": c, "auc_nhom1_cao_hon": round(auc, 3), "p": pval})
pr = pd.DataFrame(pair_rows)
pr["p_holm"] = holm(pr["p"])
pr.to_csv(HERE / "q1_so_sanh_cap_nhom.csv", index=False)
pd.DataFrame(kw_rows).to_csv(HERE / "q1_kiem_dinh_3_nhom.csv", index=False)
print("\n=== Q1 ===")
print(q1.T.to_string())
print(pd.DataFrame(kw_rows).to_string())
print(pr.round(4).to_string())

# ---------------------------------------------------------------- Q2
NUM_IND = Q1_COLS + ["clicks_change_w1_w4", "clicks_pre_start", "active_days_pre_start",
                     "num_of_prev_attempts", "studied_credits", "registration_lead_days"]
BIN_IND = ["tma1_submitted_by_d28", "tma1_on_time", "no_vle_activity_0_28"]
nc = m["nc"].eq(1)
rows2 = []
for c in NUM_IND:
    p, auc = mw_auc(m.loc[nc, c], m.loc[~nc, c])
    rows2.append({"chi_bao": c, "loai": "so", "trung_vi_khong_hoan_thanh": m.loc[nc, c].median(),
                  "trung_vi_hoan_thanh": m.loc[~nc, c].median(),
                  "auc_khong_hoan_thanh_cao_hon": round(auc, 3), "p": p})
for c in BIN_IND:
    tab = pd.crosstab(m[c], m["nc"])
    p = stats.chi2_contingency(tab)[1]
    rows2.append({"chi_bao": c, "loai": "nhi_phan", "trung_vi_khong_hoan_thanh": round(m.loc[nc, c].mean(), 3),
                  "trung_vi_hoan_thanh": round(m.loc[~nc, c].mean(), 3),
                  "auc_khong_hoan_thanh_cao_hon": np.nan, "p": p})
q2 = pd.DataFrame(rows2)
q2["p_holm"] = holm(q2["p"])
q2["co_y_nghia_holm_0_05"] = q2["p_holm"] < 0.05
q2.to_csv(HERE / "q2_chi_bao_hoan_thanh_vs_khong.csv", index=False)

rows_t = []
for i in range(1, 5):
    for meas, col in [("luot_truy_cap", f"clicks_w{i}"), ("so_ngay_hoat_dong", f"active_days_w{i}")]:
        p, auc = mw_auc(m.loc[nc, col], m.loc[~nc, col])
        rows_t.append({"chi_bao": meas, "tuan": i, "trung_vi_khong_hoan_thanh": m.loc[nc, col].median(),
                       "trung_vi_hoan_thanh": m.loc[~nc, col].median(),
                       "auc_khong_hoan_thanh_cao_hon": round(auc, 3), "p": p})
qt = pd.DataFrame(rows_t)
qt["p_holm"] = holm(qt["p"])
qt["co_y_nghia_holm_0_05"] = qt["p_holm"] < 0.05
qt.to_csv(HERE / "q2_khac_biet_theo_tuan.csv", index=False)
first_week = {}
for meas in ["luot_truy_cap", "so_ngay_hoat_dong"]:
    sub = qt[(qt.chi_bao == meas) & qt.co_y_nghia_holm_0_05]
    first_week[meas] = int(sub.tuan.min()) if len(sub) else None
print("\n=== Q2 ===")
print(q2.round(4).to_string())
print(qt.round(4).to_string())
print("Tuần đầu có khác biệt có ý nghĩa (Holm):", first_week)

# ---------------------------------------------------------------- Q3
FEATS = (WEEK_CLICKS + WEEK_ACTIVE +
         ["clicks_0_28", "active_days_0_28", "n_sites_0_28", "clicks_change_w1_w4",
          "days_since_last_active_d28", "clicks_pre_start", "active_days_pre_start",
          "no_vle_activity_0_28", "clicks_homepage_0_28", "clicks_oucontent_0_28",
          "clicks_resource_0_28", "clicks_subpage_0_28", "clicks_forumng_0_28",
          "clicks_quiz_0_28", "clicks_url_0_28", "tma1_submitted_by_d28", "tma1_on_time",
          "tma1_days_before_deadline", "num_of_prev_attempts", "studied_credits",
          "registration_lead_days", "seen_in_earlier_presentation", "late_registration_1_28",
          "days_observable_0_28"])
# Loại khỏi mô hình chính: tma1_score (không có ngày chấm trong dữ liệu -> không biết có sẵn trước ngày 28),
# label3/final_result/date_unregistration (kết quả hoặc tương lai), thuộc tính nhạy cảm (gender, age, disability,
# imd, region, highest_education), flag_high_activity/log_clicks (suy ra từ biến khác).
m["tma1_days_before_deadline"] = m["tma1_days_before_deadline"].fillna(0)  # chưa nộp -> 0, cờ nộp cho biết
X = m[FEATS].astype(float)
y = m["nc"].to_numpy()
tr = m["split"].eq("train").to_numpy()
va = m["split"].eq("validation").to_numpy()
te = m["split"].eq("test").to_numpy()
print("\nSố dòng train/validation/test:", tr.sum(), va.sum(), te.sum())


def threshold_for_recall(y_true, p, target):
    """Ngưỡng xác suất nhỏ nhất (nhiều cảnh báo nhất có thể ít hơn) đạt recall >= target."""
    order = np.argsort(-p)
    ys = y_true[order]
    ps = p[order]
    tp = np.cumsum(ys)
    k = np.where(tp / ys.sum() >= target)[0][0]
    return ps[k]


def metrics(y_true, p, thr):
    flag = p >= thr
    tp = (flag & (y_true == 1)).sum()
    return {"AUC": roc_auc_score(y_true, p), "PR_AUC": average_precision_score(y_true, p),
            "ngưỡng": thr, "recall": tp / y_true.sum(), "precision": tp / max(flag.sum(), 1),
            "ty_le_bi_canh_bao": flag.mean(), "so_bi_canh_bao": int(flag.sum()),
            "so_khong_hoan_thanh": int(y_true.sum()), "so_luot": len(y_true)}


lr = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=5000))
lr.fit(X.loc[tr], y[tr])
p_lr_va = lr.predict_proba(X.loc[va])[:, 1]
hgb = HistGradientBoostingClassifier(learning_rate=0.05, max_iter=300, max_leaf_nodes=15,
                                     min_samples_leaf=40, l2_regularization=1.0, random_state=SEED)
hgb.fit(X.loc[tr], y[tr])
p_hgb_va = hgb.predict_proba(X.loc[va])[:, 1]
auc_lr_va, auc_hgb_va = roc_auc_score(y[va], p_lr_va), roc_auc_score(y[va], p_hgb_va)
# chọn mô hình trên validation; chỉ chọn HGB nếu hơn LR > 0.01 AUC (ưu tiên giải thích được)
use_hgb = (auc_hgb_va - auc_lr_va) > 0.01
chosen_name = "HGB" if use_hgb else "LR"
chosen = hgb if use_hgb else lr
p_va = p_hgb_va if use_hgb else p_lr_va
p_te = chosen.predict_proba(X.loc[te])[:, 1]
print(f"\nAUC validation: LR={auc_lr_va:.4f}, HGB={auc_hgb_va:.4f} -> chọn {chosen_name}")

thr = threshold_for_recall(y[va], p_va, TARGET_RECALL)
res_va = metrics(y[va], p_va, thr)
res_te = metrics(y[te], p_te, thr)  # ngưỡng cố định, chốt trên validation
# biến thể: cùng tỷ lệ bị cảnh báo chốt trên validation, áp lên test theo thứ hạng
share = res_va["ty_le_bi_canh_bao"]
thr_rank_te = np.quantile(p_te, 1 - share)
res_te_rank = metrics(y[te], p_te, thr_rank_te)

# baseline: chỉ lượt truy cập tổng 0-28
base = make_pipeline(StandardScaler(), LogisticRegression(max_iter=5000))
base.fit(X.loc[tr, ["clicks_0_28"]], y[tr])
p_base_te = base.predict_proba(X.loc[te, ["clicks_0_28"]])[:, 1]
base_auc_te = roc_auc_score(y[te], p_base_te)
base_thr = threshold_for_recall(y[va], base.predict_proba(X.loc[va, ["clicks_0_28"]])[:, 1], TARGET_RECALL)
res_base_te = metrics(y[te], p_base_te, base_thr)

# nhạy cảm: thêm tma1_score (chỉ để báo cáo, không dùng cho quyết định)
Xs = X.copy()
Xs["tma1_score"] = m["tma1_score"].fillna(m.loc[tr, "tma1_score"].median())
lr_s = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=5000))
lr_s.fit(Xs.loc[tr], y[tr])
p_s_va = lr_s.predict_proba(Xs.loc[va])[:, 1]
p_s_te = lr_s.predict_proba(Xs.loc[te])[:, 1]
res_sens_te = metrics(y[te], p_s_te, threshold_for_recall(y[va], p_s_va, TARGET_RECALL))

q3 = pd.DataFrame([
    {"mo_hinh": f"{chosen_name} (chính, 28 ngày đầu)", "tap": "validation", **res_va},
    {"mo_hinh": f"{chosen_name} (chính, 28 ngày đầu)", "tap": "test (2014J)", **res_te},
    {"mo_hinh": f"{chosen_name} (chính, ngưỡng theo tỷ lệ cảnh báo)", "tap": "test (2014J)", **res_te_rank},
    {"mo_hinh": "Baseline: chỉ clicks_0_28", "tap": "test (2014J)", **res_base_te},
    {"mo_hinh": "Nhạy cảm: LR + tma1_score (không dùng để quyết định)", "tap": "test (2014J)", **res_sens_te},
])
q3.to_csv(HERE / "q3_hieu_suat_du_bao.csv", index=False)
print("\n=== Q3 ===")
print(q3.round(4).to_string())

# kiểm toán sai số theo nhóm (không dùng làm biến dự báo)
te_df = m.loc[te, K + ["nc", "label3"]].copy()
te_df["score"] = p_te
te_df["flag"] = te_df["score"] >= thr
te_df = te_df.merge(aud_ok[K + ["gender", "age_band", "disability", "imd_band"]], on=K, how="left",
                    validate="one_to_one")
audit_rows = []
for c in ["gender", "age_band", "disability", "imd_band"]:
    for val, g in te_df.groupby(c):
        auc = roc_auc_score(g.nc, g.score) if g.nc.nunique() == 2 else np.nan
        audit_rows.append({"thuoc_tinh": c, "nhom": val, "so_luot": len(g),
                           "ty_le_khong_hoan_thanh": round(g.nc.mean(), 3),
                           "ty_le_bi_canh_bao": round(g.flag.mean(), 3),
                           "recall": round((g.flag & (g.nc == 1)).sum() / max(g.nc.sum(), 1), 3),
                           "AUC": round(auc, 3)})
pd.DataFrame(audit_rows).to_csv(HERE / "q3_kiem_toan_theo_nhom_khong_dung_lam_bien.csv", index=False)

# ---------------------------------------------------------------- Q4
CAP = int(params["default_k"])
te_df["rank_trong_module_ky"] = te_df.groupby(["code_module", "code_presentation"])["score"].rank(
    ascending=False, method="first")
lst = te_df[te_df["rank_trong_module_ky"] <= CAP].copy()
lst = lst.sort_values(["code_module", "code_presentation", "rank_trong_module_ky"])
lst.to_csv(HERE / "q4_danh_sach_uu_tien_200_moi_module_ky.csv", index=False)

summ = []
for (mod, pres), g in te_df.groupby(["code_module", "code_presentation"]):
    top = g[g.rank_trong_module_ky <= CAP]
    summ.append({"module_ky": f"{mod}-{pres}", "so_sinh_vien": len(g), "so_khong_hoan_thanh": int(g.nc.sum()),
                 "so_trong_danh_sach": len(top), "so_khong_hoan_thanh_trong_danh_sach": int(top.nc.sum()),
                 "precision": round(top.nc.mean(), 3), "recall_trong_module_ky": round(top.nc.sum() / g.nc.sum(), 3),
                 "tran_toi_da_recall": round(min(CAP, g.nc.sum()) / g.nc.sum(), 3)})
q4 = pd.DataFrame(summ)
tot_hits = int(lst.nc.sum())
tot_nc = int(te_df.nc.sum())
q4.loc[len(q4)] = {"module_ky": "Tổng test", "so_sinh_vien": len(te_df), "so_khong_hoan_thanh": tot_nc,
                   "so_trong_danh_sach": len(lst), "so_khong_hoan_thanh_trong_danh_sach": tot_hits,
                   "precision": round(tot_hits / len(lst), 3), "recall_trong_module_ky": round(tot_hits / tot_nc, 3),
                   "tran_toi_da_recall": round(min(CAP * 2, tot_nc) / tot_nc, 3)}
q4.to_csv(HERE / "q4_tom_tat_trung_danh_sach.csv", index=False)

cap_rows = []
for k in [100, 200, 300]:
    top = te_df[te_df.rank_trong_module_ky <= k]
    cap_rows.append({"k_moi_module_ky": k, "so_trong_danh_sach": len(top), "trung": int(top.nc.sum()),
                     "recall_tong": round(top.nc.sum() / tot_nc, 3)})
pd.DataFrame(cap_rows).to_csv(HERE / "q4_do_nhay_suc_chua.csv", index=False)
print("\n=== Q4 ===")
print(q4.to_string())
print(pd.DataFrame(cap_rows).to_string())

# ---------------------------------------------------------------- Q5
# Giải thích bằng hồi quy logistic (hệ số x độ lệch chuẩn hóa) để có đóng góp theo từng sinh viên
lr_exp = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=5000))
lr_exp.fit(X.loc[tr], y[tr])
scaler = lr_exp.named_steps["standardscaler"]
coef = lr_exp.named_steps["logisticregression"].coef_[0]
median_all = m[FEATS].median()

LABEL = {
    "clicks_w1": "lượt truy cập tuần 1", "clicks_w2": "lượt truy cập tuần 2",
    "clicks_w3": "lượt truy cập tuần 3", "clicks_w4": "lượt truy cập tuần 4",
    "active_days_w1": "số ngày hoạt động tuần 1", "active_days_w2": "số ngày hoạt động tuần 2",
    "active_days_w3": "số ngày hoạt động tuần 3", "active_days_w4": "số ngày hoạt động tuần 4",
    "clicks_0_28": "tổng lượt truy cập 28 ngày đầu", "active_days_0_28": "số ngày hoạt động trong 28 ngày đầu",
    "n_sites_0_28": "số tài nguyên khác nhau đã mở trong 28 ngày đầu",
    "clicks_change_w1_w4": "mức thay đổi lượt truy cập từ tuần 1 đến tuần 4",
    "days_since_last_active_d28": "số ngày kể từ lần hoạt động gần nhất",
    "clicks_pre_start": "lượt truy cập trước khi khóa học bắt đầu",
    "active_days_pre_start": "số ngày hoạt động trước khi khóa học bắt đầu",
    "clicks_homepage_0_28": "lượt xem trang chủ", "clicks_oucontent_0_28": "lượt mở nội dung khóa học",
    "clicks_resource_0_28": "lượt mở tài liệu", "clicks_subpage_0_28": "lượt xem trang con",
    "clicks_forumng_0_28": "lượt truy cập diễn đàn", "clicks_quiz_0_28": "lượt làm trắc nghiệm",
    "clicks_url_0_28": "lượt mở liên kết", "tma1_days_before_deadline": "số ngày nộp TMA1 trước hạn",
    "num_of_prev_attempts": "số lần đã học lại", "studied_credits": "số tín chỉ đăng ký",
    "registration_lead_days": "số ngày đăng ký trước khi khóa bắt đầu",
    "days_observable_0_28": "số ngày quan sát được trong 28 ngày đầu",
}
BIN = {  # (văn bản khi = 1, văn bản khi = 0)
    "tma1_submitted_by_d28": ("đã nộp bài TMA1 trước ngày 28", "chưa nộp bài TMA1 trước ngày 28"),
    "tma1_on_time": ("nộp bài TMA1 đúng hạn", "không nộp bài TMA1 đúng hạn"),
    "no_vle_activity_0_28": ("không có hoạt động trên hệ thống học trực tuyến trong 28 ngày đầu",
                             "có hoạt động trên hệ thống học trực tuyến trong 28 ngày đầu"),
    "late_registration_1_28": ("đăng ký muộn sau ngày 0", "đăng ký đúng thời điểm"),
    "seen_in_earlier_presentation": ("đã từng học module này ở kỳ trước", "lần đầu học module này"),
}


def fmt(v):
    return str(int(v)) if float(v).is_integer() else f"{v:.1f}"


def phrase(f, v, med):
    if f in BIN:
        return BIN[f][0] if v == 1 else BIN[f][1]
    if f == "tma1_days_before_deadline":
        if v < 0:
            return f"nộp bài TMA1 muộn {fmt(-v)} ngày so với hạn"
        if v == 0 and med == 0:
            return "chưa nộp bài TMA1 trước ngày 28"
    rel = "thấp hơn" if v < med else ("cao hơn" if v > med else "bằng")
    return f"{LABEL.get(f, f)} là {fmt(v)} ({rel} mức trung vị {fmt(med)} của cả nhóm)"


lst_idx = te_df.loc[te_df.rank_trong_module_ky <= CAP].index
Z = scaler.transform(X.loc[lst_idx, FEATS])
contrib = pd.DataFrame(Z * coef, index=lst_idx, columns=FEATS)
expl_rows = []
for idx in lst_idx:
    row = m.loc[idx]
    c = contrib.loc[idx].sort_values(ascending=False)
    top = [f for f in c.index[:3] if c[f] > 0]
    phr = [phrase(f, row[f], median_all[f]) for f in top]
    prob = te_df.loc[idx, "score"]
    s1 = (f"Sinh viên {row['id_student']} ({row['code_module']} {row['code_presentation']}) được ưu tiên "
          f"vì xác suất không hoàn thành ước tính khoảng {prob:.0%}, các dấu hiệu chính là: "
          + "; ".join(phr) + ".")
    s2 = ("Đây là tương quan trong dữ liệu, không phải nguyên nhân đã được chứng minh, "
          "nên cố vấn nên trao đổi sớm để hiểu hoàn cảnh cụ thể của sinh viên.")
    expl_rows.append({"code_module": row["code_module"], "code_presentation": row["code_presentation"],
                      "id_student": row["id_student"], "rank_trong_module_ky": int(te_df.loc[idx, "rank_trong_module_ky"]),
                      "xac_suat_uoc_tinh": round(prob, 4),
                      "dac_trung_1": top[0] if len(top) > 0 else "", "dac_trung_2": top[1] if len(top) > 1 else "",
                      "dac_trung_3": top[2] if len(top) > 2 else "", "giai_thich_cho_co_van": s1 + " " + s2})
q5 = pd.DataFrame(expl_rows)
q5.to_csv(HERE / "q5_giai_thich_cho_co_van.csv", index=False)
top1 = q5.dac_trung_1.value_counts()
top_any = pd.concat([q5.dac_trung_1, q5.dac_trung_2, q5.dac_trung_3]).value_counts()
pd.DataFrame({"dac_trung": top_any.index, "so_lan_trong_top3": top_any.values,
              "so_lan_la_dong_gop_so_1": top1.reindex(top_any.index).fillna(0).astype(int).values}).to_csv(
    HERE / "q5_tan_suat_dac_trung_trong_danh_sach.csv", index=False)
print("\n=== Q5 ===")
print(pd.DataFrame({"so_lan_top3": top_any, "so_lan_dong_gop_1": top1.reindex(top_any.index).fillna(0)}).to_string())
print(q5.giai_thich_cho_co_van.iloc[0])

# ---------------------------------------------------------------- charts
plt.rcParams.update({"font.size": 10})
# Biểu đồ 1: Q1
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
for g, color in zip(GROUPS, ["#2a9d8f", "#e9c46a", "#e76f51"]):
    s = m[m.label3 == g]
    axes[0].plot(range(1, 5), [s[c].median() for c in WEEK_CLICKS], marker="o", label=g, color=color)
    axes[1].plot(range(1, 5), [s[c].median() for c in WEEK_ACTIVE], marker="o", label=g, color=color)
axes[0].set_title("Pass có nhiều lượt truy cập hơn Withdrawn và Fail ở cả 4 tuần; Fail thấp nhất")
axes[1].set_title("Số ngày hoạt động theo tuần: Pass cao nhất, Fail thấp nhất")
for ax in axes:
    ax.set_xlabel("Tuần (1-4)")
    ax.set_xticks(range(1, 5))
    ax.legend()
axes[0].set_ylabel("Lượt truy cập (trung vị)")
axes[1].set_ylabel("Số ngày hoạt động (trung vị)")
fig.tight_layout()
fig.savefig(HERE / "bieu_do_1_tuong_tac_4_tuan.png", dpi=150)
plt.close(fig)

# Biểu đồ 2: Q2 - AUC theo tuần
fig, ax = plt.subplots(figsize=(7, 4))
for meas, color, label in [("luot_truy_cap", "#264653", "Lượt truy cập"), ("so_ngay_hoat_dong", "#e76f51", "Số ngày hoạt động")]:
    sub = qt[qt.chi_bao == meas]
    ax.plot(sub.tuan, sub.auc_khong_hoan_thanh_cao_hon, marker="o", color=color, label=label)
    sig = sub[sub.co_y_nghia_holm_0_05]
    ax.scatter(sig.tuan, sig.auc_khong_hoan_thanh_cao_hon, s=140, facecolors="none", edgecolors=color)
ax.axhline(0.5, color="grey", ls="--", lw=1)
ax.set_xticks([1, 2, 3, 4])
ax.set_xlabel("Tuần (1-4)")
ax.set_ylabel("AUC (không hoàn thành có giá trị cao hơn)")
ax.set_title("Khác biệt hoàn thành vs không hoàn thành đã có ý nghĩa ngay từ tuần 1 và kéo dài đến tuần 4")
ax.legend()
fig.tight_layout()
fig.savefig(HERE / "bieu_do_2_khac_biet_theo_tuan.png", dpi=150)
plt.close(fig)

# Biểu đồ 3: Q3 - ROC trên test
fig, ax = plt.subplots(figsize=(5.5, 5))
for p, lab in [(p_te, f"{chosen_name} (chính)"), (p_s_te, "LR + tma1_score (nhạy cảm)"), (p_base_te, "Baseline: clicks_0_28")]:
    fpr, tpr, _ = roc_curve(y[te], p)
    ax.plot(fpr, tpr, label=f"{lab}, AUC={roc_auc_score(y[te], p):.3f}")
ax.plot([0, 1], [0, 1], color="grey", ls="--", lw=1)
ax.set_xlabel("Tỷ lệ cảnh báo nhầm (FPR)")
ax.set_ylabel("Tỷ lệ bắt được (TPR)")
ax.set_title("Mô hình dùng dữ liệu 28 ngày đầu phân biệt tốt hơn baseline trên tập test")
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig(HERE / "bieu_do_3_roc_test.png", dpi=150)
plt.close(fig)

# Biểu đồ 4: Q4 - số trúng theo module-kỳ
q4_plot = q4[q4.module_ky != "Tổng test"]
fig, ax = plt.subplots(figsize=(7, 4))
x = np.arange(len(q4_plot))
ax.bar(x, q4_plot["so_trong_danh_sach"], color="#cfd8dc", label="Số sinh viên trong danh sách")
ax.bar(x, q4_plot["so_khong_hoan_thanh_trong_danh_sach"], color="#264653", label="Trong đó không hoàn thành")
ax.set_xticks(x)
ax.set_xticklabels(q4_plot.module_ky)
ax.set_ylabel("Số sinh viên")
ax.set_title("80% danh sách ưu tiên không hoàn thành, nhưng 200/module-kỳ chỉ bắt được 23% tổng số")
ax.legend()
fig.tight_layout()
fig.savefig(HERE / "bieu_do_4_trung_danh_sach.png", dpi=150)
plt.close(fig)

summary = {
    "mo_hinh_chon": chosen_name, "auc_val_lr": round(auc_lr_va, 4), "auc_val_hgb": round(auc_hgb_va, 4),
    "nguong_xac_suat": round(float(thr), 4),
    "test": {k: (round(float(v), 4) if isinstance(v, (float, np.floating)) else v) for k, v in res_te.items()},
    "first_week_clicks": first_week["luot_truy_cap"], "first_week_active": first_week["so_ngay_hoat_dong"],
}
(HERE / "tom_tat_ket_qua.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print("\nTÓM TẮT:", json.dumps(summary, ensure_ascii=False, indent=2))
