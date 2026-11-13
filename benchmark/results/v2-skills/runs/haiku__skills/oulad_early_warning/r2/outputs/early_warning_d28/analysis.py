"""Cảnh báo sớm OULAD (BBB, FFF; 2013B-2014J) - mốc quyết định cuối ngày 28.

Chạy từ bất kỳ thư mục nào:  python outputs/early_warning_d28/analysis.py
Đầu vào: data/ (chỉ đọc). Đầu ra: outputs/early_warning_d28/.

Quy ước:
- Quần thể: các đăng ký còn theo học đến cuối ngày 28 (aq3_model_table, 13.020 dòng).
- Nhãn không hoàn thành = Fail hoặc Withdrawn (target_noncompletion = 1).
- Chia train / validation / test theo cột `split` có sẵn của dữ liệu (theo kỳ). Chọn mô hình và
  ngưỡng trên validation; test chỉ dùng một lần để báo cáo.
- Thuộc tính nhạy cảm (giới tính, độ tuổi, khuyết tật, IMD, vùng) KHÔNG là biến dự báo; chỉ dùng để
  kiểm tra sai số theo nhóm.
- tma1_score không có ngày công bố trong dữ liệu -> chỉ đưa vào phân tích độ nhạy.
"""
import json
import textwrap
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, confusion_matrix, precision_recall_curve, roc_auc_score
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / "data"
K = ["code_module", "code_presentation", "id_student"]
OUT_GROUPS = ["Pass", "Fail", "Withdrawn"]
TARGET_RECALL = 0.70
RNG = np.random.default_rng(0)

PARAMS = json.loads((DATA / "aq4_decision_params.json").read_text(encoding="utf-8"))
CAP_DEFAULT = int(PARAMS["default_k"])
CAPS = [int(x) for x in PARAMS["capacity_k_per_module_presentation"]]

# ----------------------------------------------------------------------------- nạp dữ liệu
aq1 = pd.read_csv(DATA / "aq1_student_week.csv")
m = pd.read_csv(DATA / "aq3_model_table.csv")
aud = pd.read_csv(DATA / "aq3_audit_attributes.csv")

lab = aq1.groupby(K)["label3"].agg(["first", "nunique"]).reset_index()
assert (lab["nunique"] == 1).all(), "label3 không nhất quán trong một học viên"
lab = lab.rename(columns={"first": "label3"})[K + ["label3"]]
df = m.merge(lab, on=K, how="left").merge(
    aud[K + ["gender", "age_band", "disability", "imd_band", "region"]], on=K, how="left"
)
assert len(df) == len(m)
assert ((df["label3"] == "Pass") == (df["target_noncompletion"] == 0)).all()
df["target"] = df["target_noncompletion"].astype(int)
print("Quần thể:", len(df), "| tỷ lệ không hoàn thành:", round(df.target.mean(), 4))
print(df.groupby("split").target.agg(["size", "mean"]).round(4))

# ----------------------------------------------------------------------------- tiện ích
def holm(p):
    p = np.asarray(p, dtype=float)
    order = np.argsort(p)
    adj = np.empty_like(p)
    running = 0.0
    m_ = len(p)
    for rank, i in enumerate(order):
        running = max(running, (m_ - rank) * p[i])
        adj[i] = min(running, 1.0)
    return adj


def rank_biserial(x1, x2, u1):
    """Dương = nhóm x1 có giá trị lớn hơn nhóm x2."""
    return 2 * u1 / (len(x1) * len(x2)) - 1


# ----------------------------------------------------------------------------- Câu 1: tương tác 4 tuần đầu theo nhóm kết quả
wk = (
    aq1.groupby(["label3", "week"])
    .agg(
        so_sv=("id_student", "size"),
        trung_vi_luot_truy_cap=("clicks", "median"),
        trung_binh_luot_truy_cap=("clicks", "mean"),
        trung_vi_so_ngay_truy_cap=("active_days", "median"),
        trung_binh_so_ngay_truy_cap=("active_days", "mean"),
        ty_le_0_ngay_truy_cap=("active_days", lambda s: (s == 0).mean()),
    )
    .reset_index()
)
wk.to_csv(HERE / "q1_weekly_by_outcome.csv", index=False)

q1_tests = []
for wkk in sorted(aq1.week.unique()):
    sub = aq1[aq1.week == wkk]
    for metric in ["clicks", "active_days"]:
        g = [sub.loc[sub.label3 == o, metric].values for o in OUT_GROUPS]
        kw = stats.kruskal(*g)
        for a, b in [("Pass", "Fail"), ("Pass", "Withdrawn"), ("Fail", "Withdrawn")]:
            xa = sub.loc[sub.label3 == a, metric].values
            xb = sub.loc[sub.label3 == b, metric].values
            mw = stats.mannwhitneyu(xa, xb, alternative="two-sided")
            q1_tests.append(dict(tuan=wkk, chi_so=metric, nhom_a=a, nhom_b=b,
                                 kruskal_p=kw.pvalue, mw_p=mw.pvalue,
                                 cliff_like_effect=rank_biserial(xa, xb, mw.statistic)))
