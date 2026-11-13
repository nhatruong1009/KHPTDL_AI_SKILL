# Hệ thống cảnh báo sớm — OULAD, module BBB & FFF, 4 kỳ (2013B–2014J)

## Phạm vi và cách làm

- **Quần thể:** 13.020 lượt đăng ký còn theo học đến cuối ngày 28 (lọc `unregistered_by_d28 = 0` và `registered_after_d28 = 0`; khớp đúng với bảng mô hình).
- **Mục tiêu "không hoàn thành":** Fail hoặc Withdrawn = 5.621 (43,2%). Pass gồm cả Distinction.
- **Chia thời gian:** train = 2013B, 2013J; validation = 2014B; test = 2014J (đúng cột `split` trong dữ liệu). Kết quả trên test là ước lượng khách quan nhất vì mô hình chưa từng thấy kỳ 2014J.
- **Đặc trưng:** chỉ dùng các cột trong `aq3_model_table.csv` (tương tác 0–28, TMA1 nộp đến ngày 28, lịch sử học). Demographic chỉ dùng như kiểm tra độ nhạy, không đưa vào mô hình chính.

## Câu 1 — Tương tác 4 tuần đầu khác nhau thế nào giữa Pass / Fail / Withdrawn?

Trung vị lượt nhấp mỗi tuần (xem `q1_weekly_by_outcome.csv`, biểu đồ `chart1_tuong_tac_4_tuan.png`):

| Tuần | Pass | Fail | Withdrawn |
|---|---|---|---|
| 1 | 59 | 20 | 33 |
| 2 | 50 | 15 | 24,5 |
| 3 | 60 | 23 | 36 |
| 4 | 43 | 10 | 21 |

- **Pass** tương tác nhiều nhất và đều qua 4 tuần. Tỷ lệ tuần không có lượt nhấp nào khoảng 8–12%.
- **Fail** thấp nhất. Khoảng 25–34% số tuần của nhóm này không có lượt nhấp nào; số ngày hoạt động trung vị chỉ 1–2 ngày/tuần.
- **Withdrawn** nằm giữa Pass và Fail, gần Fail hơn ở tuần 2 và 4. Vì vậy nhóm rút học không chỉ là "Fail nhẹ hơn".
- Khác biệt giữa ba nhóm có ý nghĩa thống kê ở mọi tuần (Kruskal–Wallis, p < 10⁻¹⁴⁰).

## Câu 2 — Chỉ báo nào khác biệt giữa hoàn thành (Pass) và không hoàn thành (Fail + Withdrawn)? Từ tuần nào?

Kiểm định Mann–Whitney, hiệu chỉnh BH trên toàn bộ 26 phép kiểm định. AUC = xác suất sinh viên Pass có giá trị cao hơn một sinh viên không hoàn thành (0,5 = không phân biệt được). Chi tiết trong `q2_indicator_tests.csv`.

- **Mọi chỉ báo đều có ý nghĩa** sau hiệu chỉnh (q < 0,05). Với ~13.000 sinh viên, ngưỡng p-value gần như luôn đạt, nên cần nhìn AUC.
- **Từ tuần 1:** lượt nhấp tuần 1 AUC = 0,630; ngày hoạt động tuần 1 AUC = 0,631. Khác biệt đã có ngay tuần đầu.
- **Củng cố dần qua các tuần:** ngày hoạt động lũy kế AUC tăng 0,631 → 0,657 → 0,666 → 0,673 (tuần 1 → 4). Lượt nhấp lũy kế cũng tăng tương tự.
- **Khác biệt xuất hiện trước cả khi khóa học bắt đầu:** lượt nhấp trước khai giảng AUC = 0,628. Đây là dấu hiệu của thói quen học/động lực có sẵn, không chỉ là hệ quả của 4 tuần đầu.
- **Chỉ báo mạnh nhất tại ngày 28:** số ngày từ lần hoạt động cuối đến ngày 28 (AUC đảo chiều 0,349, tương đương 0,651); ngày hoạt động lũy kế đến tuần 4 (0,673); nộp TMA1 đến ngày 28 (0,609); điểm TMA1 (0,611).

Biểu đồ: `chart2_chi_bao_theo_tuan.png`.

## Câu 3 — Chỉ dùng dữ liệu ngày 0–28, có dự báo được không, và đạt mục tiêu 70% không?

Mô hình chính: hồi quy logistic có chuẩn hóa, C = 0,5, huấn luyện trên train, đặt ngưỡng trên validation sao cho recall ≥ 70%, rồi áp dụng nguyên ngưỡng đó lên test. Gradient boosting chạy để so sánh (`q3_model_performance.csv`).

| Mô hình | Tập | AUC | Recall | Precision | Tỷ lệ bị cảnh báo |
|---|---|---|---|---|---|
| Logistic (chính) | validation 2014B | 0,756 | 0,700 | 0,643 | 50,6% |
| Logistic (chính) | **test 2014J** | **0,685** | **0,635** | 0,522 | 45,9% |
| Gradient boosting | test 2014J | 0,696 | 0,656 | 0,510 | 48,5% |

**Kết luận: mô hình có dự báo được, nhưng ở mức trung bình. Không đạt mục tiêu 70% trên dữ liệu chưa thấy.**

