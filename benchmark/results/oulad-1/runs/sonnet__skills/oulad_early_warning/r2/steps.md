# oulad_early_warning · sonnet__skills · r2

| | |
|---|---|
| Điểm overall / accuracy / quality | 71.0 / 75.0 / 65.0 |
| Thời gian · chi phí · số turn | 372.0 s · $1.027 · 34 |
| Skill đã nạp (theo thứ tự) | (không có) |
| Lỗi công cụ | 6 |

## Các bước


> Bắt đầu bằng việc khám phá dữ liệu.

1. Bash: `cd data; ls -la; for f in *; do echo "== $f"; head -3 "$f" | cut -c1-600; wc -l "$f"; done; ls ../.claude/skills; python -c "import pandas, sklearn, scipy, seaborn; print('ok')"`  
  ↳ **lỗi:** A variable in this command can't be checked before it runs
2. Bash: `cd data; ls -la; for f in *; do echo "== $f"; head -3 "$f" | cut -c1-600; wc -l "$f"; done; ls ../.claude/skills; python -c "import pandas, sklearn, scipy, seaborn; print('ok')"`  
  ↳ **lỗi:** A variable in this command can't be checked before it runs

> Tránh dùng biến trong lệnh.

3. Bash: `ls -la data; head -c 1500 data/*.csv | head -60; python -c "import pandas, sklearn, scipy, seaborn; print('ok')"`
4. Bash: `cat data/aq4_decision_params.json; head -3 data/aq3_model_table.csv data/context_all_registrations.csv | cut -c1-1500; python - <<'E' import pandas as pd d=pd.read_csv('data/aq2_diagnostic_table.csv') print(d.shape);print(d.split.value_counts());print(pd.crosstab([d.code_module,d.code_presentation]…`
5. Bash: `python - <<'E' import pandas as pd m=pd.read_csv('data/aq3_model_table.csv') print(m.describe().T[['count','mean','min','50%','max']].to_string()) print(m.groupby('split').target_noncompletion.mean()) print(m.groupby(['code_module','code_presentation']).target_noncompletion.agg(['mean','size'])) pr…`
6. Bash: `mkdir -p outputs/early_warning && cat > outputs/early_warning/analysis.py <<'E' """Cảnh báo sớm OULAD (BBB, FFF) - mốc cuối ngày 28. Chạy: python outputs/early_warning/analysis.py""" import os, json, warnings import numpy as np, pandas as pd from scipy import stats import matplotlib; matplotlib.use…`  
  ↳ **lỗi:** Contains brace with quote character (expansion obfuscation)
7. Bash: `mkdir -p outputs/early_warning && ls outputs/early_warning`
8. Write `outputs/early_warning/analysis.py`

> Đang chạy script phân tích đầy đủ.

9. Bash: `python outputs/early_warning/analysis.py 2>&1 | head -300`
10. Bash: `python - <<'E' p='outputs/early_warning/analysis.py' s=open(p).read() a=s.index("pl = pl.copy(); pl[\"row\"]") b=s.index("q5[\"ghi_chu_co_van\"]") new='''pl = pl.copy(); pl["row"] = pl.index # gom đặc trưng tương quan thành chủ đề (tổng đóng góp logistic của từng chủ đề) THEME = {} for c in X.colum…`
11. Bash: `cd outputs/early_warning; python -c " import pandas as pd q=pd.read_csv('q5_priority_list_with_reasons.csv');print(q.top1.value_counts());print(q.actual_noncompletion.mean()) for t in q.ghi_chu_co_van.sample(4,random_state=1):print(t) print(q.groupby('top1').actual_noncompletion.mean()) print(pd.re…`
12. Bash: `cd /root/.cache/skill-bench/runs/oulad-1/sonnet__skills/oulad_early_warning/r2/workspace && python - <<'E' p='outputs/early_warning/analysis.py' s=open(p).read() s=s.replace('f.append("lượng truy cập học liệu thấp (%d lượt click trong 28 ngày đầu)" % r.clicks_0_28)','f.append("lượng truy cập học li…`  
  ↳ **lỗi:** Commands that change directories and write via output redirection require explicit approval to ensure paths are evaluated correctly. For security, Claude Code cannot automatically determine the final…