q1t = pd.DataFrame(q1_tests)
q1t["mw_p_holm"] = holm(q1t.mw_p.values)
q1t.to_csv(HERE / "q1_pairwise_tests.csv", index=False)

tot = aq1.groupby(["label3", "id_student"]).agg(clicks_4tuan=("clicks", "sum"), ngay_truy_cap=("active_days", "sum")).reset_index()
q1_tot = tot.groupby("label3").agg(
    so_sv=("id_student", "size"),
    trung_vi_clicks_4tuan=("clicks_4tuan", "median"),
    trung_vi_ngay_truy_cap_4tuan=("ngay_truy_cap", "median"),
).reindex(OUT_GROUPS)
q1_tot.to_csv(HERE / "q1_totals_by_outcome.csv")
print("\n=== Câu 1: theo tuần ===")
print(wk.round(2).to_string(index=False))
print(q1t.round(4).to_string(index=False))
print(q1_tot.round(1))

# ----------------------------------------------------------------------------- Câu 2: chỉ báo phân biệt hoàn thành (Pass) và không hoàn thành (Fail+Withdrawn)
# Tính luỹ kế theo tuần từ aq1 (chỉ dữ liệu đến ngày 28).
cw = aq1.pivot_table(index=K, columns="week", values="clicks").sort_index(axis=1)
ca = aq1.pivot_table(index=K, columns="week", values="active_days").sort_index(axis=1)
cum = pd.DataFrame(index=cw.index)
for wkk in cw.columns:
    cum[f"cum_clicks_den_tuan{wkk}"] = cw.loc[:, cw.columns <= wkk].sum(axis=1)
    cum[f"cum_ngay_truy_cap_den_tuan{wkk}"] = ca.loc[:, ca.columns <= wkk].sum(axis=1)
cum = cum.reset_index()
d2 = df.merge(cum, on=K, how="left")
d2["nhom"] = np.where(d2.target == 1, "Không hoàn thành (Fail+Withdrawn)", "Hoàn thành (Pass)")
comp = d2[d2.target == 0]
noncomp = d2[d2.target == 1]

NUM_IND = {
    "clicks_w1": "Lượt truy cập tuần 1", "clicks_w2": "Lượt truy cập tuần 2",
    "clicks_w3": "Lượt truy cập tuần 3", "clicks_w4": "Lượt truy cập tuần 4",
    "active_days_w1": "Số ngày truy cập tuần 1", "active_days_w2": "Số ngày truy cập tuần 2",
    "active_days_w3": "Số ngày truy cập tuần 3", "active_days_w4": "Số ngày truy cập tuần 4",
    "log_clicks_0_28": "Tổng lượt truy cập 0–28 (log)",
    "active_days_0_28": "Số ngày có truy cập 0–28",
    "n_sites_0_28": "Số loại trang/tài liệu đã mở 0–28",
    "days_since_last_active_d28": "Số ngày kể từ lần truy cập cuối (tính đến ngày 28)",
    "clicks_pre_start": "Lượt truy cập trước khai giảng",
    "active_days_pre_start": "Số ngày truy cập trước khai giảng",
    "clicks_quiz_0_28": "Lượt làm bài trắc nghiệm 0–28",
    "clicks_forumng_0_28": "Lượt tham gia diễn đàn 0–28",
    "clicks_oucontent_0_28": "Lượt mở nội dung bài học 0–28",
    "clicks_resource_0_28": "Lượt mở tài liệu học 0–28",
    "clicks_homepage_0_28": "Lượt vào trang chủ khóa học 0–28",
    "tma1_days_before_deadline": "Nộp TMA1 sớm trước hạn (số ngày; chỉ SV đã nộp)",
    "tma1_score": "Điểm TMA1 (chỉ SV đã nộp; ngày công bố điểm không rõ)",
    "studied_credits": "Số tín chỉ đăng ký",
    "registration_lead_days": "Số ngày đăng ký trước khai giảng",
    "num_of_prev_attempts": "Số lần đã học trước đây",
    "seen_in_earlier_presentation": "Đã từng học module trước",
    "cum_clicks_den_tuan1": "Tổng lượt truy cập đến hết tuần 1",
    "cum_clicks_den_tuan2": "Tổng lượt truy cập đến hết tuần 2",
    "cum_clicks_den_tuan3": "Tổng lượt truy cập đến hết tuần 3",
    "cum_clicks_den_tuan4": "Tổng lượt truy cập đến hết tuần 4",
    "cum_ngay_truy_cap_den_tuan1": "Tổng ngày truy cập đến hết tuần 1",
    "cum_ngay_truy_cap_den_tuan2": "Tổng ngày truy cập đến hết tuần 2",
    "cum_ngay_truy_cap_den_tuan3": "Tổng ngày truy cập đến hết tuần 3",
    "cum_ngay_truy_cap_den_tuan4": "Tổng ngày truy cập đến hết tuần 4",
}
BIN_IND = {
    "tma1_submitted_by_d28": "Đã nộp TMA1 đến ngày 28",
    "tma1_on_time": "TMA1 nộp đúng hạn (0 nếu chưa nộp)",
    "no_vle_activity_0_28": "Không có hoạt động trên hệ thống học trực tuyến 0–28",
}
rows = []
for col, lbl in NUM_IND.items():
    x1 = comp[col].dropna().values
    x2 = noncomp[col].dropna().values
    mw = stats.mannwhitneyu(x1, x2, alternative="two-sided")
    rows.append(dict(chi_so=col, mo_ta=lbl, loai="liên tục", n_hoan_thanh=len(x1), n_khong_hoan_thanh=len(x2),
                     trung_vi_hoan_thanh=np.median(x1), trung_vi_khong_hoan_thanh=np.median(x2),
                     hieu_ung=rank_biserial(x1, x2, mw.statistic), p_value=mw.pvalue))
