# oulad_early_warning · haiku__skills · r1

| | |
|---|---|
| Điểm overall / accuracy / quality | 69.0 / 75.0 / 60.0 |
| Thời gian · chi phí · số turn | 341.9 s · $0.168 · 36 |
| Skill đã nạp (theo thứ tự) | (không có) |
| Lỗi công cụ | 6 |

## Các bước


> Bắt đầu bằng việc khám phá dữ liệu.

1. Bash: `ls -la && find data -maxdepth 3 | head -100 && python -c "import pandas, numpy, scipy, matplotlib, seaborn, sklearn; print('ok')"`
2. Bash: `cd /root/.cache/skill-bench/runs/oulad-1/haiku__skills/oulad_early_warning/r1/workspace/data && wc -l *.csv && for f in *.csv; do echo "== $f"; head -3 "$f"; done && echo && cat aq4_decision_params.json`  
  ↳ **lỗi:** A variable in this command can't be checked before it runs
3. Bash: `cd /root/.cache/skill-bench/runs/oulad-1/haiku__skills/oulad_early_warning/r1/workspace/data && wc -l *.csv; for f in *.csv; do echo "== $f"; head -3 "$f"; done; echo; cat aq4_decision_params.json`  
  ↳ **lỗi:** A variable in this command can't be checked before it runs
4. Bash: `cd /root/.cache/skill-bench/runs/oulad-1/haiku__skills/oulad_early_warning/r1/workspace/data && wc -l aq1_student_week.csv aq2_diagnostic_table.csv aq3_audit_attributes.csv aq3_model_table.csv context_all_registrations.csv && head -3 aq1_student_week.csv && head -3 aq2_diagnostic_table.csv && head …`

> Dữ liệu đã được chuẩn bị sẵn. Tôi kiểm tra cấu trúc, khóa, nhãn, và phân chia train/test trước khi phân tích.

5. Bash: `mkdir -p /root/.cache/skill-bench/runs/oulad-1/haiku__skills/oulad_early_warning/r1/workspace/outputs/scratch && cat > /root/.cache/skill-bench/runs/oulad-1/haiku__skills/oulad_early_warning/r1/workspace/outputs/scratch/eda.py <<'EOF' import pandas as pd, numpy as np D = "data/" aq1 = pd.read_csv(D…`  
  ↳ **lỗi:** Parser skipped input between top-level statements
6. Write `outputs/scratch/eda.py`
7. Bash: `cd /root/.cache/skill-bench/runs/oulad-1/haiku__skills/oulad_early_warning/r1/workspace && python -I outputs/scratch/eda.py`  
  ↳ **lỗi:** Exit code 1 == aq1 (52080, 9) dup keys: 0 == aq2 (13020, 45) dup keys: 0 == aq3a (13020, 13) dup keys: 0 == aq3m (13020, 41) dup keys: 0 == ctx (15671, 12) dup keys: 0 split train 6795 test 3644 vali…
8. Bash: `cd /root/.cache/skill-bench/runs/oulad-1/haiku__skills/oulad_early_warning/r1/workspace && python -I -c " import pandas as pd D='data/' aq2=pd.read_csv(D+'aq2_diagnostic_table.csv'); aq3m=pd.read_csv(D+'aq3_model_table.csv'); aq3a=pd.read_csv(D+'aq3_audit_attributes.csv'); ctx=pd.read_csv(D+'contex…`

> Nhãn `label3` nằm ở `aq2`, còn `aq3_model_table` chỉ có `target_noncompletion`. Hai bảng khớp 100% về phân chia và nhãn; 13.020 sinh viên là toàn bộ người còn học tại ngày 28. Tiếp theo kiểm tra quy ước tuần và rò rỉ nhãn trong các đặc trưng.

9. Write `outputs/scratch/check.py`
10. Bash: `python -I outputs/scratch/check.py 2>&1; python -I -c "import shap" 2>&1 | tail -1`

