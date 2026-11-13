"""Cảnh báo sớm OULAD (BBB, FFF) - mốc cuối ngày 28. Chạy: python outputs/early_warning/analysis.py"""
import os, json, warnings
import numpy as np, pandas as pd
from scipy import stats
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, roc_curve
warnings.filterwarnings("ignore")
D, O = "data", "outputs/early_warning"
os.makedirs(O, exist_ok=True)
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
COL = {"Pass": "#2a9d8f", "Fail": "#e9a03b", "Withdrawn": "#c0392b"}
VN = {"Pass": "Đạt (Pass)", "Fail": "Trượt (Fail)", "Withdrawn": "Rút lui (Withdrawn)"}
KEY = ["code_module", "code_presentation", "id_student"]

sw = pd.read_csv(D + "/aq1_student_week.csv")
dg = pd.read_csv(D + "/aq2_diagnostic_table.csv")
md = pd.read_csv(D + "/aq3_model_table.csv")
au = pd.read_csv(D + "/aq3_audit_attributes.csv")
par = json.load(open(D + "/aq4_decision_params.json"))
dg["grp"] = dg.code_module + " " + dg.code_presentation

# ---------------- Q1 ----------------
g = sw.groupby(["label3", "week"]).agg(n=("id_student", "nunique"), clicks_mean=("clicks", "mean"),
        clicks_median=("clicks", "median"), days_mean=("active_days", "mean"),
        zero_week_pct=("clicks", lambda s: (s == 0).mean() * 100)).round(2).reset_index()
g.to_csv(O + "/q1_weekly_by_outcome.csv", index=False)
tot = dg.groupby("label3").agg(n=("id_student", "size"), clicks_median=("clicks_0_28", "median"),
        clicks_mean=("clicks_0_28", "mean"), active_days_median=("active_days_0_28", "median"),
        no_activity_pct=("no_vle_activity_0_28", lambda s: s.mean() * 100),
        tma1_submitted_pct=("tma1_submitted_by_d28", lambda s: s.mean() * 100),
        tma1_score_median=("tma1_score", "median")).round(2)
tot.to_csv(O + "/q1_total_0_28_by_outcome.csv")
q1_kw = {}
for c in ["clicks_0_28", "active_days_0_28"]:
    v = stats.kruskal(*[x[c].values for _, x in dg.groupby("label3")])
    q1_kw[c] = (float(v.statistic), float(v.pvalue))
pw = []
for c in ["clicks_0_28", "active_days_0_28"]:
    for a, b in [("Pass", "Fail"), ("Pass", "Withdrawn"), ("Fail", "Withdrawn")]:
        x, y_ = dg.loc[dg.label3 == a, c], dg.loc[dg.label3 == b, c]
        u = stats.mannwhitneyu(x, y_); pw.append((c, a, b, min(1, u.pvalue * 3), u.statistic / (len(x) * len(y_))))
pd.DataFrame(pw, columns=["indicator", "A", "B", "p_bonf", "AUC_A_gt_B"]).to_csv(O + "/q1_pairwise.csv", index=False)

fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
for lab in ["Pass", "Fail", "Withdrawn"]:
    s = g[g.label3 == lab]
    ax[0].plot(s.week, s.clicks_median, marker="o", color=COL[lab], label=VN[lab])
    ax[1].plot(s.week, s.days_mean, marker="o", color=COL[lab], label=VN[lab])
ax[0].set_title("Số lượt click trung vị mỗi tuần"); ax[1].set_title("Số ngày hoạt động trung bình mỗi tuần (tối đa 7)")
for a in ax:
    a.set_xlabel("Tuần của khóa học"); a.set_xticks([1, 2, 3, 4])
ax[0].set_ylabel("Lượt click (trung vị)"); ax[1].set_ylabel("Ngày hoạt động"); ax[0].legend(frameon=False)
fig.suptitle("Tương tác 4 tuần đầu theo kết quả cuối khóa", fontweight="bold"); fig.tight_layout()
fig.savefig(O + "/q1_weekly_engagement.png", dpi=150); plt.close()

