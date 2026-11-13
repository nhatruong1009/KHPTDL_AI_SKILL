# oulad_early_warning · sonnet__skills · r1

| | |
|---|---|
| Điểm overall / accuracy / quality | 100.0 / 100.0 / 100.0 |
| Thời gian · chi phí · số turn | 301.0 s · $0.721 · 36 |
| Skill đã nạp (theo thứ tự) | `data-eda` → `data-relevance` → `analysis-plan` → `group-compare` → `data-predict` → `data-chart` → `answer-write` → `answer-qa` |
| Lỗi công cụ | 3 |

## Các bước

1. **SKILL `data-eda`**
2. Bash: `cd data; ls -la; for f in *; do echo "== $f"; head -3 "$f"; wc -l "$f"; done; python -c "import pandas, sklearn, scipy, matplotlib, seaborn; print('ok')"`  
  ↳ **lỗi:** A variable in this command can't be checked before it runs
3. Bash: `ls -la data; ls .claude/skills/data-eda/scripts; python -c "import pandas, sklearn, scipy, matplotlib, seaborn; print('ok')"`
4. Bash: `python .claude/skills/data-eda/scripts/inspect_data.py data 2>&1 | head -300; cat data/aq4_decision_params.json`
5. Bash: `cd data; cat aq4_decision_params.json; for f in aq2* aq3* context*; do echo "== $f"; head -4 $f; done; python - <<'E' import pandas as pd for f in ['aq2_diagnostic_table','aq3_audit_attributes','aq3_model_table','context_all_registrations']: d=pd.read_csv(f+'.csv');print(f,d.shape);print(d.dtypes.t…`  
  ↳ **lỗi:** A variable in this command can't be checked before it runs

> Avoid shell variables.

6. Bash: `cat data/aq4_decision_params.json; head -3 data/aq2_diagnostic_table.csv data/aq3_audit_attributes.csv data/aq3_model_table.csv data/context_all_registrations.csv`
7. Bash: `python - <<'E' import pandas as pd for f in ['aq2_diagnostic_table','aq3_audit_attributes','aq3_model_table','context_all_registrations']: d=pd.read_csv('data/'+f+'.csv');print(f,d.shape);print(d.dtypes.to_string());m=d.isna().mean();print(m[m>0].to_string()) for c in d.columns: if d[c].dtype.kind …`
8. **SKILL `data-relevance`**
9. **SKILL `analysis-plan`**
10. **SKILL `group-compare`**
11. **SKILL `data-predict`**
12. Bash: `python - <<'E' import pandas as pd, numpy as np m=pd.read_csv('data/aq3_model_table.csv'); d=pd.read_csv('data/aq2_diagnostic_table.csv'); w=pd.read_csv('data/aq1_student_week.csv'); c=pd.read_csv('data/context_all_registrations.csv') k=['code_module','code_presentation','id_student'] print(m.dupli…`
13. Bash: `python - <<'E' import pandas as pd m=pd.read_csv('data/aq3_model_table.csv'); w=pd.read_csv('data/aq1_student_week.csv') k=['code_module','code_presentation','id_student'] p=w.pivot_table(index=k,columns='week',values='clicks').reset_index().merge(m,on=k) print(((p[1]==p.clicks_w1)&(p[2]==p.clicks_…`
14. **SKILL `data-chart`**

> Đang chạy phân tích Q1–Q2 (so sánh nhóm theo tuần), sau đó là mô hình Q3–Q5.

15. Bash: `mkdir -p outputs/oulad-early-warning && cat > outputs/oulad-early-warning/q1_q2.py <<'E' import pandas as pd, numpy as np, matplotlib matplotlib.use("Agg") import matplotlib.pyplot as plt, seaborn as sns from scipy import stats OUT='outputs/oulad-early-warning/' d=pd.read_csv('data/aq2_diagnostic_t…`  
  ↳ **lỗi:** Contains brace with quote character (expansion obfuscation)
16. Write `outputs/oulad-early-warning/q1_q2.py`
17. Bash: `python outputs/oulad-early-warning/q1_q2.py 2>&1 | tail -170`
18. Write `outputs/oulad-early-warning/model.py`
19. Bash: `python outputs/oulad-early-warning/model.py 2>&1 | head -230`
20. Bash: `python - <<'E' import pandas as pd L=pd.read_csv('outputs/oulad-early-warning/q4_q5_priority_list_test_2014J.csv') for i in [0,5,150,210,300,380]: print(L.loc[i,['code_module','id_student','risk_score','actual_noncompletion']].tolist(), L.loc[i,'explanation_vi']) print(L.groupby('code_module').agg(…`
21. Read `outputs/oulad-early-warning/q4_top200_precision.png`
22. Read `outputs/oulad-early-warning/q3_model_performance.png`
23. **SKILL `answer-write`**
24. **SKILL `answer-qa`**
25. Write `outputs/oulad-early-warning/answer.md`
26. Bash: `cd outputs/oulad-early-warning && python - <<'E' s=open('answer.md').read() a=s.index('- Mạnh nhất'); b=s.index('- Hầu như không khác') new='''- Mạnh nhất (AUC theo chiều "hoàn thành cao hơn"): số ngày hoạt động 0–28 (0,674), click trang chủ (0,665), số ngày hoạt động tuần 4 (0,656), click tổng 0–2…`
27. Write `outputs/oulad-early-warning/story.md`