> Không có đặc trưng nào để lộ nhãn (AUC đơn biến cao nhất khoảng 0,67, và đó là các đặc trưng hoạt động). Quy ước tuần: tuần k = ngày 7(k-1) đến 7k-1; `clicks_0_28` gồm cả ngày 28. Tôi viết script phân tích chính và chạy.

11. Write `outputs/canh_bao_som_d28/analysis.py`
12. Bash: `python -I outputs/canh_bao_som_d28/analysis.py 2>&1 | head -c 16000`
13. Bash: `python - <<'PY' import re p="outputs/canh_bao_som_d28/analysis.py" s=open(p,encoding="utf-8").read() s=s.replace('RES["n_by_mp"] = df.groupby(MODULE_PRES).size().rename(lambda x: str(x)).to_dict()', 'RES["n_by_mp"] = {f"{a} {b}": int(n) for (a, b), n in df.groupby(MODULE_PRES).size().items()}') s=s…`

> Mô hình đã chạy xong. Trước khi diễn giải, tôi cần xem phần còn lại và kiểm tra một điểm bất thường: AUC validation (0,755) cao hơn đáng kể so với test (0,685).

14. Bash: `python -I - <<'PY' import json, pandas as pd, numpy as np R=json.load(open("outputs/canh_bao_som_d28/results.json",encoding="utf-8")) print(R["q4_total"]); print(R["q5_top1"]); print(R["q5_top1_by_group"]); print(R["q5_sample"]); print(R["q5_top1_fail_rate"]); print(R["coef_top"]); print("corr",R["…`