# ---------------- Q2 ----------------
ind = ["clicks_w%d" % i for i in range(1, 5)] + ["active_days_w%d" % i for i in range(1, 5)] + \
      ["clicks_0_28", "active_days_0_28", "n_sites_0_28", "days_since_last_active_d28", "clicks_pre_start",
       "clicks_forumng_0_28", "clicks_oucontent_0_28", "clicks_quiz_0_28", "clicks_homepage_0_28",
       "clicks_subpage_0_28", "clicks_resource_0_28", "clicks_url_0_28",
       "tma1_submitted_by_d28", "tma1_on_time", "tma1_score", "tma1_days_before_deadline",
       "num_of_prev_attempts", "studied_credits", "highest_education_ord", "registration_lead_days"]
for k in range(1, 5):
    dg["cum_clicks_w1_%d" % k] = dg[["clicks_w%d" % i for i in range(1, k + 1)]].sum(axis=1)
    dg["cum_days_w1_%d" % k] = dg[["active_days_w%d" % i for i in range(1, k + 1)]].sum(axis=1)
ind += ["cum_clicks_w1_%d" % k for k in range(1, 5)] + ["cum_days_w1_%d" % k for k in range(1, 5)]
rows = []
for c in ind:
    d = dg[[c, "target_noncompletion", "grp"]].dropna()
    x, y_ = d.loc[d.target_noncompletion == 0, c], d.loc[d.target_noncompletion == 1, c]
    u = stats.mannwhitneyu(x, y_)
    auc = u.statistic / (len(x) * len(y_))
    sg = []
    for _, t in d.groupby("grp"):
        a_, b_ = t.loc[t.target_noncompletion == 0, c], t.loc[t.target_noncompletion == 1, c]
        df_ = a_.median() - b_.median()
        sg.append(np.sign(df_) if df_ != 0 else np.sign(a_.mean() - b_.mean()))
    sg = np.array(sg)
    rows.append(dict(indicator=c, n=len(d), median_complete=x.median(), median_noncomplete=y_.median(),
                     mean_complete=x.mean(), mean_noncomplete=y_.mean(), AUC=auc, cliffs_delta=2 * auc - 1,
                     p=u.pvalue, groups_same_direction=int(max((sg > 0).sum(), (sg < 0).sum()))))
q2 = pd.DataFrame(rows)
q2["p_bonferroni"] = np.minimum(1, q2.p * len(q2))
q2["significant"] = q2.p_bonferroni < 0.05
q2["effect"] = pd.cut(q2.cliffs_delta.abs(), [-1, .1, .2, .35, 1], labels=["không đáng kể", "nhỏ", "vừa", "lớn"])
q2 = q2.round(4); q2.to_csv(O + "/q2_indicator_tests.csv", index=False)
wk = []
for c in ["clicks_w", "active_days_w"]:
    for i in range(1, 5):
        for lab in ["Fail", "Withdrawn"]:
            x, y_ = dg.loc[dg.label3 == "Pass", "%s%d" % (c, i)], dg.loc[dg.label3 == lab, "%s%d" % (c, i)]
            u = stats.mannwhitneyu(x, y_)
            wk.append(dict(metric=c[:-2], week=i, vs=lab, cliffs_delta_pass_minus=2 * u.statistic / (len(x) * len(y_)) - 1, p=u.pvalue))
wkt = pd.DataFrame(wk); wkt.round(4).to_csv(O + "/q2_weekly_pass_vs_nonpass.csv", index=False)