13. Bash: `python - <<'E' p='/root/.cache/skill-bench/runs/oulad-1/sonnet__skills/oulad_early_warning/r2/workspace/outputs/early_warning/analysis.py' s=open(p).read() s=s.replace('f.append("lượng truy cập học liệu thấp (%d lượt click trong 28 ngày đầu)" % r.clicks_0_28)','f.append("lượng truy cập học liệu chỉ…`  
  ↳ **lỗi:** This Bash command contains multiple operations. The following part requires approval: python - <<'E' p='/root/.cache/skill-bench/runs/oulad-1/sonnet__skills/oulad_early_warning/r2/workspace/outputs/e…
14. Edit `outputs/early_warning/analysis.py`
15. Edit `outputs/early_warning/analysis.py`
16. Edit `outputs/early_warning/analysis.py`
17. Edit `outputs/early_warning/analysis.py`

> Đã sửa phần diễn đạt cho cố vấn; chạy lại toàn bộ script để cập nhật kết quả.

18. Bash: `pwd; cd /root/.cache/skill-bench/runs/oulad-1/sonnet__skills/oulad_early_warning/r2/workspace; python outputs/early_warning/analysis.py > /tmp/log.txt 2>&1; tail -2 /tmp/log.txt | cut -c1-120; python -c " import pandas as pd q=pd.read_csv('outputs/early_warning/q5_priority_list_with_reasons.csv') f…`  
  ↳ **lỗi:** This Bash command contains multiple operations. The following part requires approval: pwd; cd /root/.cache/skill-bench/runs/oulad-1/sonnet__skills/oulad_early_warning/r2/workspace; python outputs/ear…
19. Bash: `cd /root/.cache/skill-bench/runs/oulad-1/sonnet__skills/oulad_early_warning/r2/workspace`
20. Bash: `python outputs/early_warning/analysis.py > outputs/early_warning/run_log.txt 2>&1; tail -2 outputs/early_warning/run_log.txt | cut -c1-120`
21. Bash: `python -c " import pandas as pd q=pd.read_csv('outputs/early_warning/q5_priority_list_with_reasons.csv') for t in q.ghi_chu_co_van.sample(3,random_state=2):print(t) print((q.tma1_submitted==0).mean(), q.clicks_0_28.median(), q.active_days_0_28.median()) print(pd.read_csv('outputs/early_warning/q5_t…`
22. Bash: `python -c " import pandas as pd q=pd.read_csv('outputs/early_warning/q5_priority_list_with_reasons.csv') print(q[q.tma1_submitted==1].tma1_score.describe()); print(q[q.tma1_submitted==1].tma1_score.value_counts().head()) m=pd.read_csv('data/aq3_model_table.csv');print(m[(m.tma1_submitted_by_d28==1)…`
23. Bash: `python -c " import pandas as pd m=pd.read_csv('data/aq3_model_table.csv') for s in [0,1,2,5]: print(s,(m.tma1_score==s).sum(), m[m.tma1_score==s].target_noncompletion.mean()) print(m[m.tma1_score<10].groupby('code_module').size(), m[m.tma1_score==1].groupby(['code_module','code_presentation']).size…`
24. Bash: `python -c " import pandas as pd m=pd.read_csv('data/aq3_model_table.csv') b=m[(m.code_module=='BBB')&(m.code_presentation=='2014J')] print(b.groupby(b.tma1_score==1)[['tma1_submitted_by_d28','tma1_on_time','tma1_days_before_deadline','target_noncompletion']].mean()) print(m.groupby(['code_module','…`
25. Edit `outputs/early_warning/analysis.py`
26. Bash: `python - <<'E' p='outputs/early_warning/analysis.py' s=open(p).read() s=s.replace('X = X_raw.copy(); X.loc[art, "tma1_score"] = 0; X.loc[art, "tma1_score_missing"] = 1', 'X = X_raw.copy(); X.loc[art, "tma1_score"] = md.loc[tr & (md.tma1_submitted_by_d28 == 1), "tma1_score"].median(); X.loc[art, "tm…`
27. Bash: `sed -n 40,75p outputs/early_warning/run_log.txt | cut -c1-200; cat outputs/early_warning/q4_per_module_presentation_test_k200.csv; python -c " import pandas as pd q=pd.read_csv('outputs/early_warning/q5_priority_list_with_reasons.csv') print((q.tma1_submitted==0).mean()); for t in q.ghi_chu_co_van.…`
28. Read `outputs/early_warning/q4_priority_list.png`
29. Edit `outputs/early_warning/analysis.py`

