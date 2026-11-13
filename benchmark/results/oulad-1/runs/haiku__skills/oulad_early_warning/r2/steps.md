# oulad_early_warning · haiku__skills · r2

| | |
|---|---|
| Điểm overall / accuracy / quality | 63.5 / 62.5 / 65.0 |
| Thời gian · chi phí · số turn | 404.5 s · $0.249 · 59 |
| Skill đã nạp (theo thứ tự) | (không có) |
| Lỗi công cụ | 6 |

## Các bước


> Bắt đầu bằng việc khám phá dữ liệu.

1. Bash: `ls -la data/ && find data -type f | head -50 && python -c "import pandas, numpy, scipy, matplotlib, seaborn, sklearn; print('ok')"`
2. Bash: `cat data/aq4_decision_params.json; echo; for f in data/*.csv; do echo "== $f"; wc -l < "$f"; head -3 "$f"; done`  
  ↳ **lỗi:** A variable in this command can't be checked before it runs
3. Bash: `cat data/aq4_decision_params.json && echo && for f in data/aq1_student_week.csv data/aq2_diagnostic_table.csv data/aq3_audit_attributes.csv data/aq3_model_table.csv data/context_all_registrations.csv; do echo "== $f"; wc -l "$f"; head -3 "$f"; done`  
  ↳ **lỗi:** A variable in this command can't be checked before it runs
4. Read `data/aq4_decision_params.json`
5. Read `data/aq1_student_week.csv`
6. Read `data/aq2_diagnostic_table.csv`
7. Read `data/aq3_audit_attributes.csv`
8. Read `data/aq3_model_table.csv`
9. Read `data/context_all_registrations.csv`

> Đã thấy cấu trúc các file. Tiếp theo kiểm tra chất lượng dữ liệu: số dòng, nhãn, split, trùng lặp, giá trị thiếu, và các cờ đăng ký/hủy đăng ký.

10. Bash: `mkdir -p /root/.cache/skill-bench/runs/oulad-1/haiku__skills/oulad_early_warning/r2/workspace/outputs/scratch && cat > /root/.cache/skill-bench/runs/oulad-1/haiku__skills/oulad_early_warning/r2/workspace/outputs/scratch/eda.py << 'EOF' import pandas as pd, numpy as np, json D = "data/" ctx = pd.rea…`  
  ↳ **lỗi:** Parser skipped input between top-level statements
11. Write `outputs/scratch/eda.py`
12. Bash: `python outputs/scratch/eda.py`

> Dữ liệu sạch về khóa (không trùng). Quần thể phân tích là 13.020 sinh viên còn active tại ngày 28; split theo kỳ (train 2013B/J, validation 2014B, test 2014J). Tiếp theo kiểm tra rò rỉ dữ liệu (leakage) và tính nhất quán giữa các bảng.