top = q2.reindex(q2.cliffs_delta.abs().sort_values(ascending=False).index).head(14)
fig, ax = plt.subplots(figsize=(8, 5.5))
ax.barh(top.indicator[::-1], top.cliffs_delta[::-1], color="#2a6f97")
ax.set_xlabel("Cliff's delta (dương: nhóm hoàn thành cao hơn)")
ax.set_title("14 chỉ báo khác biệt mạnh nhất giữa hoàn thành và không hoàn thành", fontweight="bold", fontsize=10)
fig.tight_layout(); fig.savefig(O + "/q2_top_indicators.png", dpi=150); plt.close()
fig, ax = plt.subplots(figsize=(7.5, 4))
for (m, v), s in wkt.groupby(["metric", "vs"]):
    ax.plot(s.week, s.cliffs_delta_pass_minus, marker="o", ls="-" if m == "clicks" else "--", color=COL[v],
            label="%s - Đạt so với %s" % ("Click" if m == "clicks" else "Ngày hoạt động", v))
ax.set_xticks([1, 2, 3, 4]); ax.set_xlabel("Tuần"); ax.set_ylabel("Mức khác biệt (Cliff's delta)")
ax.set_title("Khác biệt so với nhóm Đạt đã rõ từ tuần 1", fontweight="bold", fontsize=10)
ax.legend(frameon=False, fontsize=8); fig.tight_layout(); fig.savefig(O + "/q2_effect_by_week.png", dpi=150); plt.close()

# ---------------- Q3 ----------------
feat = [c for c in md.columns if c not in KEY + ["split", "target_noncompletion", "clicks_0_28"]]
def prep(df):
    X = df[feat].copy()
    X["tma1_score_missing"] = X.tma1_score.isna().astype(int)
    X["tma1_score"] = X.tma1_score.fillna(0); X["tma1_days_before_deadline"] = X.tma1_days_before_deadline.fillna(0)
    return X
X_raw = prep(md); y = md.target_noncompletion.values
tr, va, te = [(md.split == s).values for s in ["train", "validation", "test"]]
# PHÁT HIỆN: BBB 2014J (tập test) có 38% điểm tma1_score = 1 và phần còn lại ~100 -> thang điểm khác các kỳ khác
# (không kỳ nào khác có điểm 1). Quy tắc: module-kỳ nào có >10% điểm == 1 thì coi tma1_score là không so sánh được (như thiếu).
share1 = md.assign(o=(md.tma1_score == 1)).groupby(["code_module", "code_presentation"]).o.transform("mean")
art = (share1 > 0.10).values
print("Số SV thuộc module-kỳ có thang điểm TMA1 bất thường:", art.sum())
X = X_raw.copy(); X.loc[art, "tma1_score"] = md.loc[tr & (md.tma1_submitted_by_d28 == 1), "tma1_score"].median(); X.loc[art, "tma1_score_missing"] = 0
skew = [c for c in X.columns if c.startswith("clicks_") and c != "clicks_change_w1_w4"] + ["n_sites_0_28", "active_days_pre_start"]
def lg(X):
    Z = X.copy()
    for c in skew: Z[c] = np.log1p(Z[c].clip(lower=0))
    return Z