> Hai phát hiện quan trọng: 1. **Chia tập theo kỳ, không ngẫu nhiên**: train = 2013B/2013J, validation = 2014B, test = 2014J. Test là bài kiểm tra "sang kỳ mới" (out-of-time), nên AUC giảm là điều dự kiến, không phải lỗi. 2. **Đặc trưng TMA bị trùng lặp**: `tma1_score_missing`, `tma1_deadline_missing…

15. Edit `outputs/canh_bao_som_d28/analysis.py`
16. Edit `outputs/canh_bao_som_d28/analysis.py`
17. Edit `outputs/canh_bao_som_d28/analysis.py`
18. Bash: `python -I outputs/canh_bao_som_d28/analysis.py > outputs/canh_bao_som_d28/run_log.txt 2>&1; echo exit=$?; python -I - <<'PY' import json, pandas as pd R=json.load(open("outputs/canh_bao_som_d28/results.json",encoding="utf-8")) print("val:", R["val_models"]); print("chosen", R["chosen_model"], "thr"…`  
  ↳ **lỗi:** A variable in this command can't be checked before it runs
19. Bash: `python -I outputs/canh_bao_som_d28/analysis.py > outputs/canh_bao_som_d28/run_log.txt 2>&1; echo exit=$?`  
  ↳ **lỗi:** A variable in this command can't be checked before it runs
20. Bash: `python -I outputs/canh_bao_som_d28/analysis.py > outputs/canh_bao_som_d28/run_log.txt 2>&1 && echo done`
21. Write `outputs/scratch/show.py`
22. Bash: `python -I outputs/scratch/show.py`

> Các hệ số đã hợp lý (lượt nhấp, ngày hoạt động và nộp TMA1 đều mang dấu âm). Tôi lấy thêm số liệu so sánh cặp và tỉ lệ không hoạt động để trả lời câu 1.

23. Bash: `cd /root/.cache/skill-bench/runs/oulad-1/haiku__skills/oulad_early_warning/r1/workspace/outputs/canh_bao_som_d28 && python -I -c " import pandas as pd pd.set_option('display.width',250) k=pd.read_csv('cau1_so_sanh_3_nhom.csv') print(k[['chi_bao','p_KW_holm','eta2','trung_vi_Pass','trung_vi_Fail','t…`

> Số liệu đã đủ cho 5 câu. Tôi kiểm tra nhanh hai biểu đồ để chắc chắn tiếng Việt hiển thị đúng và nhãn không bị chồng.

24. Read `outputs/canh_bao_som_d28/cau3_recall_theo_ti_le_gan_co.png`
25. Read `outputs/canh_bao_som_d28/cau2_khac_biet_theo_tuan.png`

> Biểu đồ hiển thị đúng tiếng Việt. Tôi xóa thư mục nháp của mình, rồi viết answer.md và story.md.

26. Bash: `cd /root/.cache/skill-bench/runs/oulad-1/haiku__skills/oulad_early_warning/r1/workspace/outputs && rm -r scratch && ls && head -c 600 canh_bao_som_d28/cau5_giai_thich_tung_sinh_vien.csv`
27. Write `outputs/canh_bao_som_d28/answer.md`

> Tôi đối chiếu lại từng con số trong answer.md với kết quả. Có vài chỗ sai nhỏ cần sửa: số chỉ báo có ý nghĩa (36/37, không phải 34/37), AUC đơn biến thấp nhất là 0,59, và một số làm tròn.

28. Edit `outputs/canh_bao_som_d28/answer.md`
29. Edit `outputs/canh_bao_som_d28/answer.md`
30. Edit `outputs/canh_bao_som_d28/answer.md`
31. Edit `outputs/canh_bao_som_d28/answer.md`
32. Edit `outputs/canh_bao_som_d28/answer.md`
33. Edit `outputs/canh_bao_som_d28/answer.md`
34. Edit `outputs/canh_bao_som_d28/answer.md`
35. Write `outputs/canh_bao_som_d28/story.md`

> ## Trả lời 5 câu hỏi (mốc cuối ngày 28) Dữ liệu có 13.020 lượt đăng ký còn học đến ngày 28, trong đó 43% không hoàn thành (5.621 người: 3.469 Fail và 2.152 Withdrawn). Kết quả chính: dữ liệu đến ngày 28 phân biệt được nhóm có nguy cơ ở mức trung bình, nhưng danh sách 200 suất mỗi module-kỳ chỉ bắt …


## Trả lời cuối cùng

## Trả lời 5 câu hỏi (mốc cuối ngày 28) Dữ liệu có 13.020 lượt đăng ký còn học đến ngày 28, trong đó 43% không hoàn thành (5.621 người: 3.469 Fail và 2.152 Withdrawn). Kết quả chính: dữ liệu đến ngày 28 phân biệt được nhóm có nguy cơ ở mức trung bình, nhưng danh sách 200 suất mỗi module-kỳ chỉ bắt được khoảng 25% số người không hoàn thành. 1. **Tương tác 4 tuần đầu:** Pass tương tác nhiều nhất, Withdrawn ở giữa, Fail thấp nhất ở mọi tuần. Tổng lượt nhấp 4 tuần (trung vị) là Pass 251, Withdrawn 158, Fail 111. Khác biệt giữa 3 nhóm có ý nghĩa thống kê (Kruskal-Wallis, Holm, p < 0,001). 2. **Chỉ báo khác biệt:** 36/37 chỉ báo có ý nghĩa, chủ yếu là hoạt động (lượt nhấp, ngày hoạt động, ngày kể từ lần truy cập cuối, số loại học liệu). Nộp TMA1 đến ngày 28 là chỉ báo rõ nhất: 97% nhóm hoàn thành so với 76% nhóm không hoàn thành. Khác biệt xuất hiện **từ tuần 1** và tăng nhẹ đến tuần 4. Mức tách biệt của từng chỉ báo còn yếu (AUC đơn biến 0,59–0,67). Ngày đăng ký không khác biệt. 3. **Dự báo bằng dữ liệu 0–28:** Có dự báo được ở mức trung bình. Logistic regression đạt AUC 0,67 trên tập test (kỳ 2014J), so với 0,75 trên validation và 0,73 khi kiểm định chéo 5 lớp. Ngưỡng chọn trên validation để đạt recall ≥ 70% cho **recall 64% trên test**, gắn cờ 47% sinh viên, precision 52%. Để đạt 70% trên test cần gắn cờ 53% sinh viên. **Mục tiêu 70% không đạt ở mức gắn cờ thực tế.** 4. **Phân bổ 200 suất:** Trong mỗi module-kỳ, xếp sinh viên theo điểm rủi ro ngoài mẫu và lấy 200 người cao nhất. Danh sách 1.600 sinh viên **trúng 1.383 người (86%)** không hoàn thành, bắt được **24,6%** trên tổng 5.621 người. Không module-kỳ nào đạt 70% với 200 suất. Muốn đạt 70% cần gắn cờ khoảng 49–57% mỗi cohort. 5. **Giải thích cho cố vấn:** Với mỗi sinh viên, tôi tính đóng góp của từng đặc trưng vào điểm rủi ro (logistic, log-odds so với trung bình cohort) và lấy 2 đặc trưng lớn nhất. Đặc trưng hàng đầu với khoảng 1.375/1.600 sinh viên là **chưa nộp TMA1 đến ngày 28**, kế đến là ít hoạt động đến ngày 28. Ví dụ (sinh viên 79378, BBB 2013B): *"Sinh viên 79378 (BBB 2013B) nằm trong nhóm 200 sinh viên có điểm rủi ro cao nhất của module-kỳ này. Yếu tố đóng góp nhiều nhất là chưa nộp TMA1 đến ngày 28, tiếp theo là tổng số ngày hoạt động đến ngày 28 thấp hơn mức trung bình. Cố vấn nên hỗ trợ lập kế hoạch nộp bài đánh giá TMA1 đúng hạn."* Toàn bộ 1.600 câu nằm trong `cau5_giai_thich_tung_sinh_vien.csv`. ## Phương pháp và lựa chọn của tôi - **Đối tượng:** toàn bộ 13.020 sinh viên còn học đến ngày 28. "Hoàn thành" = Pass và Distinction. Nhãn không rò rỉ vào đặc trưng; đã kiểm tra AUC đơn biến của từng đặc trưng. - **Phân chia:** dùng cột `split` có sẵn. Train là 2013, validation là 2014B, test là 2014J. Đây là kiểm tra sang kỳ mới, khắt khe hơn phân chia ngẫu nhiên. - **Đặc trưng mô hình:** 21 đặc trưng, chỉ dùng dữ liệu đến ngày 28 và hồ sơ lúc đăng ký. Tôi bỏ giới tính, khuyết tật, vùng, IMD, độ tuổi khỏi mô hình. Tôi bỏ thêm các đếm lượt nhấp theo loại và cờ TMA1 trùng lặp vì gây cộng …

## Tiêu chí bị trượt (giám khảo)

- AQ3 kết quả: PR-AUC test ±0,05 so với tham chiếu, có baseline, nói rõ mục tiêu 70%  
  ↳ PR-AUC test 0,50, thấp hơn tham chiếu ~0,66 khoảng 0,16, do đưa tma1_score vào (đúng bẫy). AUC 0,67 so với 0,73. Recall 63,9% tại ngưỡng validation và nói rõ chưa đạt 70% (đạt). Baseline chỉ so trên validation, không so trên test.
- AQ4: xếp hạng trong từng module-kỳ trên kỳ test, precision@200 khớp, so với tỉ lệ cơ sở  
  ↳ Có giới hạn 200 cho mỗi module-kỳ. BBB-2014J 0,72 và FFF-2014J 0,885 nằm trong ±0,08, có tỉ lệ cơ sở 0,356/0,399. Nhưng điểm rủi ro lấy từ CV 5-fold xáo trộn ngẫu nhiên trên mọi kỳ, không phải mô hình temporal. Con số chính 1.383/1.600 (86%) gộp cả các kỳ huấn luyện.