for col, lbl in BIN_IND.items():
    ct = pd.crosstab(d2[col], d2.target)
    chi2, p, _, _ = stats.chi2_contingency(ct)
    p_c = comp[col].mean()
    p_n = noncomp[col].mean()
    rows.append(dict(chi_so=col, mo_ta=lbl, loai="nhị phân (tỷ lệ = 1)", n_hoan_thanh=len(comp), n_khong_hoan_thanh=len(noncomp),
                     trung_vi_hoan_thanh=p_c, trung_vi_khong_hoan_thanh=p_n,
                     hieu_ung=p_c - p_n, p_value=p))
q2 = pd.DataFrame(rows)
q2["p_holm"] = holm(q2.p_value.values)
q2["co_y_nghia_holm_0_05"] = q2.p_holm < 0.05
q2 = q2.sort_values("hieu_ung", key=lambda s: s.abs(), ascending=False)
q2.to_csv(HERE / "q2_indicator_tests.csv", index=False)

# Từ tuần nào khác biệt xuất hiện: với từng họ chỉ báo theo tuần, tuần đầu tiên có p (Holm) < 0.05
fam = {
    "Lượt truy cập theo tuần": [f"clicks_w{k}" for k in range(1, 5)],
    "Ngày truy cập theo tuần": [f"active_days_w{k}" for k in range(1, 5)],
    "Tổng lượt truy cập luỹ kế": [f"cum_clicks_den_tuan{k}" for k in range(1, 5)],
    "Tổng ngày truy cập luỹ kế": [f"cum_ngay_truy_cap_den_tuan{k}" for k in range(1, 5)],
}
wk_rows = []
for fam_name, cols in fam.items():
    sub = q2[q2.chi_so.isin(cols)].copy()
    sub["tuan"] = sub.chi_so.str.extract(r"(\d)$")[0].astype(int)
    sub = sub.sort_values("tuan")
    sub["p_holm_ho"] = holm(sub.p_value.values)
    first = sub.loc[sub.p_holm_ho < 0.05, "tuan"]
    wk_rows.append(dict(ho_chi_so=fam_name,
                        tuan_dau_tien_co_y_nghia=int(first.min()) if len(first) else None,
                        hieu_ung_theo_tuan=" | ".join(f"T{t}:{e:+.3f}" for t, e in zip(sub.tuan, sub.hieu_ung)),
                        p_holm_theo_tuan=" | ".join(f"T{t}:{p:.2g}" for t, p in zip(sub.tuan, sub.p_holm_ho))))
q2w = pd.DataFrame(wk_rows)
q2w.to_csv(HERE / "q2_first_week_significant.csv", index=False)
print("\n=== Câu 2 ===")
print(q2[["chi_so", "trung_vi_hoan_thanh", "trung_vi_khong_hoan_thanh", "hieu_ung", "p_holm", "co_y_nghia_holm_0_05"]].round(4).to_string(index=False))
print(q2w.to_string(index=False))

# ----------------------------------------------------------------------------- Câu 3: mô hình dự báo chỉ dùng dữ liệu đến ngày 28
MAIN_FEATS = [
    "clicks_w1", "clicks_w2", "clicks_w3", "clicks_w4",
    "active_days_w1", "active_days_w2", "active_days_w3", "active_days_w4",
    "log_clicks_0_28", "active_days_0_28", "n_sites_0_28", "clicks_change_w1_w4",
    "days_since_last_active_d28", "clicks_pre_start", "active_days_pre_start", "no_vle_activity_0_28",
    "clicks_homepage_0_28", "clicks_oucontent_0_28", "clicks_resource_0_28", "clicks_subpage_0_28",
    "clicks_forumng_0_28", "clicks_quiz_0_28", "clicks_url_0_28",
    "tma1_submitted_by_d28", "tma1_on_time", "tma1_days_before_deadline",
    "num_of_prev_attempts", "studied_credits", "registration_lead_days",
    "seen_in_earlier_presentation", "late_registration_1_28",
]
RAW_CLICK_COLS = {"clicks_w1", "clicks_w2", "clicks_w3", "clicks_w4", "clicks_pre_start", "clicks_homepage_0_28",
                  "clicks_oucontent_0_28", "clicks_resource_0_28", "clicks_subpage_0_28", "clicks_forumng_0_28",
                  "clicks_quiz_0_28", "clicks_url_0_28"}
