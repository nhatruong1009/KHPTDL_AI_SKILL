# bank_marketing · haiku__skills · r1

| | |
|---|---|
| Điểm overall / accuracy / quality | 78.0 / 83.3 / 70.0 |
| Thời gian · chi phí · số turn | 353.2 s · $0.077 · 36 |
| Skill đã nạp (theo thứ tự) | `data-eda` → `answer-write` → `answer-qa` |
| Lỗi công cụ | 5 |

## Các bước

1. **SKILL `data-eda`**
2. Bash: `find data -type f | head -50 && echo --- && ls -la data && python -c "import pandas, numpy, scipy, matplotlib, seaborn, sklearn; print('ok', sklearn.__version__)"`
3. Bash: `python .claude/skills/data-eda/scripts/inspect_data.py data/ 2>&1 | head -150; echo ---; cat data/bank-names.txt | head -80; echo ---; cat data/bank-additional/bank-additional-names.txt | head -80; echo ---; wc -l data/*.csv data/bank-additional/*.csv; head -3 data/bank-additional/bank-additional-f…`
4. Bash: `mkdir -p /root/.cache/skill-bench/runs/v2-skills/haiku__skills/bank_marketing/r1/workspace/outputs/priority_call_term_deposit && cd /root/.cache/skill-bench/runs/v2-skills/haiku__skills/bank_marketing/r1/workspace && python - <<'EOF' import pandas as pd a=pd.read_csv("data/bank-additional/bank-addi…`
5. Write `outputs/priority_call_term_deposit/analysis.py`
6. Bash: `time python outputs/priority_call_term_deposit/analysis.py 2>&1 | tail -150`
7. Bash: `python - <<'EOF' 2>&1 | grep -v Warn import warnings; warnings.filterwarnings("ignore") import pandas as pd, numpy as np from sklearn.metrics import roc_auc_score exec(open("outputs/priority_call_term_deposit/analysis.py").read().split("# ------------------------------------------------------------…`  
  ↳ **lỗi:** Contains brace with quote character (expansion obfuscation)
8. Write `outputs/priority_call_term_deposit/_diag.py`
9. Bash: `python outputs/priority_call_term_deposit/_diag.py 2>&1 | tail -80`

> The time-based holdout shows strong drift: the subscription rate climbs from about 3% in the earliest rows to about 46% in the last 10%, and the macro indicators move with time. Before finalizing, I'll fix two things in the script: the sensitivity and robustness runs used GBM while the headline mod…

10. Write `outputs/priority_call_term_deposit/analysis.py`
11. Bash: `rm -f outputs/priority_call_term_deposit/_diag.py && python outputs/priority_call_term_deposit/analysis.py 2>&1 | tail -160`

> The results are now consistent across the headline and the sensitivity runs. Next I'll load the answer and QA skills and confirm the output files.

12. **SKILL `answer-write`**
13. **SKILL `answer-qa`**
14. Bash: `cd /root/.cache/skill-bench/runs/v2-skills/haiku__skills/bank_marketing/r1/workspace/outputs/priority_call_term_deposit && ls -la && cat chenh_lech_auc_bootstrap.csv`
15. Read `outputs/priority_call_term_deposit/bieu_do_1_duong_tich_luy.png`
16. Read `outputs/priority_call_term_deposit/bieu_do_2_yeu_to_quan_trong.png`
17. Read `outputs/priority_call_term_deposit/bieu_do_3_do_nhay.png`

> QA on the charts found three problems: chart 1 and chart 2 titles are cut off, and chart 3's bars start at 0.5 instead of 0. I'll fix these and rerun.

18. Bash: `python - <<'EOF' from pathlib import Path p=Path("analysis.py"); s=p.read_text() reps={ 'ax.set_title(f"Trên giai đoạn test cuối, gọi 20% đầu danh sách bắt {r20_m:.0%} người đăng ký; baseline bắt {r20_b:.0%}",\n loc="left", fontsize=11)': 'ax.set_title(f"Test cuối: gọi 20% đầu danh sách bắt {r20_m:…`  
  ↳ **lỗi:** Contains brace with quote character (expansion obfuscation)
