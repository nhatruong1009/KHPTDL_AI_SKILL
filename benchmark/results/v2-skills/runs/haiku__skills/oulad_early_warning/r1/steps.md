# oulad_early_warning · haiku__skills · r1

| | |
|---|---|
| Điểm overall / accuracy / quality | 78.5 / 87.5 / 65.0 |
| Thời gian · chi phí · số turn | 305.1 s · $0.083 · 33 |
| Skill đã nạp (theo thứ tự) | `data-eda` → `data-relevance` → `analysis-plan` |
| Lỗi công cụ | 4 |

## Các bước


> I'll start by loading the EDA skill and looking at what's in `data/`.

1. **SKILL `data-eda`**
2. Bash: `find data -maxdepth 3 | head -100 && du -sh data/* && python -c "import pandas, numpy, scipy, matplotlib, seaborn, sklearn; print('ok')"`

> The EDA skill says to run its inspection script first. I'll run it on `data/`.

3. Bash: `python .claude/skills/data-eda/scripts/inspect_data.py data 2>&1 | head -400; echo ---; cat data/aq4_decision_params.json; echo; for f in data/*.csv; do echo "== $f"; head -3 "$f"; wc -l "$f"; done`  
  ↳ **lỗi:** A variable in this command can't be checked before it runs
4. Bash: `python .claude/skills/data-eda/scripts/inspect_data.py data 2>&1 | head -400`
5. Bash: `cat data/aq4_decision_params.json && ls -la data && wc -l data/*.csv`

> The inspection output was saved to a file. I'll read it.

6. Read `/root/.claude/projects/-root--cache-skill-bench-runs-v2-skills-haiku--skills-oulad-early-warning-r1-workspace/866d1560-147c-4947-858a-5c553417dd40/tool-results/bctmzrwk3.txt`

> The EDA gives me the layout I need. Next I'll run the relevance gate and planning skills before analysis.

7. **SKILL `data-relevance`**
8. **SKILL `analysis-plan`**

> Relevance gate: **Relevant**. All five questions map to columns in the data. Before writing the analysis, I need to check the split design, the week definitions, and whether the TMA fields leak past day 28.

9. Bash: `mkdir -p /root/.cache/skill-bench/runs/v2-skills/haiku__skills/oulad_early_warning/r1/workspace/outputs && cat > /root/.cache/skill-bench/runs/v2-skills/haiku__skills/oulad_early_warning/r1/workspace/outputs/_explore.py <<'EOF' import pandas as pd, numpy as np D = "data/" m = pd.read_csv(D+"aq3_mod…`  
  ↳ **lỗi:** Parser skipped input between top-level statements

> The shell rejected the heredoc. I'll write the exploration script with the Write tool instead.

10. Write `outputs/_explore.py`
11. Bash: `python outputs/_explore.py`

> The split is time-based by module-presentation: 2013B/2013J train, 2014B validation, 2014J test. I'll keep that split. The TMA1 score has no marking date in the data, so it stays out of the main model. The model population is the 13,020 students still enrolled on day 28. Next I'll write the full an…

12. Bash: `mkdir -p outputs/canh-bao-som-oulad && rm -f outputs/_explore.py && ls outputs`
13. Write `outputs/canh-bao-som-oulad/analysis.py`
14. Bash: `python outputs/canh-bao-som-oulad/analysis.py 2>&1 | tail -n 300`

> The script runs end to end. Before writing up, I need to fix three things I can see in the output: - The Q4 chart title says the list catches "about half" of non-completers. The real figure is 322 of 400 on the list (80%), but only 23% of all non-completers. - The Q1 and Q2 chart titles were placeh…

15. Edit `outputs/canh-bao-som-oulad/analysis.py`
16. Edit `outputs/canh-bao-som-oulad/analysis.py`
17. Edit `outputs/canh-bao-som-oulad/analysis.py`
18. Edit `outputs/canh-bao-som-oulad/analysis.py`
19. Bash: `sed -i 's/trung (khong hoan thanh trong danh sach)/so_khong_hoan_thanh_trong_danh_sach/g' outputs/canh-bao-som-oulad/analysis.py && python outputs/canh-bao-som-oulad/analysis.py > outputs/canh-bao-som-oulad/log_chay.txt 2>&1; echo exit=$?; grep -n "Sinh viên 34756" outputs/canh-bao-som-oulad/log_ch…`  
  ↳ **lỗi:** A variable in this command can't be checked before it runs

> The shell rejected that command. I'll make the column-name change with an edit and run the script in a separate call.

20. Edit `outputs/canh-bao-som-oulad/analysis.py`
21. Bash: `python outputs/canh-bao-som-oulad/analysis.py > outputs/canh-bao-som-oulad/log_chay.txt 2>&1; echo exit=$?; ls outputs/canh-bao-som-oulad; cat outputs/canh-bao-som-oulad/q4_tom_tat_trung_danh_sach.csv; echo; head -c 700 outputs/canh-bao-som-oulad/q5_giai_thich_cho_co_van.csv`  
  ↳ **lỗi:** A variable in this command can't be checked before it runs
22. Bash: `python outputs/canh-bao-som-oulad/analysis.py > outputs/canh-bao-som-oulad/log_chay.txt 2>&1; tail -n 3 outputs/canh-bao-som-oulad/log_chay.txt`
23. Read `outputs/canh-bao-som-oulad/q4_tom_tat_trung_danh_sach.csv`
24. Read `outputs/canh-bao-som-oulad/q5_giai_thich_cho_co_van.csv`

> The re-run finished and the Q4 summary and Q5 explanations read correctly. The last check is the group audit of errors, which uses the sensitive attributes only for auditing. I'll read it, then write the answer.