TMA_FEATS = ["tma1_submitted_by_d28", "tma1_on_time", "tma1_days_before_deadline"]


def build_X(d, feats):
    X = d[feats].astype(float).copy()
    for c in feats:
        if c in RAW_CLICK_COLS:
            X[c] = np.log1p(X[c])
    if "tma1_days_before_deadline" in X:
        X["tma1_days_before_deadline"] = X["tma1_days_before_deadline"].fillna(0)
    if "tma1_score" in X:
        X["tma1_score_thieu"] = X["tma1_score"].isna().astype(float)
        X["tma1_score"] = X["tma1_score"].fillna(0)
    return X


tr = df[df.split == "train"].reset_index(drop=True)
va = df[df.split == "validation"].reset_index(drop=True)
te = df[df.split == "test"].reset_index(drop=True)


def fit_models(feats):
    Xtr, Xva = build_X(tr, feats), build_X(va, feats)
    sc = StandardScaler().fit(Xtr)
    lr = LogisticRegression(C=1.0, max_iter=5000).fit(sc.transform(Xtr), tr.target)
    hgb = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_leaf_nodes=15,
                                         min_samples_leaf=40, l2_regularization=1.0, random_state=0).fit(Xtr, tr.target)
    return sc, lr, hgb


def score(model_name, sc, lr, hgb, d, feats):
    X = build_X(d, feats)
    if model_name == "logistic":
        return lr.predict_proba(sc.transform(X))[:, 1]
    return hgb.predict_proba(X)[:, 1]


def pick_threshold(y, p):
    """Ngưỡng cao nhất đạt recall >= mục tiêu (chọn precision tốt nhất trong các ngưỡng đó)."""
    prec, rec, thr = precision_recall_curve(y, p)
    ok = np.where(rec[:-1] >= TARGET_RECALL)[0]
    best = ok[np.argmax(prec[ok])]
    return thr[best]


def metrics(y, p, thr):
    yhat = (p >= thr).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, yhat, labels=[0, 1]).ravel()
    return dict(auc=roc_auc_score(y, p), average_precision=average_precision_score(y, p),
                nguong=thr, recall=tp / (tp + fn), precision=tp / (tp + fp) if tp + fp else np.nan,
                ty_le_bi_gan_co=yhat.mean(), tp=tp, fp=fp, fn=fn, tn=tn)


# So sánh mô hình trên validation
sc, lr, hgb = fit_models(MAIN_FEATS)
p_va_lr = score("logistic", sc, lr, hgb, va, MAIN_FEATS)
p_va_hgb = score("boosting", sc, lr, hgb, va, MAIN_FEATS)
auc_lr = roc_auc_score(va.target, p_va_lr)
auc_hgb = roc_auc_score(va.target, p_va_hgb)
chosen = "boosting" if (auc_hgb - auc_lr) > 0.01 else "logistic"
print(f"\nValidation AUC: logistic={auc_lr:.4f}, boosting={auc_hgb:.4f} -> chọn: {chosen}")

# Đường cơ sở: chỉ tổng lượt truy cập 0–28 (logistic)
base_feats = ["log_clicks_0_28"]
sc_b, lr_b, hgb_b = fit_models(base_feats)
# Độ nhạy
sens_sets = {
    "chính: 32 đặc trưng đến ngày 28": MAIN_FEATS,
    "bỏ nhóm TMA1": [f for f in MAIN_FEATS if f not in TMA_FEATS],
    "thêm điểm TMA1 (độ nhạy)": MAIN_FEATS + ["tma1_score"],
    "đường cơ sở: chỉ tổng lượt truy cập 0–28": base_feats,
}
sens_rows = []
threshold_store = {}
for name, feats in sens_sets.items():
    for mname in ["logistic", "boosting"]:
        sc_s, lr_s, hgb_s = fit_models(feats)
        pv = score(mname, sc_s, lr_s, hgb_s, va, feats)
        pt = score(mname, sc_s, lr_s, hgb_s, te, feats)
        thr = pick_threshold(va.target.values, pv)
        mt = metrics(te.target.values, pt, thr)
        mv = metrics(va.target.values, pv, thr)
        sens_rows.append(dict(bo_dac_trung=name, mo_hinh=mname, auc_validation=mv["auc"], auc_test=mt["auc"],
                              nguong_tu_validation=thr, recall_test=mt["recall"], precision_test=mt["precision"],
                              ty_le_bi_gan_co_test=mt["ty_le_bi_gan_co"], dat_muc_tieu_70=mt["recall"] >= TARGET_RECALL))
        if name.startswith("chính") and mname == chosen:
            threshold_store["main"] = (thr, pt, pv, mt, mv)