sc = StandardScaler().fit(lg(X[tr]))
Xl = pd.DataFrame(sc.transform(lg(X)), columns=X.columns, index=X.index)
res = {}
lr = LogisticRegression(C=0.1, max_iter=2000).fit(Xl[tr], y[tr]); res["Logistic"] = lr.predict_proba(Xl)[:, 1]
gb = HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=200, l2_regularization=1.0, random_state=0).fit(X[tr], y[tr])
res["GradientBoosting"] = gb.predict_proba(X)[:, 1]
res["Baseline: -log(click 0-28)"] = -md.log_clicks_0_28.values
res["Baseline: chua nop TMA1 + it ngay"] = (1 - md.tma1_submitted_by_d28.values) * 100 - md.active_days_0_28.values
# so sánh độ nhạy: dữ liệu thô (chưa xử lý thang điểm TMA1 bất thường) vs đã xử lý
sens = []
for nm, XX in [("tho (giu tma1_score = 1)", X_raw), ("da xu ly (tma1_score BBB 2014J = trung vi train)", X)]:
    Z = lg(XX); sc2 = StandardScaler().fit(Z[tr]); Zs = sc2.transform(Z)
    l2 = LogisticRegression(C=0.1, max_iter=2000).fit(Zs[tr], y[tr]); p1 = l2.predict_proba(Zs)[:, 1]
    g2 = HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=200, l2_regularization=1.0, random_state=0).fit(XX[tr], y[tr]); p2 = g2.predict_proba(XX)[:, 1]
    for mn, pp in [("Logistic", p1), ("GradientBoosting", p2)]:
        sens.append(dict(du_lieu=nm, model=mn, AUC_val=roc_auc_score(y[va], pp[va]), AUC_test=roc_auc_score(y[te], pp[te]),
                         AUC_test_BBB2014J=roc_auc_score(y[art], pp[art]), AUC_test_FFF2014J=roc_auc_score(y[te & ~art], pp[te & ~art])))
pd.DataFrame(sens).round(4).to_csv(O + "/q3_sensitivity_tma1_scale_artifact.csv", index=False)
print(pd.DataFrame(sens).round(3).to_string())
def rec_prec(s, yy, thr):
    f = s >= thr
    return yy[f].sum() / yy.sum(), (yy[f].mean() if f.any() else np.nan), f.mean()
rows = []
for n, s in res.items():
    r = dict(model=n)
    for nm, m in [("val", va), ("test", te)]:
        r["AUC_" + nm] = roc_auc_score(y[m], s[m]); r["PRAUC_" + nm] = average_precision_score(y[m], s[m])
    thr = np.quantile(s[va][y[va] == 1], 0.30)
    r["thr_from_val"] = thr
    for nm, m in [("val", va), ("test", te)]:
        rc, pr, fr = rec_prec(s[m], y[m], thr); r["recall_" + nm], r["precision_" + nm], r["flagged_share_" + nm] = rc, pr, fr
    rows.append(r)
q3 = pd.DataFrame(rows).round(4); q3.to_csv(O + "/q3_model_comparison.csv", index=False)
print(q3.T.to_string())
qi = q3.set_index("model")
best = "Logistic" if qi.loc["Logistic", "AUC_val"] >= qi.loc["GradientBoosting", "AUC_val"] - 0.01 else "GradientBoosting"
print("MODEL CHON:", best)
S = res[best]
fig, ax = plt.subplots(1, 2, figsize=(11, 4.3))
for n in ["Logistic", "GradientBoosting", "Baseline: -log(click 0-28)"]:
    fpr, tpr, _ = roc_curve(y[te], res[n][te]); ax[0].plot(fpr, tpr, label="%s (AUC=%.3f)" % (n, roc_auc_score(y[te], res[n][te])))