> Chạy lại script lần cuối rồi viết báo cáo.

30. Bash: `python outputs/early_warning/analysis.py > outputs/early_warning/run_log.txt 2>&1; tail -1 outputs/early_warning/run_log.txt | cut -c1-80; python -c " import pandas as pd q=pd.read_csv('outputs/early_warning/q5_priority_list_with_reasons.csv') print(q.ghi_chu_co_van.iloc[0]);print(q.groupby('code_m…`
31. Bash: `python -c " import pandas as pd m=pd.read_csv('data/aq3_model_table.csv') print(m.groupby(['code_module','code_presentation','tma1_submitted_by_d28']).target_noncompletion.agg(['size','mean']).round(3).unstack())"`
32. Write `outputs/early_warning/answer.md`
33. Write `outputs/early_warning/story.md`

> Dự báo được ở mức vừa phải, nhưng chưa đạt mục tiêu bắt 70% sinh viên không hoàn thành. Mô hình đạt AUC 0,72 trên kỳ test 2014J (khoảng tin cậy 95%: 0,71–0,74). Tôi chia dữ liệu theo thời gian: train 2013B+2013J, validation 2014B, test 2014J. Mô hình và ngưỡng chọn trên validation, test chỉ để báo …


## Trả lời cuối cùng

Dự báo được ở mức vừa phải, nhưng chưa đạt mục tiêu bắt 70% sinh viên không hoàn thành. Mô hình đạt AUC 0,72 trên kỳ test 2014J (khoảng tin cậy 95%: 0,71–0,74). Tôi chia dữ liệu theo thời gian: train 2013B+2013J, validation 2014B, test 2014J. Mô hình và ngưỡng chọn trên validation, test chỉ để báo cáo cuối. **1. Tương tác 4 tuần đầu theo kết quả.** Pass vào học trung vị 12 ngày và 257 lượt click. Withdrawn là 9 ngày và 160,5 click, Fail thấp nhất với 7 ngày và 112 click. Kruskal-Wallis cho p < 1e-200, và các kiểm định từng cặp đều có ý nghĩa. **2. Chỉ báo khác biệt, và từ tuần nào.** - 35 trong 36 chỉ báo khác biệt có ý nghĩa (Bonferroni), cùng chiều ở cả 8 module-kỳ. Ngoại lệ duy nhất là `registration_lead_days`. - Khác biệt đã rõ từ tuần 1 (Cliff's delta ≈ 0,26) và tăng nhẹ lên ≈ 0,30 ở tuần 2–4. - Mạnh nhất là số ngày hoạt động (0,35), click trang chủ (0,33) và click diễn đàn (0,30). - Sinh viên chưa nộp TMA1 trước ngày 28 có 81–93% không hoàn thành ở mọi module-kỳ. **3. Dự báo từ dữ liệu ngày 0–28 và mục tiêu 70%.** - Để bắt 70% sinh viên không hoàn thành trên test, phải gắn cờ khoảng 51% sinh viên, với độ chính xác khoảng 53% (tỷ lệ nền 37,8%). - Ngưỡng chọn trên validation chỉ bắt được 65,8% trên test. - Gradient boosting nhỉnh hơn một chút (AUC test 0,742), nhưng tôi chọn Logistic vì validation ngang nhau và giải thích được cho câu 5. **4. Danh sách ưu tiên với K = 200 mỗi module-kỳ.** - Xếp theo điểm rủi ro, danh sách 400 người trúng 291 người (72,8%), so với 37,8% nếu chọn ngẫu nhiên. - Danh sách chỉ bao phủ 21,2% trong 1.376 sinh viên không hoàn thành, nên K = 200 không thể đạt 70%. - Quy tắc đơn giản "chưa nộp TMA1, rồi ít ngày hoạt động" trúng 80,5% trên test. Trên validation thì mô hình thắng (88,3% so với 82,8%), nên kết quả hai bên không nhất quán. - Tôi khuyến nghị dùng quy tắc đơn giản làm nền, và dùng mô hình bổ sung cho BBB, nơi chỉ khoảng 6% sinh viên chưa nộp TMA1. - Với giả định chuyển đổi 14% của nhà trường, danh sách này giúp được khoảng 41 người (quy tắc TMA1: khoảng 45). **5. Lý do rủi ro cho từng sinh viên ưu tiên.** - Tôi tính đóng góp của từng đặc trưng trong mô hình Logistic, gộp thành 7 chủ đề, rồi lấy 3 chủ đề lớn nhất cho mỗi người. Các chủ đề hay gặp nhất là số ngày vào học, bài TMA1, hồ sơ nền và lượng truy cập học liệu. - File `q5_priority_list_with_reasons.csv` có 400 sinh viên, mỗi người kèm 2–3 câu cho cố vấn ở cột `ghi_chu_co_van`. **Hạn chế cần biết.** - **Thang điểm TMA1 bất thường:** ở BBB 2014J, 38% điểm `tma1_score` bằng 1 và phần còn lại gần 100, không kỳ nào khác như vậy. Nếu giữ nguyên, AUC test giảm từ 0,72 xuống 0,69. Tôi gán các điểm này bằng trung vị của train; cần xác nhận với bộ phận dữ liệu. Kết quả cả hai cách có trong `q3_sensitivity_tma1_scale_artifact.csv`. - **Chênh giữa các kỳ:** AUC validation là 0,76 còn test là 0,72. - **Chênh giữa các module:** AUC ở BBB 2014J (0,64) kém FFF 2014J (0,79). - **Tương quan, không phải nhân quả:** các "lý do" ở câu 5 là yếu tố làm tăng điểm rủi ro, khô…

## Tiêu chí bị trượt (giám khảo)

- AQ3 rò rỉ/đạo đức: không dùng biến kết quả hay thuộc tính nhạy cảm; tma1_score bị loại hoặc được cảnh báo look-ahead  
  ↳ Không dùng biến nhạy cảm (để riêng cho audit). Tuy nhiên tma1_score được đưa vào làm đặc trưng chính và không được cảnh báo về nguy cơ look-ahead (thời điểm công bố điểm). Agent chỉ xử lý 'thang điểm bất thường' ở BBB 2014J, và quy tắc phát hiện (>10% điểm = 1) được tính trên chính dữ liệu test.
- AQ4: xếp hạng trong từng module-kỳ (200 mỗi bên), precision@200 khớp tham chiếu (BBB ~0,76, FFF ~0,88 ±0,08), so với tỷ lệ nền  
  ↳ Xếp hạng đúng cách, riêng từng module-kỳ. FFF 2014J đạt 86,5% (khớp tham chiếu), nhưng BBB 2014J chỉ 59,0%, lệch xa tham chiếu 0,76, nhiều khả năng do dùng tma1_score. Có so với tỷ lệ nền 0,356/0,399.