sens = pd.DataFrame(sens_rows)
sens.to_csv(HERE / "q3_sensitivity_models.csv", index=False)
print(sens.round(4).to_string(index=False))

# Kết quả chính trên test (dùng một lần)
thr, p_te, p_va, mt, mv = threshold_store["main"]
p_te_main = p_te
p_va_main = p_va
mt_df = pd.DataFrame([dict(tap="validation", **mv), dict(tap="test", **mt)])
mt_df.to_csv(HERE / "q3_main_metrics.csv", index=False)

# Khoảng tin cậy bootstrap cho recall trên test
yte = te.target.values
boot = []
for _ in range(1000):
    idx = RNG.integers(0, len(yte), len(yte))
    yb, pb = yte[idx], p_te_main[idx]
    if yb.sum() == 0:
        continue
    boot.append(((pb >= thr) & (yb == 1)).sum() / yb.sum())
ci_lo, ci_hi = np.percentile(boot, [2.5, 97.5])
print(f"\nTest: AUC={mt['auc']:.3f}, recall={mt['recall']:.3f} (95% CI {ci_lo:.3f}-{ci_hi:.3f}), "
      f"precision={mt['precision']:.3f}, tỷ lệ gắn cờ={mt['ty_le_bi_gan_co']:.3f}, ngưỡng={thr:.4f}")

# Kiểm tra theo nhóm (chỉ để audit, không dùng làm biến)
te_aud = te.assign(p=p_te_main, flag=(p_te_main >= thr).astype(int))
audit_rows = []
for col in ["gender", "age_band", "disability", "imd_band"]:
    for g, sub in te_aud.groupby(col):
        pos = sub[sub.target == 1]
        audit_rows.append(dict(nhom_kiem_tra=col, gia_tri=g, so_sv=len(sub),
                               ty_le_khong_hoan_thanh=sub.target.mean(),
                               ty_le_duoc_gan_co=sub.flag.mean(),
                               recall_nhom=(pos.flag.mean() if len(pos) else np.nan)))
pd.DataFrame(audit_rows).to_csv(HERE / "q3_audit_by_group_test.csv", index=False)

# Chọn mô hình dùng cho danh sách ưu tiên và giải thích
scorer_name = chosen
exp_sc, exp_lr, _ = sc, lr, hgb  # giải thích luôn dựa trên hồi quy logistic (đường tuyến tính)

# ----------------------------------------------------------------------------- Câu 4: danh sách ưu tiên theo sức chứa
te_aud = te.copy()
te_aud["diem_rui_ro"] = p_te_main
va_aud = va.copy()
va_aud["diem_rui_ro"] = p_va_main


def capacity_list(d, k):
    out = []
    for (mod, pres), g in d.groupby(["code_module", "code_presentation"]):
        top = g.sort_values(["diem_rui_ro", "id_student"], ascending=[False, True]).head(k)
        out.append(top.assign(hang_trong_module_ky=range(1, len(top) + 1)))
    return pd.concat(out)


def baseline_list(d, k):
    out = []
    for (mod, pres), g in d.groupby(["code_module", "code_presentation"]):
        top = g.sort_values(["clicks_0_28", "id_student"], ascending=[True, True]).head(k)
        out.append(top)
    return pd.concat(out)


cap_rows = []
for tap_name, d in [("validation", va_aud), ("test", te_aud)]:
    for k in sorted(set(CAPS + [CAP_DEFAULT])):
        for rule, lister in [("mô hình rủi ro", capacity_list), ("ít lượt truy cập nhất 0–28 (đối chứng)", baseline_list)]:
            L = lister(d, k)
            for (mod, pres), g in d.groupby(["code_module", "code_presentation"]):
                sel = L[(L.code_module == mod) & (L.code_presentation == pres)]
                hits = int(sel.target.sum())
                total_nc = int(g.target.sum())
                cap_rows.append(dict(tap=tap_name, quy_tac=rule, module_ky=f"{mod} {pres}", k=k,
                                     so_sv_trong_module_ky=len(g), so_sv_duoc_lien_he=len(sel),
                                     so_trung_khong_hoan_thanh=hits, ty_le_trung=hits / len(sel) if len(sel) else np.nan,
                                     tong_khong_hoan_thanh=total_nc, ty_le_bat_duoc=hits / total_nc if total_nc else np.nan))
cap = pd.DataFrame(cap_rows)
cap.to_csv(HERE / "q4_capacity_summary.csv", index=False)
print("\n=== Câu 4 (test, k=200 mặc định) ===")
print(cap[(cap.tap == "test") & (cap.k == CAP_DEFAULT)].round(3).to_string(index=False))