ax[0].plot([0, 1], [0, 1], "k:", lw=1); ax[0].set_xlabel("Tỷ lệ báo động nhầm (sinh viên hoàn thành bị gắn cờ)"); ax[0].set_ylabel("Recall (bắt được không hoàn thành)")
ax[0].axhline(.7, color="#c0392b", ls="--", lw=1); ax[0].text(.55, .72, "Mục tiêu 70%", color="#c0392b"); ax[0].set_title("Đường ROC trên tập kiểm tra (2014J)"); ax[0].legend(frameon=False, fontsize=8, loc="lower right")
o = np.argsort(-S[te]); yy = y[te][o]; share = np.arange(1, len(yy) + 1) / len(yy)
cg = np.cumsum(yy) / yy.sum()
ax[1].plot(share * 100, cg * 100, color="#2a6f97", label="Mô hình"); ax[1].plot([0, 100], [0, 100], "k:", label="Ngẫu nhiên")
ax[1].axhline(70, color="#c0392b", ls="--", lw=1)
i70 = np.searchsorted(cg, .7); ax[1].plot(share[i70] * 100, 70, "o", color="#c0392b")
ax[1].annotate("Cần gắn cờ %.0f%% sinh viên\nđể bắt 70%%" % (share[i70] * 100), (share[i70] * 100, 70), (share[i70] * 100 + 8, 45), arrowprops=dict(arrowstyle="->"))
ax[1].set_xlabel("% sinh viên được gắn cờ (xếp theo rủi ro)"); ax[1].set_ylabel("% sinh viên không hoàn thành bắt được"); ax[1].set_title("Đường thu hồi (gain) - tập kiểm tra"); ax[1].legend(frameon=False)
fig.tight_layout(); fig.savefig(O + "/q3_model_performance.png", dpi=150); plt.close()
print("Flag share needed for 70% recall on test:", share[i70])
cal = pd.DataFrame({"s": S[te], "y": y[te]}); cal["bin"] = pd.qcut(cal.s, 10, duplicates="drop")
cal.groupby("bin").agg(pred=("s", "mean"), obs=("y", "mean"), n=("y", "size")).round(3).to_csv(O + "/q3_calibration_test_deciles.csv")
print("Brier", brier_score_loss(y[te], S[te]))
rng = np.random.default_rng(0); idx = np.where(te)[0]
bs = [roc_auc_score(y[b], S[b]) for b in (rng.choice(idx, len(idx)) for _ in range(300))]
ci = np.percentile(bs, [2.5, 97.5]); print("AUC test CI", ci)
md["score"] = S
thr = np.quantile(S[va][y[va] == 1], 0.30)
rc, pr, fr = rec_prec(S[te], y[te], thr)
print("Q3 thr val:", thr, "test recall/prec/flag", rc, pr, fr)
pd.DataFrame([dict(model=best, thr=thr, recall_test=rc, precision_test=pr, flagged_share_test=fr, base_rate_test=y[te].mean(),
                   flag_share_for_70pct_recall_test=share[i70], auc_ci_lo=ci[0], auc_ci_hi=ci[1])]).round(4).to_csv(O + "/q3_operating_point.csv", index=False)

# ---------------- Q4 ----------------
K_list = par["capacity_k_per_module_presentation"]; conv = par["assumed_conversion_rate"]
rules = {"Mô hình (điểm rủi ro)": md.score.values,
         "Quy tắc đơn giản: ít click nhất 0-28": -md.log_clicks_0_28.values + 1e-6 * md.score.values,
         "Quy tắc đơn giản: chưa nộp TMA1, rồi ít ngày hoạt động": (1 - md.tma1_submitted_by_d28.values) * 100 - md.active_days_0_28.values + 1e-6 * md.score.values}
rows = []
for sp, m in [("validation", va), ("test", te)]:
    for K in K_list:
        for rn, s in list(rules.items()) + [("Ngẫu nhiên", None)]:
            hit = pos = n = 0
            for gk, ix in md[m].groupby(["code_module", "code_presentation"]).groups.items():
                ii = md.index.get_indexer(ix)
                if s is None:
                    h = np.mean([y[rng.choice(ii, K, replace=False)].sum() for _ in range(200)])
                else:
                    sel = ii[np.argsort(-s[ii])[:K]]; h = y[sel].sum()
                hit += h; pos += y[ii].sum(); n += min(K, len(ii))
            rows.append(dict(split=sp, K=K, rule=rn, flagged=n, hits=round(hit, 1), precision=hit / n, recall=hit / pos,
                             noncompleters_total=int(pos), expected_helped=hit * conv))
q4 = pd.DataFrame(rows).round(4); q4.to_csv(O + "/q4_priority_list_performance.csv", index=False)
print(q4[q4.K == 200].to_string())
lists = []
for gk, grp_ in md[te].groupby(["code_module", "code_presentation"]):
    lists.append(grp_.sort_values("score", ascending=False).head(par["default_k"]).assign(rank=lambda d: np.arange(1, len(d) + 1)))
