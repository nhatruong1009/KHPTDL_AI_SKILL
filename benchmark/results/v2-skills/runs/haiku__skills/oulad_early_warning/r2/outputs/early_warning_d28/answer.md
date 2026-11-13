# Cảnh báo sớm sinh viên có nguy cơ không hoàn thành (mốc cuối ngày 28)

**Dữ liệu:** OULAD, module BBB và FFF, 4 kỳ (2013B, 2013J, 2014B, 2014J). Quần thể là 13.020 đăng ký còn theo học đến cuối ngày 28. Tỷ lệ không hoàn thành (Fail hoặc Withdrawn) là 43,2%, gồm Pass 7.399, Fail 3.469 và Withdrawn 2.152.

## Trả lời ngắn gọn

1. **Tương tác 4 tuần đầu:** sinh viên Pass có lượt truy cập cao hơn rõ rệt ở cả 4 tuần. Trung vị lượt truy cập mỗi tuần của Pass là 59 / 50 / 60 / 43, của Withdrawn là 33 / 24,5 / 36 / 21 và của Fail là 20 / 15 / 23 / 10. Trung vị số ngày có truy cập của Pass là 3 mỗi tuần; Withdrawn là 2; Fail là 2 hoặc 1. Nhóm Withdrawn nằm giữa Pass và Fail. Tỷ lệ "0 ngày truy cập trong tuần" là 8–12% ở Pass, 20–27% ở Withdrawn và 25–34% ở Fail. Mọi cặp so sánh đều có ý nghĩa sau hiệu chỉnh Holm (p < 0,001).

2. **Chỉ báo khác biệt và từ tuần nào:** hầu hết chỉ báo khác biệt có ý nghĩa thống kê, vì cỡ mẫu lớn. Vì vậy cần nhìn hiệu ứng. Chỉ báo mạnh nhất là số ngày có truy cập 0–28 (trung vị 12 so với 7; hiệu ứng 0,35), tiếp theo là lượt vào trang chủ khóa học (49 so với 26), lượt tham gia diễn đàn (69 so với 26), số ngày kể từ lần truy cập cuối (1 so với 3 ngày) và tỷ lệ đã nộp TMA1 đến ngày 28 (97% so với 76%). Khác biệt đã có ý nghĩa **ngay từ tuần 1** (p_Holm ≈ 10⁻¹⁴⁴), hiệu ứng ổn định khoảng 0,26–0,31 theo tuần và tăng dần khi cộng dồn số ngày truy cập (0,26 ở tuần 1 lên 0,35 ở tuần 4). Số ngày đăng ký trước khai giảng không khác biệt (p_Holm = 0,86).

3. **Dự báo chỉ dùng dữ liệu đến ngày 28:** có, ở mức trung bình. Trên tập test (2014J), AUC là 0,716. Ngưỡng được chọn trên validation (2014B) để đạt recall ≥ 70%. Khi áp dụng lên test, mô hình bắt được **71,5%** sinh viên không hoàn thành (khoảng tin cậy 95%: 69,3–73,7%), precision là 50,9%, và phải gắn cờ **53%** quần thể. **Mục tiêu ≥ 70% đạt về điểm ước lượng, nhưng cận dưới khoảng tin cậy nằm dưới 70%, nên đây là kết quả biên.**

4. **Ưu tiên 200 sinh viên mỗi module-kỳ:** xếp theo điểm rủi ro giảm dần trong từng module-kỳ, lấy 200 đầu tiên. Trên test (2014J), danh sách trúng:
   - BBB 2014J: 146/200 (73%) là không hoàn thành, bắt được 146/635 (23%) tổng số.
   - FFF 2014J: 176/200 (88%) là không hoàn thành, bắt được 176/741 (24%) tổng số.
   - Tổng cộng: 322/400 (80,5%) trúng, bắt được 322/1.376 (23%) tổng số.

   **Mục tiêu 70% không đạt trong ràng buộc sức chứa 200.** Với 200 mỗi module-kỳ, chỉ có thể bắt khoảng 23% tổng số không hoàn thành. Để bắt 70%, phải gắn cờ khoảng 53% sinh viên, tức khoảng 950 mỗi module-kỳ, vượt xa sức chứa 200.