> **Kết luận:** Có dự báo được, nhưng chỉ ở mức vừa phải: AUC trên tập test (kỳ 2014J) là 0,71, so với 0,50 nếu đoán theo tỷ lệ nền. Mục tiêu bắt ít nhất 70% sinh viên không hoàn thành đạt được về mặt mô hình, nhưng phải gắn cờ 53% sinh viên và chỉ đúng 50% số đó. Với giới hạn 200 sinh viên mỗi modul…


## Trả lời cuối cùng

**Kết luận:** Có dự báo được, nhưng chỉ ở mức vừa phải: AUC trên tập test (kỳ 2014J) là 0,71, so với 0,50 nếu đoán theo tỷ lệ nền. Mục tiêu bắt ít nhất 70% sinh viên không hoàn thành đạt được về mặt mô hình, nhưng phải gắn cờ 53% sinh viên và chỉ đúng 50% số đó. Với giới hạn 200 sinh viên mỗi module-kỳ thì mục tiêu 70% không đạt được: danh sách top-200 trúng 80,5% (322/400) nhưng chỉ bắt được 23,4% (322/1.376) số sinh viên không hoàn thành. **Q1 – Ba nhóm trong 4 tuần đầu** (n: Pass 7.399, Fail 3.469, Withdrawn 2.152): - Thứ tự Pass > Withdrawn > Fail xuất hiện ở cả 4 tuần, cả click lẫn số ngày vào học. - Click trung vị tuần 1 là 59 (Pass), 33 (Withdrawn) và 20 (Fail). - Nộp TMA1 trước ngày 28: 97% (Pass), 76% (Withdrawn), 75% (Fail). - Nhóm Fail còn ít tương tác hơn cả Withdrawn. **Q2 – Chỉ báo khác biệt và từ tuần nào:** - Mọi chỉ báo hoạt động đều khác biệt có ý nghĩa (p đã hiệu chỉnh Holm < 0,001), và khác biệt đã có từ tuần 1, thậm chí trước ngày 0. Hiệu ứng ở mức nhỏ đến vừa. - Rõ nhất (AUC theo chiều "hoàn thành cao hơn"): số ngày hoạt động 0–28 (0,674), click trang chủ (0,665) và số ngày hoạt động tuần 4 (0,656). - Tuần 2–4 chỉ nhỉnh hơn tuần 1 một chút, và kết quả nhất quán ở cả 8 module-kỳ. - Ngày đăng ký sớm hay muộn hầu như không liên quan (AUC 0,499). **Q3 – Dự báo từ dữ liệu ngày 0–28:** - Tôi dùng đúng cách chia của dữ liệu: train 2013B+2013J, validation 2014B, test 2014J. Mô hình và ngưỡng chọn trên validation, test chỉ dùng một lần. - Mô hình chọn là hồi quy logistic. Trên test nó có recall 70,4% (khoảng tin cậy 95%: 68,0–72,7%), precision 50,1% và AUC 0,713. HistGradientBoosting đạt AUC 0,723 nhưng recall chỉ 66,5% ở cùng cách chọn ngưỡng. - Tôi loại `tma1_score` khỏi mô hình chính vì không rõ điểm được công bố trước ngày 28 chưa. Chạy thử có thêm nó thì kết quả không khá hơn (AUC test 0,665), nên kết luận không đổi. - Kiểm toán theo nhóm nhạy cảm cho thấy recall từ 63% đến 81%. Thấp hơn ở sinh viên có khuyết tật (64%) và tuổi 35–55 (65%). Báo động nhầm ở nữ là 48%, ở nam là 35%. **Q4 – Ưu tiên ai, trúng bao nhiêu:** - Quy tắc: xếp theo điểm rủi ro của mô hình trong từng module-kỳ, lấy 200 người cao nhất. - BBB 2014J trúng 146/200 (73%) và FFF 2014J trúng 176/200 (88%). Cả hai đều cao hơn khoảng 2 lần so với tỷ lệ nền. - Trần bao phủ khi chỉ liên hệ 200 người là 27–32%. Để đạt 70% phải liên hệ 1.032 người ở BBB và 888 ở FFF, tức gấp 4–5 lần năng lực hiện có. - Quy tắc đơn giản "chưa nộp TMA1, rồi ít click nhất" trúng 78,8%, chỉ kém mô hình khoảng 1,7 điểm phần trăm. - Tỷ lệ chuyển đổi 14% là giả định có sẵn trong tham số, chưa kiểm chứng. Theo đó, 322 người trúng tương ứng khoảng 45 sinh viên được hỗ trợ thành công. **Q5 – Yếu tố đóng góp nhiều nhất:** - Với 354/400 sinh viên ưu tiên, yếu tố số một là bài TMA1 (BBB 154, FFF 200). Còn lại là click học liệu (29, đều ở BBB), lịch sử học lại hoặc tải tín chỉ (14) và số ngày vào học (3). - Mỗi sinh viên có một câu diễn đạt riêng cho cố vấn trong cột `explanation_vi`. Ví dụ: *"Sinh v…