pl = pd.concat(lists)
pm = pl.groupby(["code_module", "code_presentation"]).agg(flagged=("target_noncompletion", "size"), hits=("target_noncompletion", "sum"))
pm["precision"] = pm.hits / pm.flagged
pm = pm.join(md[te].groupby(["code_module", "code_presentation"]).target_noncompletion.agg(total_noncomp="sum", students="size"))
pm["recall"] = pm.hits / pm.total_noncomp; pm["base_rate"] = pm.total_noncomp / pm.students
pm.round(4).to_csv(O + "/q4_per_module_presentation_test_k200.csv")
a = pl.merge(au, on=KEY); allte = md[te].merge(au, on=KEY)
fa = []
for c in ["gender", "age_band", "disability"]:
    t = pd.concat([allte.groupby(c).size().rename("students"), a.groupby(c).size().rename("flagged")], axis=1).fillna(0)
    t["flag_rate_pct"] = t.flagged / t.students * 100; t["attribute"] = c
    fa.append(t.reset_index().rename(columns={c: "value", "index": "value"}))
pd.concat(fa).round(2).to_csv(O + "/q4_audit_flag_rate_by_group.csv", index=False)
sub = q4[q4.split == "test"]
fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
pv = sub.pivot(index="K", columns="rule", values="precision") * 100; pv.plot.bar(ax=ax[0], rot=0, width=.8)
ax[0].set_ylabel("% trúng (thực sự không hoàn thành)"); ax[0].set_xlabel("Số sinh viên liên hệ mỗi module-kỳ (K)"); ax[0].set_title("Độ chính xác danh sách ưu tiên (test 2014J)")
ax[0].axhline(y[te].mean() * 100, color="k", ls=":", lw=1); ax[0].legend(frameon=False, fontsize=7)
rv = sub.pivot(index="K", columns="rule", values="recall") * 100; rv.plot.bar(ax=ax[1], rot=0, width=.8, legend=False)
ax[1].set_ylabel("% sinh viên không hoàn thành được bắt"); ax[1].set_xlabel("K"); ax[1].axhline(70, color="#c0392b", ls="--"); ax[1].text(-.4, 72, "Mục tiêu 70%", color="#c0392b"); ax[1].set_title("Độ phủ (recall) - xa mục tiêu 70%"); ax[1].set_ylim(0, 100)
fig.tight_layout(); fig.savefig(O + "/q4_priority_list.png", dpi=150); plt.close()

# ---------------- Q5 ----------------
coef = pd.Series(lr.coef_[0], index=X.columns)
contrib = Xl.mul(coef, axis=1)  # đã chuẩn hóa quanh trung bình train => đóng góp so với SV trung bình
DESC = {"clicks_w1": "lượt click tuần 1", "clicks_w2": "lượt click tuần 2", "clicks_w3": "lượt click tuần 3", "clicks_w4": "lượt click tuần 4",
        "active_days_w1": "số ngày học tuần 1", "active_days_w2": "số ngày học tuần 2", "active_days_w3": "số ngày học tuần 3", "active_days_w4": "số ngày học tuần 4",
        "log_clicks_0_28": "tổng lượt click 28 ngày đầu", "active_days_0_28": "tổng số ngày vào học trong 28 ngày", "n_sites_0_28": "số loại trang học liệu đã mở",
        "clicks_change_w1_w4": "mức thay đổi click từ tuần 1 đến tuần 4", "days_since_last_active_d28": "số ngày kể từ lần vào học gần nhất",
        "clicks_pre_start": "lượt click trước khi khóa bắt đầu", "active_days_pre_start": "số ngày vào học trước khi khóa bắt đầu",
        "no_vle_activity_0_28": "không có hoạt động nào trên hệ thống", "clicks_homepage_0_28": "click trang chủ", "clicks_oucontent_0_28": "click nội dung bài học",
        "clicks_resource_0_28": "click tài liệu", "clicks_subpage_0_28": "click trang con", "clicks_forumng_0_28": "click diễn đàn", "clicks_quiz_0_28": "click quiz",
        "clicks_url_0_28": "click liên kết ngoài", "tma1_submitted_by_d28": "nộp bài TMA1 trước ngày 28", "tma1_on_time": "nộp TMA1 đúng hạn",
        "tma1_days_before_deadline": "số ngày nộp TMA1 sớm hơn hạn", "num_of_prev_attempts": "số lần học lại module", "studied_credits": "tổng tín chỉ đang học",
        "highest_education_ord": "trình độ học vấn đầu vào", "registration_lead_days": "số ngày đăng ký trước khi khóa bắt đầu", "tma1_score": "điểm bài TMA1",
        "seen_in_earlier_presentation": "từng xuất hiện ở kỳ trước", "late_registration_1_28": "đăng ký muộn", "days_observable_0_28": "số ngày quan sát được",
        "flag_high_activity": "cờ hoạt động rất cao", "tma1_score_missing": "chưa có điểm TMA1"}