5. **Đặc trưng đóng góp nhiều nhất cho cố vấn:** trong 400 sinh viên ưu tiên, các yếu tố xuất hiện nhiều nhất trong 3 yếu tố đầu là số ngày có truy cập 0–28 thấp (359 lần), chưa nộp TMA1 đến ngày 28 (308 lần), TMA1 nộp trễ hoặc chưa nộp (259 lần) và ít truy cập trang chủ khóa học (114 lần). Ví dụ hai câu cho cố vấn (sinh viên được tạo tự động từ đóng góp của mô hình, xem `q4_priority_list_test_k200.csv`):

   > Sinh viên này được xếp ưu tiên chủ yếu vì chưa nộp bài TMA1 đến ngày 28, ít ngày có truy cập trong 28 ngày đầu và đã học lại nhiều lần trước đây. Nên nhắc lịch nộp bài TMA và hỗ trợ kế hoạch cho bài tiếp theo. Đây là tín hiệu dự báo từ dữ liệu 28 ngày đầu, nên dùng để mở đầu trao đổi, không phải kết luận về năng lực của sinh viên.

   > Sinh viên này được xếp ưu tiên chủ yếu vì bài TMA1 nộp trễ hạn hoặc chưa nộp, ít ngày có truy cập trong 28 ngày đầu và ít truy cập hệ thống trước khi khai giảng. Nên nhắc lịch nộp bài TMA và hỗ trợ kế hoạch cho bài tiếp theo. Đây là tín hiệu dự báo từ dữ liệu 28 ngày đầu, nên dùng để mở đầu trao đổi, không phải kết luận về năng lực của sinh viên.

## Phương pháp

- **Quần thể và nhãn:** dùng `aq3_model_table.csv` (13.020 dòng, đã loại đăng ký rút trước ngày 28 và đăng ký sau ngày 28). Nhãn không hoàn thành = `target_noncompletion` (Fail hoặc Withdrawn = 1; Pass và Distinction = 0). Kiểm tra: nhãn khớp với `label3` 100%.
- **Chia dữ liệu:** dùng cột `split` có sẵn, theo kỳ. Train = 2013B và 2013J (6.795 dòng), validation = 2014B (2.581), test = 2014J (3.644). Mô hình và ngưỡng được chọn trên validation; test dùng một lần để báo cáo.
- **Đặc trưng (32 biến, đều quan sát được đến ngày 28):** lượt truy cập và số ngày truy cập theo tuần 1–4, tổng hợp 0–28, truy cập theo loại tài nguyên, truy cập trước khai giảng, nhóm TMA1 (đã nộp đến ngày 28, đúng hạn, số ngày trước hạn), số lần học trước, số tín chỉ, số ngày đăng ký trước khai giảng, đã học module trước, đăng ký muộn.
- **Loại trừ:**
  - Thuộc tính nhạy cảm (giới tính, độ tuổi, khuyết tật, IMD, vùng) không dùng làm biến dự báo. Chỉ dùng để kiểm tra sai số theo nhóm.
  - `highest_education` không dùng làm biến dự báo. Đây là lựa chọn của tôi vì biến này gần với thuộc tính nền tảng xã hội.
  - `tma1_score` không dùng trong mô hình chính vì không có ngày công bố điểm trong dữ liệu. Đưa vào như phân tích độ nhạy có nhãn.
- **Mô hình:** hồi quy logistic (chuẩn hoá, C = 1). So sánh với gradient boosting (HistGradientBoosting). Quy tắc chọn đặt trước khi xem test: chỉ dùng boosting nếu AUC validation cao hơn logistic trên 0,01. Logistic AUC validation 0,729; boosting 0,724, nên chọn logistic.
- **Ngưỡng:** ngưỡng cao nhất đạt recall ≥ 0,70 trên validation (0,3865). Recall trên validation là 0,703.
- **Danh sách ưu tiên:** xếp theo xác suất rủi ro giảm dần trong từng module-kỳ, lấy top 200. Tie-break theo `id_student` nhỏ hơn.
- **Giải thích cá nhân:** đóng góp của mỗi đặc trưng vào log-odds = hệ số × giá trị chuẩn hoá, so với sinh viên trung bình của tập train. Lấy 3 đóng góp dương lớn nhất, tối đa một ý về TMA1 để câu không lặp.

## Kết quả độ nhạy (`q3_sensitivity_models.csv`)