# Danh sách ưu tiên chính trên test (k mặc định) kèm giải thích
pri = capacity_list(te_aud, CAP_DEFAULT)
Xpri = build_X(pri, MAIN_FEATS)
z = exp_sc.transform(Xpri)
coef = exp_lr.coef_[0]
contrib = z * coef  # đóng góp vào log-odds so với học viên trung bình (quần thể train)

PH = {
    "clicks_w1": ("lượt truy cập tuần 1 thấp", "lượt truy cập tuần 1 cao"),
    "clicks_w2": ("lượt truy cập tuần 2 thấp", "lượt truy cập tuần 2 cao"),
    "clicks_w3": ("lượt truy cập tuần 3 thấp", "lượt truy cập tuần 3 cao"),
    "clicks_w4": ("lượt truy cập tuần 4 thấp", "lượt truy cập tuần 4 cao"),
    "active_days_w1": ("số ngày truy cập tuần 1 thấp", "số ngày truy cập tuần 1 cao"),
    "active_days_w2": ("số ngày truy cập tuần 2 thấp", "số ngày truy cập tuần 2 cao"),
    "active_days_w3": ("số ngày truy cập tuần 3 thấp", "số ngày truy cập tuần 3 cao"),
    "active_days_w4": ("số ngày truy cập tuần 4 thấp", "số ngày truy cập tuần 4 cao"),
    "log_clicks_0_28": ("tổng lượt truy cập 28 ngày đầu thấp", "tổng lượt truy cập 28 ngày đầu cao"),
    "active_days_0_28": ("ít ngày có truy cập trong 28 ngày đầu", "nhiều ngày có truy cập trong 28 ngày đầu"),
    "n_sites_0_28": ("ít loại tài liệu được mở trong 28 ngày đầu", "nhiều loại tài liệu được mở trong 28 ngày đầu"),
    "clicks_change_w1_w4": ("lượt truy cập giảm dần từ tuần 1 đến tuần 4", "lượt truy cập tăng dần từ tuần 1 đến tuần 4"),
    "days_since_last_active_d28": ("đã lâu không truy cập tính đến ngày 28", "vừa truy cập gần ngày 28"),
    "clicks_pre_start": ("ít truy cập hệ thống trước khi khai giảng", "nhiều truy cập hệ thống trước khi khai giảng"),
    "active_days_pre_start": ("ít ngày truy cập trước khi khai giảng", "nhiều ngày truy cập trước khi khai giảng"),
    "no_vle_activity_0_28": ("vẫn có hoạt động trên hệ thống học trực tuyến", "không có hoạt động nào trên hệ thống học trực tuyến trong 28 ngày đầu"),
    "clicks_homepage_0_28": ("ít vào trang chủ khóa học", "nhiều vào trang chủ khóa học"),
    "clicks_oucontent_0_28": ("ít mở nội dung bài học", "nhiều mở nội dung bài học"),
    "clicks_resource_0_28": ("ít mở tài liệu học", "nhiều mở tài liệu học"),
    "clicks_subpage_0_28": ("ít mở các trang con của khóa học", "nhiều mở các trang con của khóa học"),
    "clicks_forumng_0_28": ("ít tham gia diễn đàn thảo luận", "nhiều tham gia diễn đàn thảo luận"),
    "clicks_quiz_0_28": ("ít làm bài trắc nghiệm", "nhiều làm bài trắc nghiệm"),
    "clicks_url_0_28": ("ít mở liên kết học liệu", "nhiều mở liên kết học liệu"),
    "tma1_submitted_by_d28": ("chưa nộp bài TMA1 đến ngày 28", "đã nộp bài TMA1 đến ngày 28"),
    "tma1_on_time": ("bài TMA1 nộp trễ hạn hoặc chưa nộp", "bài TMA1 nộp đúng hạn"),
    "tma1_days_before_deadline": ("nộp bài TMA1 sát hạn hoặc chưa nộp", "nộp bài TMA1 sớm trước hạn"),
    "num_of_prev_attempts": ("ít lần học lại trước đây", "đã học lại nhiều lần trước đây"),
    "studied_credits": ("khối lượng tín chỉ đăng ký thấp", "khối lượng tín chỉ đăng ký cao"),
    "registration_lead_days": ("đăng ký sát ngày khai giảng", "đăng ký sớm trước khai giảng"),
    "seen_in_earlier_presentation": ("chưa từng học module này trước đây", "đã từng học module này trước đây"),
    "late_registration_1_28": ("đăng ký trước ngày 1", "đăng ký sau ngày 1"),
}
CAT = {
    "tma": {"tma1_submitted_by_d28", "tma1_on_time", "tma1_days_before_deadline"},
    "profile": {"num_of_prev_attempts", "studied_credits", "registration_lead_days",
                "seen_in_earlier_presentation", "late_registration_1_28"},
}
ACTION = {
    "tma": "Nên nhắc lịch nộp bài TMA và hỗ trợ kế hoạch cho bài tiếp theo.",
    "profile": "Nên trò chuyện về khối lượng học, kinh nghiệm học trước đây và kế hoạch học tập phù hợp.",
    "vle": "Nên trao đổi sớm để tìm hiểu khó khăn khi học trên hệ thống và hướng dẫn cách vào học liệu.",
}
FEAT_ORDER = MAIN_FEATS