19. Edit `outputs/priority_call_term_deposit/analysis.py`
20. Edit `outputs/priority_call_term_deposit/analysis.py`
21. Edit `outputs/priority_call_term_deposit/analysis.py`
22. Edit `outputs/priority_call_term_deposit/analysis.py`
23. Bash: `cd /root/.cache/skill-bench/runs/v2-skills/haiku__skills/bank_marketing/r1/workspace && python outputs/priority_call_term_deposit/analysis.py > outputs/priority_call_term_deposit/run_log.txt 2>&1; echo exit=$?; grep -A7 "Test:" outputs/priority_call_term_deposit/run_log.txt | head -8`  
  ↳ **lỗi:** A variable in this command can't be checked before it runs
24. Bash: `cd /root/.cache/skill-bench/runs/v2-skills/haiku__skills/bank_marketing/r1/workspace && python outputs/priority_call_term_deposit/analysis.py > outputs/priority_call_term_deposit/run_log.txt 2>&1; echo exit=$?; grep -A7 "Test:" outputs/priority_call_term_deposit/run_log.txt | head -8`  
  ↳ **lỗi:** A variable in this command can't be checked before it runs
25. Bash: `cd /root/.cache/skill-bench/runs/v2-skills/haiku__skills/bank_marketing/r1/workspace && python outputs/priority_call_term_deposit/analysis.py > outputs/priority_call_term_deposit/run_log.txt 2>&1 && grep -A7 "Test:" outputs/priority_call_term_deposit/run_log.txt | head -8`  
  ↳ **lỗi:** Commands that change directories and write via output redirection require explicit approval to ensure paths are evaluated correctly. For security, Claude Code cannot automatically determine the final…
26. Bash: `python /root/.cache/skill-bench/runs/v2-skills/haiku__skills/bank_marketing/r1/workspace/outputs/priority_call_term_deposit/analysis.py > /root/.cache/skill-bench/runs/v2-skills/haiku__skills/bank_marketing/r1/workspace/outputs/priority_call_term_deposit/run_log.txt 2>&1`
27. Read `outputs/priority_call_term_deposit/run_log.txt`
28. Read `outputs/priority_call_term_deposit/bieu_do_1_duong_tich_luy.png`
29. Read `outputs/priority_call_term_deposit/bieu_do_5_troi_dat.png`

> Charts now render with complete titles, and the run log matches the numbers above. Next I'll write `answer.md` and `story.md`.

30. Write `outputs/priority_call_term_deposit/answer.md`
31. Write `outputs/priority_call_term_deposit/story.md`
32. Edit `outputs/priority_call_term_deposit/answer.md`