- Trên validation, recall 70% đạt được vì ngưỡng được chọn ở đó. Khi chuyển sang 2014J, recall rơi xuống 63,5%.
- Để đạt ≥ 70% recall trên test, cần cảnh báo khoảng **52% số sinh viên** (≈1.900 người). Với mức này, precision chỉ khoảng 0,5.
- Demographic (giới, độ tuổi, IMD, trình độ, khuyết tật) không cải thiện đáng kể: AUC 0,699, recall 0,645 (`q3_sensitivity_demographics.json`).
- Tỷ lệ không hoàn thành khác giữa các kỳ: 2014B 46,5%, 2014J 37,8%. Ngưỡng cố định khi kỳ có tỷ lệ thấp hơn sẽ cảnh báo nhiều hơn mức cần thiết.

## Câu 4 — Ưu tiên ai với tối đa 200 sinh viên mỗi module-kỳ, và trúng bao nhiêu?

**Quy tắc:** trong mỗi module-kỳ, sắp xếp sinh viên theo điểm rủi ro của mô hình (xác suất không hoàn thành) giảm dần, lấy 200 người đầu. Điểm rủi ro được tính bằng mô hình logistic huấn luyện trên các kỳ trước (train + validation), áp dụng cho 2014J (`q4_capacity_hits.csv`, `q4_priority_list_2014J.csv`).

| Module-kỳ | Số SV | Không hoàn thành thực tế | Trúng trong 200 ưu tiên | Precision | Trên tổng số không hoàn thành |
|---|---|---|---|---|---|
| BBB 2014J | 1.786 | 635 | **111** | 55,5% | 17,5% |
| FFF 2014J | 1.858 | 741 | **176** | 88,0% | 23,8% |
| **Tổng** | 3.644 | 1.376 | **287 / 400 (71,8%)** | | |

- Baseline "ít lượt nhấp nhất trong 0–28 ngày" trúng 289/400, gần như bằng mô hình. Mô hình tốt hơn ở FFF (176 so với 168) và kém hơn ở BBB (111 so với 121).
- **Giới hạn của năng lực:** 200 suất chỉ bao phủ 18–24% tổng số sinh viên không hoàn thành của mỗi module. Dù danh sách trúng tốt, phần lớn người cần hỗ trợ vẫn nằm ngoài danh sách.

Biểu đồ: `chart3_trung_danh_sach_uu_tien.png`.

## Câu 5 — Với mỗi sinh viên ưu tiên, yếu tố nào đóng góp nhiều nhất? (Lời khuyên cho cố vấn)

Mỗi sinh viên được phân tích bằng cách phân rã điểm rủi ro của mô hình logistic thành đóng góp của từng đặc trưng (`q5_top_factors_priority_2014J.csv`, cột `ghi_chú_cho_cố_vấn`).

- **Chưa nộp bài TMA1 đến ngày 28:** 232 sinh viên. Trong nhóm này, 90% thực tế không hoàn thành.
- **Đã nộp TMA1 nhưng điểm thấp:** 167 sinh viên. Gần một nửa không hoàn thành.
- **Yếu tố thứ hai** phổ biến nhất là ít lượt nhấp trong 0–28 ngày (312 sinh viên).

Ví dụ ghi chú (2–3 câu, không thuật ngữ):

> Sinh viên 654923 (BBB 2014J) nằm trong nhóm ưu tiên hạng 1; yếu tố làm tăng rủi ro nhiều nhất là bài TMA1 đã nộp nhưng điểm thấp (1/100). Yếu tố tiếp theo: ít truy cập học liệu trong 4 tuần đầu (0 lượt nhấp). Gợi ý: hẹn trao đổi về cách làm bài và các nội dung còn yếu.

Lưu ý: các đặc trưng về lượt nhấp và ngày hoạt động có tương quan mạnh, nên phân bổ đóng góp giữa chúng chỉ mang tính minh họa. Đây là giải thích của mô hình, không phải quan hệ nhân quả.

## Hạn chế và các giả định

- **Ngưỡng 70% không đạt trên test**, đây là kết quả chính cần nhà trường cân nhắc: mục tiêu này đòi hỏi cảnh báo khoảng một nửa sinh viên, không phù hợp với năng lực 200 suất mỗi module.
- **Kiểm chứng biểu đồ:** script `validate_palette.js` không chạy được trong lần này (lệnh bị từ chối), nên bảng màu lấy theo giá trị tham chiếu của kỹ năng dataviz (xanh, cam, lục lam); chưa được kiểm chứng bằng validator.
- **`aq4_decision_params.json`:** tỷ lệ chuyển đổi giả định 0,14 không được dùng vì không có câu hỏi nào yêu cầu và không kiểm chứng được nguồn ("A5 (P1), C05 (P3)").
- **Các chỉ báo tính đến ngày 28:** `tma1_score` và `tma1_days_before_deadline` bị thiếu với sinh viên chưa nộp; đã điền bằng trung bình huấn luyện (trung tính), còn thông tin "chưa nộp" được giữ bởi cờ `tma1_submitted_by_d28`. Điền 0 sẽ tạo đóng góp giả rất lớn, đã loại bỏ.
- **Mô hình chỉ có 2 module-kỳ test (2014J).** Kết quả Q4 dựa trên 400 sinh viên của hai nhóm này.

## Tệp đầu ra

- `answer.md` (file này), `story.md`
- Bảng: `q1_weekly_by_outcome.csv`, `q2_indicator_tests.csv`, `q3_model_performance.csv`, `q3_recall_curve_test.csv`, `q3_lr_coefficients.csv`, `q4_capacity_hits.csv`, `q4_priority_list_2014J.csv`, `q5_top_factors_priority_2014J.csv`
- Biểu đồ: `chart1_tuong_tac_4_tuan.png`, `chart2_chi_bao_theo_tuan.png`, `chart3_trung_danh_sach_uu_tien.png`
- Mã: `scripts/` (`q1_q2.py`, `q3_5.py`, `q5_text.py`, `charts.py`)