pl = pl.copy(); pl["row"] = pl.index
# gom đặc trưng tương quan thành chủ đề (tổng đóng góp logistic của từng chủ đề)
THEME = {}
for c in X.columns:
    pass
CLKF = [c for c in X.columns if c.startswith("clicks_") and c not in ("clicks_pre_start", "clicks_change_w1_w4")] + ["log_clicks_0_28", "n_sites_0_28"]
for c in X.columns:
    if c.startswith("tma1"): THEME[c] = "tma1"
    elif c in CLKF: THEME[c] = "luong_truy_cap"
    elif c.startswith("active_days_w") or c == "active_days_0_28": THEME[c] = "so_ngay_hoc"
    elif c == "days_since_last_active_d28": THEME[c] = "lan_hoc_gan_nhat"
    elif c in ("clicks_change_w1_w4", "no_vle_activity_0_28"): THEME[c] = "xu_huong_giam"
    elif c in ("clicks_pre_start", "active_days_pre_start", "registration_lead_days", "late_registration_1_28", "days_observable_0_28"): THEME[c] = "chuan_bi_truoc_khoa"
    else: THEME[c] = "ho_so_hoc_tap"
TH = contrib.T.groupby(THEME).sum().T
rows = []
for _, r in pl.iterrows():
    tp = TH.loc[r["row"]].sort_values(ascending=False).head(3)
    rows.append(dict(code_module=r.code_module, code_presentation=r.code_presentation, id_student=r.id_student, rank=r["rank"],
                     risk_score=round(r.score, 3), actual_noncompletion=r.target_noncompletion,
                     top1=tp.index[0], top1_contrib=tp.iloc[0], top2=tp.index[1], top2_contrib=tp.iloc[1], top3=tp.index[2], top3_contrib=tp.iloc[2],
                     clicks_0_28=md.loc[r["row"], "clicks_0_28"], active_days_0_28=md.loc[r["row"], "active_days_0_28"],
                     tma1_submitted=md.loc[r["row"], "tma1_submitted_by_d28"], tma1_score=md.loc[r["row"], "tma1_score"],
                     days_since_last_active=md.loc[r["row"], "days_since_last_active_d28"],
                     highest_education_ord=md.loc[r["row"], "highest_education_ord"], num_prev=md.loc[r["row"], "num_of_prev_attempts"]))