> **Trả lời ngắn:** Mô hình chưa chứng minh được là tốt hơn baseline đơn giản. Trên validation, mô hình vượt baseline (AUC 0,660 so với 0,484). Nhưng trên giai đoạn test cuối (15% dữ liệu theo thời gian), mô hình kém baseline "chỉ dùng poutcome": AUC 0,578 so với 0,621 (chênh lệch −0,043, khoảng tin …


## Trả lời cuối cùng

**Trả lời ngắn:** Mô hình chưa chứng minh được là tốt hơn baseline đơn giản. Trên validation, mô hình vượt baseline (AUC 0,660 so với 0,484). Nhưng trên giai đoạn test cuối (15% dữ liệu theo thời gian), mô hình kém baseline "chỉ dùng poutcome": AUC 0,578 so với 0,621 (chênh lệch −0,043, khoảng tin cậy 95% từ −0,067 đến −0,022). Khi gọi 20% danh sách đầu, mô hình bắt được 25% người đăng ký, baseline bắt được 35%. **Yếu tố quan trọng nhất** (giảm AUC khi xáo trộn biến trên test): `nr.employed` (0,085), `pdays` (0,047), `month` (0,042), `poutcome` (0,030), `emp.var.rate` (0,026). Đặc điểm khách hàng như nghề nghiệp, học vấn, vay nhà, vay tiêu dùng, nợ xấu gần như không đóng góp. Các biến kinh tế và thời điểm này là tín hiệu theo thời gian, không ổn định. **Bằng chứng chính:** - Tỷ lệ đăng ký tăng từ 3% lên 46% qua thời gian. Train 5,6%, test 38,5%. Test rơi vào giai đoạn chưa có trong train, nên đây là ngoại suy. - Khách thành công ở chiến dịch trước đăng ký 65%, thất bại 14%, chưa từng gọi 9%. - Bỏ chỉ số kinh tế: AUC 0,605, vẫn dưới baseline. Thêm `duration` (rò rỉ): AUC 0,652, không dùng được. - Trên bank-full.csv: AUC 0,647 so với baseline 0,633, nhưng recall trong 20% đầu 27,6% so với 34,0%. Kết quả lẫn lộn. **Phương pháp:** - Dữ liệu chính: `bank-additional-full.csv` (41.188 dòng), vì có đủ nhất thông tin. Giữ 12 dòng trùng lặp vì không có khóa khách hàng. - Loại `duration` và `campaign` khỏi mô hình chính theo kiểm tra thời điểm. Chỉ số kinh tế được giữ vì đã biết tại thời điểm gọi, nhưng là biến thời gian. - Chia theo thời gian 70/15/15. Chọn mô hình trên validation (Logistic có macro), test chạm một lần. - Loại `age` và `marital` khỏi đầu vào. Kiểm tra theo nhóm tuổi chỉ để audit: AUC trong nhóm 60+ là 0,47. - Câu hỏi không nêu mục tiêu hay hạn mức. Tôi giả định đơn vị lập kế hoạch là 20% danh sách đầu. **Gợi ý (không phải kết luận từ dữ liệu):** Không nên dùng mô hình này làm quy tắc ưu tiên gọi điện. Ưu tiên khách có kết quả thành công ở chiến dịch trước là lựa chọn đơn giản hơn và tốt hơn trên giai đoạn test. Nếu muốn mô hình, cần huấn luyện lại trên dữ liệu gần nhất và theo dõi tỷ lệ đăng ký theo tháng. **Giả định và hạn chế:** Dữ liệu 2008–2010 của một ngân hàng Bồ Đào Nha, có thể không đại diện hiện tại. Kết quả là liên quan, không phải nhân quả. Chỉ số kinh tế cần giá trị hiện tại hoặc dự báo khi dùng cho chiến dịch thật. **Kiểm tra QA (answer-qa):** | Kiểm tra | Kết quả | Ghi chú/sửa | |---|---|---| | Trả lời đúng câu hỏi | Đạt | Có nêu rõ giả định 20% danh sách; không có mục tiêu nào trong câu hỏi | | Số liệu truy vết được | Đạt | Mọi số lấy từ `run_log.txt` và CSV, đã chạy lại script | | Mẫu, tỷ lệ, chia dữ liệu | Đạt | n validation 6.178, n test 6.179 | | Thời điểm đặc trưng, nhạy cảm | Đạt | Loại duration, campaign; age/marital không làm đầu vào | | Kết quả độ nhạy phản ánh vào kết luận | Đạt | Kết luận chính là "không vượt baseline" khớp với tất cả kịch bản | | Biểu đồ: tiêu đề nêu kết quả, trục | Đã sửa | Tiêu đề biểu đồ 1, 2…

## Tiêu chí bị trượt (giám khảo)

- 2. Loại duration vì rò rỉ, ROC-AUC trong khoảng thực tế (~0,75-0,82)  
  ↳ Có loại duration và nêu lý do 'chỉ biết sau cuộc gọi' (thêm vào thì AUC 0,652). Nhưng AUC test chính chỉ 0,578 (validation 0,660), thấp hơn nhiều so với khoảng tham chiếu 0,79 (chia ngẫu nhiên) và cả ~0,70-0,715 (chia theo thời gian 25% cuối). Nguyên nhân chính: chia 70/15/15 và không huấn luyện lại trên train+validation trước khi chạy test.