def describe(i):
    c = contrib[i]
    order = np.argsort(-c)
    top, n_tma = [], 0
    for j in order:  # tối đa 1 ý về TMA1 để câu không lặp
        if c[j] <= 0:
            break
        if FEAT_ORDER[j] in CAT["tma"]:
            if n_tma >= 1:
                continue
            n_tma += 1
        top.append(j)
        if len(top) == 3:
            break
    names = [FEAT_ORDER[j] for j in top]
    phr = []
    for j in top:
        f = FEAT_ORDER[j]
        lo, hi = PH[f]
        phr.append(hi if z[i, j] > 0 else lo)
    if not phr:
        return "", "", "", ""
    if len(phr) == 1:
        s1 = f"Sinh viên này được xếp ưu tiên chủ yếu vì {phr[0]}."
    elif len(phr) == 2:
        s1 = f"Sinh viên này được xếp ưu tiên chủ yếu vì {phr[0]} và {phr[1]}."
    else:
        s1 = f"Sinh viên này được xếp ưu tiên chủ yếu vì {phr[0]}, {phr[1]} và {phr[2]}."
    cat = "vle"
    if names[0] in CAT["tma"]:
        cat = "tma"
    elif names[0] in CAT["profile"]:
        cat = "profile"
    s2 = ACTION[cat]
    s3 = "Đây là tín hiệu dự báo từ dữ liệu 28 ngày đầu, nên dùng để mở đầu trao đổi, không phải kết luận về năng lực của sinh viên."
    return names[0], "; ".join(names), phr, f"{s1} {s2} {s3}"


pri = pri.reset_index(drop=True)
expl = [describe(i) for i in range(len(pri))]
pri["yeu_to_1"] = [e[0] for e in expl]
pri["3_yeu_to_chinh"] = [e[1] for e in expl]
pri["mo_ta_vi"] = [e[3] for e in expl]
pri["ghi_chu_ten_yeu_to"] = [" | ".join(e[2]) for e in expl]
pri_out = pri[["code_module", "code_presentation", "id_student", "hang_trong_module_ky", "diem_rui_ro",
               "target", "label3", "yeu_to_1", "3_yeu_to_chinh", "ghi_chu_ten_yeu_to", "mo_ta_vi"]]
pri_out = pri_out.rename(columns={"target": "thuc_te_khong_hoan_thanh (chỉ để đánh giá)", "label3": "thuc_te_ket_qua (chỉ để đánh giá)"})
pri_out.to_csv(HERE / "q4_priority_list_test_k200.csv", index=False)

# Các đặc trưng đóng góp nhiều nhất trong danh sách (đếm theo lần xuất hiện trong top 3)
tops = []
for i in range(len(pri)):
    c = contrib[i]
    order = np.argsort(-c)
    for j in [j for j in order if c[j] > 0][:3]:
        tops.append(FEAT_ORDER[j])
top_counts = pd.Series(tops).value_counts().head(15)
top_counts.to_csv(HERE / "q5_top_driver_counts.csv", header=["so_lan_trong_top3"])
print("\n=== Câu 5: đặc trưng đóng góp nhiều nhất trong danh sách ưu tiên ===")
print(top_counts.to_string())

# Hàm mẫu cho cố vấn
print("\nVí dụ 3 học viên đầu danh sách:")
for t in pri_out.head(3).mo_ta_vi.tolist():
    print(" -", t)

# ----------------------------------------------------------------------------- biểu đồ
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False})
COL = {"Pass": "#2E7D32", "Fail": "#C62828", "Withdrawn": "#EF6C00"}
VI_OUT = {"Pass": "Đạt (Pass)", "Fail": "Trượt (Fail)", "Withdrawn": "Rút học (Withdrawn)"}
TITLES = {
    "q1": "Sinh viên đạt có trung vị lượt truy cập gấp 2,5–4 lần sinh viên Fail ở cả 4 tuần; Withdrawn nằm giữa",
    "q2": "Số ngày truy cập 0–28 phân biệt rõ nhất hoàn thành và không hoàn thành (hiệu ứng ~0,35)",
    "q3": "Trên test, mô hình bắt được 71,5% sinh viên không hoàn thành nhưng phải gắn cờ 53% quần thể",
    "q4": "Với 200 SV mỗi module-kỳ, 73–88% là không hoàn thành nhưng chỉ bắt được ~23% tổng số",
}

# Biểu đồ 1: trung vị lượt truy cập theo tuần, theo nhóm kết quả
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
for o in OUT_GROUPS:
    s = wk[wk.label3 == o]
    axes[0].plot(s.week, s.trung_vi_luot_truy_cap, marker="o", color=COL[o], label=VI_OUT[o])
    axes[1].plot(s.week, s.trung_vi_so_ngay_truy_cap, marker="o", color=COL[o], label=VI_OUT[o])