q5 = pd.DataFrame(rows)
MED_CLK = int(md.clicks_0_28.median()); MED_DAYS = int(md.active_days_0_28.median())
TH_VN = {"tma1": "bài TMA1", "luong_truy_cap": "lượng truy cập học liệu", "so_ngay_hoc": "số ngày vào học", "lan_hoc_gan_nhat": "khoảng cách từ lần học gần nhất",
         "xu_huong_giam": "xu hướng học giảm", "chuan_bi_truoc_khoa": "mức chuẩn bị trước khi khóa bắt đầu", "ho_so_hoc_tap": "hồ sơ học tập (học vấn đầu vào, tín chỉ, số lần học lại)"}
def advice(r):
    f = []
    for k in ["top1", "top2", "top3"]:
        c = r[k]
        if c == "tma1": f.append("chưa nộp bài TMA1 (bài kiểm tra đầu tiên)" if r.tma1_submitted == 0 else "bài TMA1 nộp muộn hoặc kết quả chưa tốt")
        elif c == "luong_truy_cap": f.append("lượng truy cập học liệu chỉ %d lượt click trong 28 ngày đầu (trung vị toàn khóa: %d)" % (r.clicks_0_28, MED_CLK))
        elif c == "so_ngay_hoc": f.append("chỉ vào học %d ngày trong 29 ngày đầu (trung vị: %d)" % (r.active_days_0_28, MED_DAYS))
        elif c == "lan_hoc_gan_nhat": f.append("đã %d ngày chưa vào học" % r.days_since_last_active)
        elif c == "xu_huong_giam": f.append("mức học giảm dần qua các tuần")
        elif c == "chuan_bi_truoc_khoa": f.append("ít làm quen với hệ thống trước khi khóa bắt đầu")
        else: f.append("hồ sơ nền (trình độ đầu vào thấp hơn mức trung bình hoặc đã từng học lại)" if (r.highest_education_ord < 2 or r.num_prev > 0) else "hồ sơ nền (khối lượng tín chỉ/trình độ đầu vào)")
    lead = ", ".join(f[:-1]) + (" và " if len(f) > 1 else "") + f[-1]
    return "Sinh viên này được ưu tiên chủ yếu vì " + lead + ". Nên liên hệ sớm để hỏi về khó khăn và hỗ trợ lịch học (đây là dấu hiệu tương quan, không khẳng định nguyên nhân)."
q5["ghi_chu_co_van"] = q5.apply(advice, axis=1)
q5.round(3).to_csv(O + "/q5_priority_list_with_reasons.csv", index=False)
cnt = pd.concat([q5.top1, q5.top2, q5.top3]).value_counts().rename("so_sv_co_trong_top3")
cnt1 = q5.top1.value_counts().rename("so_sv_top1"); print(cnt1)
cnt.to_csv(O + "/q5_top_driver_counts.csv")
coef.rename("coef").to_csv(O + "/q5_logistic_coefficients.csv")
fig, ax = plt.subplots(figsize=(8, 4.5)); c10 = cnt.head(8)[::-1]
ax.barh([TH_VN.get(i, i) for i in c10.index], c10.values, color="#2a6f97"); ax.set_xlabel("Số sinh viên ưu tiên có đặc trưng này trong top-3 đóng góp rủi ro")
ax.set_title("Đặc trưng thúc đẩy rủi ro nhiều nhất (%d sinh viên ưu tiên)" % len(q5), fontweight="bold", fontsize=10); fig.tight_layout(); fig.savefig(O + "/q5_top_drivers.png", dpi=150); plt.close()
print(cnt.head(10)); print(coef.sort_values(key=abs, ascending=False).head(12))
print(q5.groupby("code_module").size()); print(q5.ghi_chu_co_van.head(3).tolist())
print(tot.to_string()); print(q1_kw)
print(q2[["indicator", "AUC", "cliffs_delta", "p_bonferroni", "effect", "groups_same_direction"]].to_string())
print(wkt.round(3).to_string()); print(pm.round(3)); print(pd.read_csv(O + "/q4_audit_flag_rate_by_group.csv"))
print(pd.read_csv(O + "/q1_pairwise.csv")); print(g.to_string())