13. Write `outputs/scratch/leak.py`
14. Bash: `python outputs/scratch/leak.py`  
  ↳ **lỗi:** Exit code 1 aq2 cols not in aq3: ['age_band', 'disability', 'final_result', 'gender', 'highest_education', 'imd_band', 'label3', 'region'] aq3 cols not in aq2: ['days_observable_0_28', 'flag_high_act…

> Sửa lỗi: `flag_high_activity` nằm trong bảng model (aq3), không phải bảng diagnostic. Chạy lại phần kiểm tra.

15. Edit `outputs/scratch/leak.py`
16. Bash: `python outputs/scratch/leak.py 2>&1 | tail -n 80`

> Kiểm tra xong: không có rò rỉ nghiêm trọng (điểm TMA1 chỉ có khi đã nộp trước ngày 28; các số theo tuần khớp với bảng tổng hợp). `flag_high_activity` là cờ dẫn xuất nên tôi sẽ bỏ khỏi mô hình. Bảng model không có thông tin nhân khẩu học. Tiếp theo thử nhanh các mô hình để chọn cấu hình và kiểm tra …

17. Write `outputs/scratch/model_try.py`
18. Bash: `python outputs/scratch/model_try.py 2>&1 | tail -n 60`

> Kết quả thử nghiệm: hồi quy logistic (AUC validation 0.756, test 0.685) cho kết quả gần với gradient boosting (0.753 / 0.691). Tôi chọn logistic vì có thể phân rã điểm rủi ro thành đóng góp từng đặc trưng cho câu 5. `registration_lead_days` là số ngày trước khai giảng (= −date_registration), đã xác…

19. Write `outputs/canh-bao-som/analysis.py`

> Script đã viết, nhưng còn vài đoạn thừa (biến `OUT` gán trong lời gọi hàm, dòng `p_i` vô nghĩa, `fmt_rel` không dùng). Dọn lại trước khi chạy.

20. Edit `outputs/canh-bao-som/analysis.py`
21. Edit `outputs/canh-bao-som/analysis.py`
22. Edit `outputs/canh-bao-som/analysis.py`
23. Bash: `python outputs/canh-bao-som/analysis.py 2>&1 | tail -n 150`

> `aq3_model_table` không có cột `final_result`. Tôi sẽ ghép từ `context_all_registrations.csv` (cùng khóa, kiểm tra số dòng).

24. Edit `outputs/canh-bao-som/analysis.py`
25. Edit `outputs/canh-bao-som/analysis.py`
26. Bash: `python outputs/canh-bao-som/analysis.py 2>&1 | tail -n 200`

> `picks_test` chỉ mang vài cột nên thiếu đặc trưng. Sửa `eval_topk` giữ toàn bộ cột.

27. Edit `outputs/canh-bao-som/analysis.py`
28. Bash: `python outputs/canh-bao-som/analysis.py 2>&1 | tail -n 200`

> Script chạy xong. Vài kết quả cần kiểm tra kỹ trước khi viết câu trả lời: (a) ở tập test 2014J, luật "ít lượt truy cập" trúng 289 so với 284 của mô hình, tức mô hình không nhỉnh hơn; (b) LOPO cho precision 85%, cao hơn hẳn test (71%). Xem các bảng chi tiết.

29. Read `outputs/canh-bao-som/q2_chi_bao_hoan_thanh_vs_khong.csv`
30. Read `outputs/canh-bao-som/q4_kiem_dinh_cheo_8_module_ky.csv`
31. Read `outputs/canh-bao-som/q1_tuong_tac_4_tuan_theo_nhom.csv`

> Kết quả Q2 nhất quán: khác biệt đã có ý nghĩa ngay tuần 1 và duy trì đến tuần 4. Q4 có điểm cần làm chắc: trên 2014J, luật đơn giản gần như ngang mô hình, nên tôi bổ sung đối chiếu cùng cơ sở trên kiểm định chéo và validation, cùng trần recall lý thuyết dưới giới hạn 200.

32. Edit `outputs/canh-bao-som/analysis.py`
33. Edit `outputs/canh-bao-som/analysis.py`
34. Edit `outputs/canh-bao-som/analysis.py`
35. Bash: `python outputs/canh-bao-som/analysis.py > outputs/canh-bao-som/run_log.txt 2>&1; echo exit=$?; python -c "import json;d=json.load(open('outputs/canh-bao-som/metrics.json'));[print(k,d[k]) for k in d if k.startswith('q4') and k not in ('q4_lopo_auc',)]; print(d['q4_lopo_auc'])"`  
  ↳ **lỗi:** A variable in this command can't be checked before it runs
36. Bash: `python outputs/canh-bao-som/analysis.py > outputs/canh-bao-som/run_log.txt 2>&1; echo exit=$?`  
  ↳ **lỗi:** A variable in this command can't be checked before it runs
37. Read `outputs/canh-bao-som/metrics.json`

> Lệnh bị chặn vì có `$?`. Chạy lại không dùng biến shell.

38. Bash: `python outputs/canh-bao-som/analysis.py > outputs/canh-bao-som/run_log.txt 2>&1 && echo RUN_OK && tail -n 3 outputs/canh-bao-som/run_log.txt`
39. Read `outputs/canh-bao-som/metrics.json`
40. Read `outputs/canh-bao-som/q4_hieu_qua_200_tren_test.csv`
41. Read `outputs/canh-bao-som/q4_hieu_qua_200_tren_validation.csv`
42. Read `outputs/canh-bao-som/q4_kiem_dinh_cheo_co_so_it_click.csv`

> Kết quả đối chiếu Q4 đã đủ: mô hình thắng luật đơn giản trên validation (352 vs 314 trúng/400) và kiểm định chéo 8 module-kỳ (1356 vs 1243 trúng/1600), nhưng thua nhẹ trên test 2014J (284 vs 289). Tiếp theo kiểm tra so sánh cặp ở Q1 và các câu giải thích ở Q5.

43. Read `outputs/canh-bao-som/q1_so_sanh_cap_nhom.csv`
44. Read `outputs/canh-bao-som/q4_danh_sach_uu_tien_test_2014J_kem_giai_thich.csv`
45. Read `outputs/canh-bao-som/q3_he_so_hoi_quy_logistic.csv`

> Q5 có hai lỗi cần sửa trước khi giao: 1. Số âm của `tma1_days_before_deadline` đang hiển thị thành "nộp TMA1 trước hạn -8 ngày". Phải là "nộp trễ 8 ngày so với hạn". 2. Câu mở đầu nêu "ước tính khoảng 99%". Xác suất của mô hình trên 2014J (tỉ lệ nền thấp hơn) có thể quá tự tin, nên không nên đưa ch…

46. Edit `outputs/canh-bao-som/analysis.py`
47. Edit `outputs/canh-bao-som/analysis.py`
48. Edit `outputs/canh-bao-som/analysis.py`
49. Bash: `python outputs/canh-bao-som/analysis.py > outputs/canh-bao-som/run_log.txt 2>&1 && echo RUN_OK && ls outputs/canh-bao-som/`

> Đã chạy xong. Kiểm tra nhanh biểu đồ Q3 (đường bắt được theo tỉ lệ liên hệ) để chắc nhãn và trục đúng.

50. Read `outputs/canh-bao-som/q3_duong_bat_duoc_tren_test.png`
51. Read `outputs/canh-bao-som/q4_trung_theo_module_ky.png`

> Hai biểu đồ đọc đúng. Kiểm tra lại câu giải thích Q5 sau khi sửa, lấy ví dụ cho báo cáo.

52. Read `outputs/canh-bao-som/q4_danh_sach_uu_tien_test_2014J_kem_giai_thich.csv`
53. Read `outputs/canh-bao-som/q5_tan_suat_yeu_to_trong_danh_sach.csv`

> Tất cả kết quả đã sẵn sàng. Viết `answer.md`, `story.md`, dọn thư mục nháp và kiểm tra cuối.

54. Write `outputs/canh-bao-som/answer.md`

> Đối chiếu lại các số trong `answer.md` với CSV đã tạo. Có ba chỗ cần sửa: "mọi chỉ số" (trung vị số ngày truy cập tuần 1 của Withdrawn và Fail bằng nhau), ngưỡng q (lớn nhất khoảng 3·10⁻¹²), và khoảng δ của Fail so với Pass (đến −0,37).

55. Edit `outputs/canh-bao-som/answer.md`
56. Edit `outputs/canh-bao-som/answer.md`
57. Write `outputs/canh-bao-som/story.md`
58. Bash: `rm -rf outputs/scratch && ls -R outputs | head -50`

> ## Trả lời ngắn 1. **Tương tác 4 tuần đầu:** Pass cao nhất, Fail thấp nhất ở hầu hết chỉ số, Withdrawn nằm giữa. Trung vị lượt truy cập tuần 1 là 53 (Pass), 33 (Withdrawn), 20 (Fail). 2. **Chỉ báo khác biệt:** 28 trên 34 chỉ báo khác biệt có ý nghĩa giữa hoàn thành và không hoàn thành. Khác biệt xu…


## Trả lời cuối cùng

## Trả lời ngắn 1. **Tương tác 4 tuần đầu:** Pass cao nhất, Fail thấp nhất ở hầu hết chỉ số, Withdrawn nằm giữa. Trung vị lượt truy cập tuần 1 là 53 (Pass), 33 (Withdrawn), 20 (Fail). 2. **Chỉ báo khác biệt:** 28 trên 34 chỉ báo khác biệt có ý nghĩa giữa hoàn thành và không hoàn thành. Khác biệt xuất hiện **ngay từ tuần 1** và duy trì đến tuần 4. Nổi bật nhất là nộp TMA1 đúng hạn (93,6% so với 66,5%). 3. **Dự báo đến ngày 28:** Có dự báo được, mức vừa phải. AUC test 2014J là 0,685 (validation 0,756). Ngưỡng chọn trên validation bắt được **63%** sinh viên không hoàn thành trên test, chưa đạt 70%. Đạt 70% cần liên hệ khoảng **52%** sinh viên mỗi module-kỳ, tức khoảng 920–960 người. 4. **Danh sách 200 mỗi module-kỳ:** Xếp theo điểm rủi ro của mô hình, đồng hạng thì ưu tiên ít lượt truy cập đến ngày 28. Trên 2014J, 400 sinh viên **trúng 284 (71%)**, gần ngang luật "ít click nhất" (289). Danh sách này bắt được 21% tổng số sinh viên không hoàn thành. **Mục tiêu 70% không khả thi với giới hạn 200**: ngay cả xếp hạng hoàn hảo cũng chỉ bắt tối đa khoảng 28%. 5. **Giải thích cho cố vấn:** Yếu tố đóng góp nhiều nhất là lượt truy cập thấp đến ngày 28 (90% danh sách), chưa có hoặc điểm TMA1 thấp (57% và 43%). Mỗi sinh viên có 2–3 câu giải thích trong CSV. ## Bằng chứng - **Q1:** Nhóm Withdrawn chỉ gồm người rút sau ngày 28, nên trông tích cực hơn thực tế. Distinction (1.346) được loại khỏi bảng ba nhóm. - **Q2:** Hiệu độ Cliff's δ khoảng −0,26 đến −0,31 ở mỗi tuần. Không có khác biệt đáng kể ở thay đổi truy cập tuần 1→4, số tín chỉ, thời điểm đăng ký, đăng ký muộn. - **Q3:** Mô hình logistic, 34 đặc trưng, huấn luyện trên 2013, chọn ngưỡng trên 2014B, đánh giá trên 2014J. Gradient boosting cho kết quả gần tương đương (AUC test 0,691). Luật đơn giản chỉ đạt AUC 0,652. - **Q4:** Trên kiểm định chéo 8 module-kỳ, mô hình trúng 1.356/1.600 (85%) so với 1.243 (78%) của luật đơn giản. Trên 2014J, hai cách ngang nhau. Nên dùng mô hình, kèm luật đơn giản để đối chiếu. ## Phương pháp - Quần thể: 13.020 sinh viên còn active tại ngày 28, lấy từ `aq3_model_table.csv`. Kết quả cuối kỳ ghép từ `context_all_registrations.csv`, khớp 100%. - Đã loại `flag_high_activity` và `log_clicks_0_28`. Bảng model không có nhân khẩu học, nên mô hình không dùng giới tính, khuyết tật, tuổi, vùng hay IMD. - Hồi quy logistic được chọn vì giải thích được. Đóng góp của từng đặc trưng vào log-odds được dùng để viết câu cho cố vấn. - Tôi chạy các bước phân tích trong một script (`analysis.py`) thay vì gọi lần lượt từng skill con. ## Giả định - Tuần 1–4 tương ứng ngày 0–27. `clicks_0_28` có thêm ngày 28, nên lệch với tổng tuần ở một số sinh viên. - "Hoàn thành" trong Q2 = Pass + Distinction, khớp định nghĩa target. - Không dùng `assumed_conversion_rate = 0,14` trong `aq4_decision_params.json`: không kiểm chứng được trong dữ liệu và không cần cho việc xếp hạng. - Giới hạn 200 áp dụng cho từng module-kỳ, không phải cho cả khóa. ## Lưu ý - Đây là liên quan, không phải nhân quả. Không biết liên hệ có…

## Tiêu chí bị trượt (giám khảo)

- AQ3 rò rỉ/đạo đức: không dùng cột kết quả/thuộc tính nhạy cảm; tma1_score bị loại hoặc được cảnh báo look-ahead  
  ↳ Không dùng thuộc tính nhạy cảm. Tuy nhiên FEATS gồm mọi cột trừ khóa, cột kết quả, flag_high_activity và log_clicks_0_28, nên tma1_score vẫn nằm trong mô hình mà không được cảnh báo khả năng look-ahead. Bài chỉ ghi 'Điểm TMA1 chỉ có khi đã nộp trước ngày 28'.
- AQ3 kết quả: PR-AUC test ±0,05 so với tham chiếu (~0,66), có baseline, ngưỡng từ validation, nói rõ có đạt 70% hay không  
  ↳ AP test của logistic là 0,540, thấp hơn tham chiếu 0,665 khoảng 0,12, gần đúng bằng biến thể có tma1_score (0,539). Gradient boosting đạt 0,591, cũng ngoài khoảng. Phần còn lại đúng: ngưỡng chọn trên validation, recall test 63%, có nói rõ chưa đạt 70%, có so với nền 0,378 và luật đơn giản.
- AQ4: xếp hạng trong từng module-kỳ (200 mỗi bên), precision@200 khớp (BBB ~0,76, FFF ~0,88), so với tỉ lệ nền  
  ↳ Có xếp hạng riêng từng module-kỳ. FFF-2014J đạt 176/200 = 88%, khớp. BBB-2014J chỉ đạt 108/200 = 54%, kém tham chiếu 0,76 tới 0,22, có lẽ do dùng tma1_score. Có so với kỳ vọng ngẫu nhiên (71 và 80).