axes[0].set_title("Trung vị lượt truy cập theo tuần", fontsize=10)
axes[1].set_title("Trung vị số ngày có truy cập theo tuần", fontsize=10)
for ax in axes:
    ax.set_xlabel("Tuần (4 tuần đầu)")
    ax.set_xticks([1, 2, 3, 4])
axes[0].set_ylabel("Lượt truy cập")
axes[1].set_ylabel("Số ngày")
axes[1].legend(frameon=False, fontsize=9)
fig.suptitle(textwrap.fill(TITLES["q1"], 85), fontsize=11, y=1.04)
fig.tight_layout()
fig.savefig(HERE / "q1_weekly_by_outcome.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# Biểu đồ 2: hiệu ứng (rank-biserial) của các chỉ báo, nhóm hoàn thành so với không hoàn thành
top_q2 = q2.head(14).iloc[::-1]
fig, ax = plt.subplots(figsize=(9, 6))
colors = ["#1565C0" if p < 0.05 else "#9E9E9E" for p in top_q2.p_holm]
ax.barh(top_q2.mo_ta, top_q2.hieu_ung, color=colors)
ax.axvline(0, color="black", lw=0.8)
ax.set_xlabel("Hiệu ứng (dương = nhóm hoàn thành cao hơn)\nXanh = có ý nghĩa sau hiệu chỉnh Holm")
ax.set_title(textwrap.fill(TITLES["q2"], 65), fontsize=11, loc="left")
fig.tight_layout()
fig.savefig(HERE / "q2_indicator_effects.png", dpi=150)
plt.close(fig)

# Biểu đồ 3: đường lợi ích trên test (tỷ lệ gắn cờ so với tỷ lệ bắt được)
order = np.argsort(-p_te_main)
yy = yte[order]
cum_flag = np.arange(1, len(yy) + 1) / len(yy)
cum_catch = np.cumsum(yy) / yy.sum()
fig, ax = plt.subplots(figsize=(7, 5))
ax.plot(cum_flag * 100, cum_catch * 100, color="#1565C0", lw=2, label="Mô hình rủi ro")
ax.plot([0, 100], [0, 100], color="#9E9E9E", ls="--", label="Ngẫu nhiên")
ax.axhline(TARGET_RECALL * 100, color="#C62828", ls=":", label="Mục tiêu 70%")
ax.axvline(mt["ty_le_bi_gan_co"] * 100, color="#6A1B9A", ls=":", label=f"Ngưỡng đã chọn (gắn cờ {mt['ty_le_bi_gan_co']*100:.0f}%)")
ax.set_xlabel("% sinh viên được gắn cờ (theo thứ tự rủi ro giảm dần)")
ax.set_ylabel("% sinh viên không hoàn thành được bắt")
ax.set_title(textwrap.fill(TITLES["q3"], 65), fontsize=10, loc="left")
ax.legend(frameon=False, fontsize=9)
fig.tight_layout()
fig.savefig(HERE / "q3_test_capture_curve.png", dpi=150)
plt.close(fig)

# Biểu đồ 4: danh sách 200 bắt được bao nhiêu, so với nền
ct = cap[(cap.tap == "test") & (cap.k == CAP_DEFAULT)].copy()
fig, ax = plt.subplots(figsize=(8, 4.5))
xs = np.arange(len(ct) // 2)
w_ = 0.38
mdl = ct[ct.quy_tac == "mô hình rủi ro"].reset_index(drop=True)
base = ct[ct.quy_tac.str.startswith("ít")].reset_index(drop=True)
ax.bar(xs - w_ / 2, mdl.ty_le_trung * 100, w_, color="#1565C0", label="Mô hình rủi ro")
ax.bar(xs + w_ / 2, base.ty_le_trung * 100, w_, color="#9E9E9E", label="Đối chứng: ít truy cập nhất")
ax.set_xticks(xs)
ax.set_xticklabels(mdl.module_ky)
ax.set_ylabel("% trong 200 SV được liên hệ là không hoàn thành")
ax.set_title(textwrap.fill(TITLES["q4"], 70), fontsize=11, loc="left")
ax.legend(frameon=False, fontsize=9)
for i, (a, b) in enumerate(zip(mdl.ty_le_trung, base.ty_le_trung)):
    ax.text(i - w_ / 2, a * 100 + 1, f"{a*100:.0f}%", ha="center", fontsize=9)
    ax.text(i + w_ / 2, b * 100 + 1, f"{b*100:.0f}%", ha="center", fontsize=9)
fig.tight_layout()
fig.savefig(HERE / "q4_capacity_hits.png", dpi=150)
plt.close(fig)

print("\nHOÀN TẤT. Mô hình dùng cho danh sách:", scorer_name, "| giải thích: hồi quy logistic")