25. Read `outputs/canh-bao-som-oulad/q3_kiem_toan_theo_nhom_khong_dung_lam_bien.csv`

> The audit shows the fixed-threshold recall is uneven across groups, so I'll report that as a caveat. Now I'll write the answer and the story.

26. Write `outputs/canh-bao-som-oulad/answer.md`
27. Write `outputs/canh-bao-som-oulad/story.md`

> Before the final reply, I'll tighten one overstated sentence in the answer (the pairwise test covered four indicators, not all) and confirm the output files exist.

28. Edit `outputs/canh-bao-som-oulad/answer.md`
29. Bash: `ls outputs/canh-bao-som-oulad`

> Mô hình 28 ngày đầu phân biệt được sinh viên không hoàn thành ở mức trung bình (AUC 0.72 trên test 2014J). Mục tiêu bắt ít nhất 70% **không đạt** với ngưỡng cố định (64%); chỉ đạt khi cảnh báo khoảng 54% sinh viên. Danh sách 200 suất mỗi module-kỳ có 80% trúng, nhưng chỉ bắt được 23% tổng số không …


## Trả lời cuối cùng

Mô hình 28 ngày đầu phân biệt được sinh viên không hoàn thành ở mức trung bình (AUC 0.72 trên test 2014J). Mục tiêu bắt ít nhất 70% **không đạt** với ngưỡng cố định (64%); chỉ đạt khi cảnh báo khoảng 54% sinh viên. Danh sách 200 suất mỗi module-kỳ có 80% trúng, nhưng chỉ bắt được 23% tổng số không hoàn thành. **1. Tương tác 4 tuần đầu:** Pass cao nhất, Withdrawn ở giữa, Fail thấp nhất. Trung vị lượt truy cập tuần 1 là 59 (Pass), 33 (Withdrawn), 20 (Fail). Khoảng cách vẫn còn ở tuần 4 (43, 21, 10). **2. Chỉ báo khác biệt có ý nghĩa:** hầu hết chỉ báo được kiểm định đều có ý nghĩa sau hiệu chỉnh Holm; ngoại trừ `registration_lead_days`. Mạnh nhất là số ngày hoạt động và lượt truy cập trong 28 ngày đầu, và việc nộp TMA1 (97% so với 76%). Khác biệt đã có **ngay từ tuần 1** và kéo dài đến tuần 4; không tăng dần theo tuần. **3. Dự báo chỉ từ ngày 0–28:** - Mô hình chính là hồi quy logistic, AUC test 0.716. Baseline chỉ dùng lượt truy cập tổng: 0.652. - Ngưỡng chốt trên validation cho recall 64% trên test (chưa đạt), cảnh báo 45% sinh viên. - Đặt cùng tỷ lệ cảnh báo 54% lên test cho recall 72% (đạt), precision 51%. **4. Ưu tiên với 200 suất mỗi module-kỳ:** xếp theo xác suất không hoàn thành ước tính, lấy 200 đầu tiên trong mỗi module-kỳ. Trên test: BBB-2014J trúng 149/200, FFF-2014J trúng 173/200; tổng 322/400 (80%). Trần recall lý thuyết dưới giới hạn này là 29%, nên mục tiêu 70% không thể đạt. Với 300 suất mỗi module-kỳ, recall đạt 32%. **5. Đặc trưng đóng góp chính:** tổng lượt truy cập 28 ngày đầu là yếu tố hàng đầu của 268/400 sinh viên. Mỗi sinh viên có một đoạn 2–3 câu cho cố vấn trong `q5_giai_thich_cho_co_van.csv`. **Lựa chọn của tôi (không có người hỏi lại):** - Dùng tách theo thời gian có sẵn trong dữ liệu: train = 2013B/2013J, validation = 2014B, test = 2014J. - Không đưa vào mô hình: `tma1_score` (không rõ ngày chấm, nên chỉ báo cáo như nhạy cảm; AUC giảm xuống 0.667), thuộc tính nhân khẩu học và trình độ học vấn (chỉ dùng để kiểm toán). Recall theo nhóm chênh lệch đáng kể, ví dụ IMD 10–20% chỉ 58%, IMD không rõ 76%. - Quần thể là 13,020 lượt còn học đến ngày 28; 2,644 lượt đã rút trước ngày 28 bị loại theo đề bài. - Không dùng `assumed_conversion_rate` 0.14 vì nguồn không có trong dữ liệu. **Hạn chế:** đây là tương quan trong dữ liệu quan sát, không phải nguyên nhân. Tỷ lệ không hoàn thành khác nhau giữa các kỳ (test 38%, validation 47%), nên cần chốt lại ngưỡng trước khi dùng cho kỳ mới. Kết quả nằm trong `outputs/canh-bao-som-oulad/`: `answer.md`, `story.md`, `analysis.py`, các bảng `q1`–`q5` (CSV), bốn biểu đồ PNG, và `log_chay.txt`.

## Tiêu chí bị trượt (giám khảo)

- AQ5: giải thích từng sinh viên dựa trên đóng góp thực của mô hình, không dùng thuộc tính nhạy cảm, lý do chính hợp lý  
  ↳ Lỗi chỉ số: lst_idx lấy từ te_df (2014J) nhưng m.loc[idx] và X.loc[idx] lại trả về dòng của 2013B. Cả 400 dòng trong q5_giai_thich_cho_co_van.csv đều là BBB 2013B, không có dòng nào thuộc 2014J. Ví dụ sinh viên 34756 'BBB 2013B' không có trong danh sách ưu tiên. Vì vậy con số 268/400 và giá trị đặc trưng đều thuộc sai sinh viên.
