"""Q5: for every student in the priority list (2014J, top 200 per module-presentation),
list the features that add most to the risk score and write short advisor notes."""
import pandas as pd, numpy as np

D = "data/"
OUT = "outputs/"
K = ['code_module', 'code_presentation', 'id_student']

m = pd.read_csv(D + "aq3_model_table.csv")
for c in ['tma1_days_before_deadline', 'tma1_score']:
    m[c] = m[c].fillna(m.loc[m.split == 'train', c].mean())
con = pd.read_csv(OUT + "q5_contributions_priority.csv")
pri = pd.read_csv(OUT + "q4_priority_list_2014J.csv")
FEATS = [c for c in con.columns if c not in K]

rows = []
for _, r in pri.iterrows():
    key = (r.code_module, r.code_presentation, r.id_student)
    c = con[(con.code_module == r.code_module) & (con.code_presentation == r.code_presentation) & (con.id_student == r.id_student)]
    vals = c[FEATS].iloc[0].sort_values(ascending=False)
    pos = vals[vals > 0.05]
    top = list(pos.index[:2])
    mm = m[(m.code_module == r.code_module) & (m.code_presentation == r.code_presentation) & (m.id_student == r.id_student)].iloc[0]
    rows.append(dict(code_module=r.code_module, code_presentation=r.code_presentation, id_student=r.id_student,
                     rank_in_mp=r.rank_in_mp, risk_score=round(r.risk_score, 3),
                     yếu_tố_1=top[0] if len(top) > 0 else '', yếu_tố_1_đóng_góp=round(pos.iloc[0], 3) if len(pos) else 0,
                     yếu_tố_2=top[1] if len(top) > 1 else '', yếu_tố_2_đóng_góp=round(pos.iloc[1], 3) if len(pos) > 1 else 0,
                     tma1_submitted=int(mm.tma1_submitted_by_d28), tma1_score=round(mm.tma1_score, 1),
                     clicks_0_28=int(mm.clicks_0_28), days_since_last_active=int(mm.days_since_last_active_d28),
                     target=int(r.target_noncompletion) if 'target_noncompletion' in r else None))
out = pd.DataFrame(rows)
out.to_csv(OUT + "q5_top_factors_priority_2014J.csv", index=False)
print(out.yếu_tố_1.value_counts().to_string())
print(out.yếu_tố_2.value_counts().to_string())
print(out.groupby('yếu_tố_1').tma1_submitted.mean())
print(out[['tma1_submitted', 'tma1_score', 'clicks_0_28', 'days_since_last_active']].describe().T.to_string())

# ---- advisor-friendly notes (2-3 sentences per student) ----
def phrase(feat, row):
    if feat == 'tma1_submitted_by_d28':
        return "chưa nộp bài đánh giá đầu tiên (TMA1) trước ngày 28"
    if feat == 'tma1_score':
        return f"bài TMA1 đã nộp nhưng điểm thấp ({row.tma1_score:.0f}/100)"
    if feat == 'tma1_on_time':
        return "bài TMA1 nộp muộn so với hạn"
    if feat in ('clicks_0_28', 'log_clicks_0_28', 'clicks_w1', 'clicks_w2', 'clicks_w3', 'clicks_w4'):
        return f"ít truy cập học liệu trong 4 tuần đầu ({row.clicks_0_28} lượt nhấp)"
    if feat in ('active_days_0_28', 'active_days_w1', 'active_days_w2', 'active_days_w3', 'active_days_w4'):
        return "ít ngày có hoạt động trong 4 tuần đầu"
    if feat == 'days_since_last_active_d28':
        return f"lâu không đăng nhập học ({row.days_since_last_active} ngày tính đến ngày 28)"
    if feat in ('clicks_subpage_0_28', 'clicks_resource_0_28', 'clicks_oucontent_0_28', 'clicks_homepage_0_28', 'n_sites_0_28'):
        return "ít mở các phần học liệu khác nhau"
    if feat == 'highest_education_ord':
        return "trình độ học vấn trước khi nhập học ở mức thấp"
    if feat == 'num_of_prev_attempts':
        return "đã từng phải học lại môn này"
    if feat in ('clicks_pre_start', 'active_days_pre_start'):
        return "ít hoạt động trước khi khóa học bắt đầu"
    return f"chỉ số {feat} ở mức bất lợi"

def action(f1):
    if f1 == 'tma1_submitted_by_d28':
        return "nhắc nộp bài TMA1 và hỏi xem sinh viên có khó khăn gì khiến chưa nộp"
    if f1 == 'tma1_score':
        return "hẹn trao đổi về cách làm bài và các nội dung còn yếu"
    return "trao đổi để biết sinh viên có gặp trở ngại về thời gian hay truy cập học liệu không"

notes = []
for _, r in out.iterrows():
    row = m[(m.code_module == r.code_module) & (m.code_presentation == r.code_presentation) & (m.id_student == r.id_student)].iloc[0]
    row = row.copy(); row['tma1_score'] = r.tma1_score; row['clicks_0_28'] = r.clicks_0_28; row['days_since_last_active'] = r.days_since_last_active
    f1 = r.yếu_tố_1; f2 = r.yếu_tố_2
    s1 = f"Sinh viên {r.id_student} ({r.code_module} {r.code_presentation}) nằm trong nhóm ưu tiên hạng {r.rank_in_mp}; yếu tố làm tăng rủi ro nhiều nhất là {phrase(f1, row)}."
    s2 = f" Yếu tố tiếp theo: {phrase(f2, row)}." if f2 else ""
    s3 = f" Gợi ý: {action(f1)}."
    notes.append(s1 + s2 + s3)
out['ghi_chú_cho_cố_vấn'] = notes
out.to_csv(OUT + "q5_top_factors_priority_2014J.csv", index=False)
print(out['ghi_chú_cho_cố_vấn'].head(3).to_string())