| Phiên bản | Test AUC | Test recall | Tỷ lệ gắn cờ | Đạt 70%? |
|---|---|---|---|---|
| **Chính: logistic, 32 đặc trưng** | **0,716** | **0,715** | **53%** | **Có (biên)** |
| Boosting, 32 đặc trưng | 0,713 | 0,676 | 50% | Không |
| Bỏ nhóm TMA1, logistic | 0,692 | 0,775 | 63% | Có, nhưng gắn cờ nhiều hơn |
| Thêm điểm TMA1 (độ nhạy), logistic | 0,667 | 0,659 | 48% | Không |
| Đường cơ sở: chỉ tổng lượt truy cập 0–28 | 0,652 | 0,706 | 59% | Có, precision thấp hơn |

Kết luận: đạt 70% recall phụ thuộc vào mô hình và cách chọn ngưỡng. Khi thêm điểm TMA1 hoặc đổi sang boosting, kết quả trên test không đạt 70%. Mô hình chính chỉ hơn đường cơ sở về AUC (0,716 so với 0,652) và precision (0,509 so với 0,451), không phải về recall.

**Kiểm tra theo nhóm (chỉ để audit, test):** recall nam 72%, nữ 71%. Recall nhóm khuyết tật là 66% (n = 341), nhóm không khuyết tật là 72%. Recall nhóm tuổi 35–55 là 67%, nhóm 0–35 là 73%. Nhóm có khuyết tật có tỷ lệ không hoàn thành thực tế cao hơn (52%), nhưng mô hình bắt được ít hơn. Đây là điểm cần theo dõi nếu hệ thống triển khai.

**Sức chứa (`q4_capacity_summary.csv`):** trên test, k = 100 cho 94/100 và 90/100; k = 300 cho 196/300 và 243/300 (BBB và FFF). Đối chứng "ít lượt truy cập nhất 0–28" với k = 200 cho 121/200 và 168/200. Mô hình rủi ro tốt hơn đối chứng ở cả hai module-kỳ, tổng cộng 322 so với 289 trúng.

## Hạn chế và giả định

- **Đường cơ sở và chọn ngưỡng:** mô hình train trên các kỳ 2013 và đánh giá trên kỳ 2014J. Ngưỡng chọn trên 2014B có recall validation chỉ 0,703, rất sát mức 70%. Vì vậy khoảng cách với mục tiêu là rất nhỏ.
- **Test đã được xem trong bảng độ nhạy:** các phiên bản độ nhạy được tính trên test để báo cáo. Chúng không được dùng để chọn mô hình hay ngưỡng cho kết quả chính.
- **Câu 2 dùng toàn bộ quần thể:** đây là thống kê mô tả. Không dùng để huấn luyện.
- **Hiệp phương sai:** tổng truy cập 0–28 và truy cập theo tuần tương quan mạnh, nên tỷ phần đóng góp giữa chúng chỉ là xấp xỉ. Các câu nêu "đặc trưng nào" nên được hiểu là đóng góp tương đối, không phải nguyên nhân.
- **Quan sát, không phải thí nghiệm:** kết quả cho thấy liên hệ và khả năng dự báo, không chứng minh rằng tăng truy cập sẽ cải thiện kết quả.
- **Tham số `assumed_conversion_rate` (0,14) trong `aq4_decision_params.json` không được dùng**, vì câu hỏi không đề cập đến tỷ lệ chuyển đổi.
- **Cách hiểu của tôi:** "tương tác" là lượt truy cập và số ngày có truy cập trong hệ thống học trực tuyến; "sức chứa 200" áp dụng cho từng module-kỳ trên kỳ test (2014J).

## Tệp đầu ra (`outputs/early_warning_d28/`)

- `analysis.py`: toàn bộ mã phân tích, chạy được từ thư mục gốc dự án.
- `run_log.txt`: nhật ký chạy.
- Câu 1: `q1_weekly_by_outcome.csv`, `q1_pairwise_tests.csv`, `q1_totals_by_outcome.csv`, `q1_weekly_by_outcome.png`.
- Câu 2: `q2_indicator_tests.csv`, `q2_first_week_significant.csv`, `q2_indicator_effects.png`.
- Câu 3: `q3_main_metrics.csv`, `q3_sensitivity_models.csv`, `q3_audit_by_group_test.csv`, `q3_test_capture_curve.png`.
- Câu 4: `q4_capacity_summary.csv`, `q4_capacity_hits.png`, `q4_priority_list_test_k200.csv` (có ID sinh viên, điểm rủi ro, 3 yếu tố chính và câu cho cố vấn).
- Câu 5: `q5_top_driver_counts.csv`.
