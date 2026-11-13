# Cảnh báo sớm sinh viên không hoàn thành — mốc cuối ngày 28

## Trả lời nhanh

1. **Tương tác 4 tuần đầu**: Pass tương tác nhiều nhất, Withdrawn ở giữa, Fail thấp nhất ở mọi tuần. Tổng lượt nhấp 4 tuần (trung vị): Pass 251, Withdrawn 158, Fail 111.
2. **Chỉ báo khác biệt có ý nghĩa**: hầu hết chỉ báo hoạt động (lượt nhấp, số ngày hoạt động, ngày kể từ lần truy cập cuối, số loại học liệu) và việc nộp TMA1 đến ngày 28. Khác biệt xuất hiện **từ tuần 1** và tăng nhẹ đến tuần 4. Mức tách biệt của từng chỉ báo còn yếu đến trung bình (AUC đơn biến 0,59–0,67).
3. **Dự báo chỉ dùng dữ liệu 0–28**: có dự báo được ở mức trung bình. AUC trên tập test 0,67 (validation 0,75). Ở ngưỡng chọn trên validation để đạt recall ≥ 70%, tập test chỉ đạt **recall 64%**. Muốn đạt 70% trên test phải gắn cờ **53% sinh viên**, với precision 50%. **Mục tiêu 70% không đạt ở mức gắn cờ thực tế.**
4. **Danh sách 200 mỗi module-kỳ** (1.600 sinh viên, ưu tiên theo điểm rủi ro cao nhất trong từng module-kỳ): **1.383 / 1.600 (86%)** thực sự không hoàn thành. Danh sách bắt được **24,6%** trong tổng số 5.621 sinh viên không hoàn thành. Với năng lực 200 mỗi module-kỳ, không thể đạt 70%; cần gắn cờ khoảng 49–57% sinh viên mỗi module-kỳ.
5. **Đặc trưng đóng góp nhiều nhất** cho sinh viên trong danh sách: chưa nộp TMA1 đến ngày 28 (khoảng 1.375 / 1.600 trường hợp), kế đến là ít hoạt động đến ngày 28 (tổng ngày hoạt động hoặc tổng lượt nhấp thấp). Mỗi sinh viên có 2–3 câu giải thích trong `cau5_giai_thich_tung_sinh_vien.csv`.

## Dữ liệu và phạm vi

- 13.020 lượt đăng ký còn học đến ngày 28 (BBB và FFF, 4 kỳ mỗi module). Tỉ lệ không hoàn thành (Fail hoặc Withdrawn) **43,2%** (5.621 người). Khớp hoàn toàn giữa `aq2`, `aq3_model_table` về khóa, phân chia và nhãn.
- Nhãn: Fail và Withdrawn là "không hoàn thành"; Pass và Distinction là "hoàn thành".
- Phân chia có sẵn theo kỳ: train = 2013B và 2013J, validation = 2014B, test = 2014J. Tập test là **kỳ sau** nên là bài kiểm tra "sang kỳ mới" khắt khe hơn một phân chia ngẫu nhiên.
- Tuần k = ngày 7(k−1) đến 7k−1 (giả định; đã kiểm tra tổng lượt nhấp theo tuần khớp với `aq1`).

## Câu 1 — Tương tác 4 tuần đầu theo Pass / Fail / Withdrawn

| Chỉ số (trung vị) | Pass | Fail | Withdrawn |
|---|---|---|---|
| Lượt nhấp tuần 1 / 2 / 3 / 4 | 59 / 50 / 60 / 43 | 20 / 15 / 23 / 10 | 33 / 24,5 / 36 / 21 |
| Lượt nhấp 4 tuần | 251 | 111 | 158 |
| Ngày hoạt động 4 tuần | 12 | 7 | 9 |
| Tỉ lệ không có lượt nhấp nào trong tuần 4 | 12% | 34% | 27,5% |

- Khác biệt giữa 3 nhóm có ý nghĩa ở mọi chỉ báo (Kruskal-Wallis, hiệu chỉnh Holm, p < 0,001). Hiệu ứng nhỏ đến trung bình (eta² 0,05–0,09).
- So cặp: Fail thấp hơn Pass rõ nhất (xác suất Fail > Pass chỉ 0,32 cho lượt nhấp 4 tuần). Withdrawn ở giữa: cao hơn Fail (0,57) và thấp hơn Pass (0,39).

## Câu 2 — Chỉ báo khác biệt giữa Hoàn thành và Không hoàn thành

Kiểm định Mann-Whitney (hoặc chi-square cho nhị phân) cho 37 chỉ báo, hiệu chỉnh Holm. Chi tiết: `cau2_chi_bao_hoan_thanh_vs_khong.csv`.

- **Có ý nghĩa (36/37)**, xếp theo AUC đơn biến:
  - Ngày hoạt động tích lũy đến tuần 4: AUC 0,67 (trung vị 12 so với 7).
  - Lượt nhấp trang chủ khóa học đến ngày 28: AUC 0,67 (49 so với 26).
  - Lượt nhấp tích lũy đến tuần 4: AUC 0,65 (251 so với 125).
  - Ngày kể từ lần hoạt động cuối (ngày 28): AUC 0,65 (trung vị 1 so với 3).
  - Lượt nhấp diễn đàn: AUC 0,65 (69 so với 26).
  - **Nộp TMA1 đến ngày 28**: 97,3% ở nhóm hoàn thành, 75,5% ở nhóm không hoàn thành. Nộp TMA1 đúng hạn: 93,6% so với 66,5%.
  - Điểm TMA1 (trung vị 80 so với 74): AUC 0,61.
  - Số loại học liệu đã truy cập: AUC 0,62.
- **Không có ý nghĩa**: số ngày đăng ký trước khai giảng (`registration_lead_days`).
- Một số chỉ báo có ý nghĩa thống kê nhưng yếu về thực tế hoặc chiều ngược: `clicks_change_w1_w4` (AUC 0,48), số tín chỉ (0,47), lần học lại (0,45), `no_vle_activity_0_28` (0,46).

**Từ tuần nào?** Lượt nhấp và ngày hoạt động của **tuần 1** đã khác biệt có ý nghĩa (AUC 0,63). Tuần 2 đạt 0,65–0,66; tuần 3 đạt 0,63–0,67; tuần 4 đạt 0,65–0,67. Khác biệt có mặt sớm và chủ yếu tăng nhẹ theo thời gian (`cau2_khac_biet_theo_tuan.png`).

## Câu 3 — Dự báo chỉ dùng dữ liệu 0–28

- **Đặc trưng (33 cột, rút gọn còn 21 sau khi bỏ cộng tuyến)**: lượt nhấp và ngày hoạt động theo tuần, tổng đến ngày 28, số loại học liệu, ngày kể từ lần hoạt động cuối, hoạt động trước khai giảng, nộp TMA1 và điểm TMA1, số lần học lại, số tín chỉ, trình độ học vấn, số ngày đăng ký trước khai giảng.
- **Không dùng** giới tính, khuyết tật, vùng, IMD, độ tuổi trong mô hình. Đây là lựa chọn của tôi, để tránh đưa thuộc tính nhân khẩu vào quyết định cảnh báo.
- **Chọn mô hình**: logistic regression (AUC validation 0,746) nhỉnh hơn HistGradientBoosting (0,738), nên chọn logistic vì dễ giải thích cho cố vấn. Baseline "ít lượt nhấp đến ngày 28": AUC validation 0,647.

| Tập test (2014J, 3.644 sinh viên) | Giá trị |
|---|---|
| AUC | 0,67 |
| PR-AUC (cơ sở 37,8%) | 0,50 |
| Ngưỡng (chọn trên validation, recall ≥ 70%) | 0,385 |
| Recall (bắt được) | **63,9%** (879 / 1.376) |
| Precision | 51,6% |
| Tỉ lệ sinh viên bị gắn cờ | 46,8% |
| Bỏ sót | 497 sinh viên |
| Đạt recall 70% | cần gắn cờ **52,6%** sinh viên, precision 50,3% |

Đánh giá ngoài mẫu 5-fold trên toàn bộ 13.020 sinh viên: AUC 0,73, nhất quán với validation.

**Kết luận**: dự báo được ở mức trung bình, tốt hơn baseline đơn giản. Không đạt 70% recall với số gắn cờ hợp lý. Đạt 70% cần gắn cờ khoảng một nửa số sinh viên.

## Câu 4 — Phân bổ 200 suất liên hệ mỗi module-kỳ

- **Quy tắc**: trong từng module-kỳ, xếp sinh viên theo điểm rủi ro (xác suất không hoàn thành từ logistic, ngoài mẫu 5-fold), lấy 200 người có điểm cao nhất. Không xét thêm tiêu chí nào khác.
- **Kết quả**:

| Module-kỳ | Số SV | Không hoàn thành | Trong 200 | Precision | Recall trong danh sách | SV cần gắn cờ để bắt 70% |
|---|---|---|---|---|---|---|
| BBB 2013B | 1.529 | 727 | 190 | 95,0% | 26,1% | 765 (50%) |
| BBB 2013J | 1.834 | 763 | 175 | 87,5% | 22,9% | 913 (50%) |
| BBB 2014B | 1.280 | 553 | 170 | 85,0% | 30,7% | 661 (52%) |
| BBB 2014J | 1.786 | 635 | 144 | 72,0% | 22,7% | 1.015 (57%) |
| FFF 2013B | 1.450 | 668 | 174 | 87,0% | 26,1% | 748 (52%) |
| FFF 2013J | 1.982 | 887 | 178 | 89,0% | 20,1% | 997 (50%) |
| FFF 2014B | 1.301 | 647 | 175 | 87,5% | 27,1% | 673 (52%) |
| FFF 2014J | 1.858 | 741 | 177 | 88,5% | 23,9% | 903 (49%) |
| **Tổng** | **13.020** | **5.621** | **1.383 / 1.600** | **86,4%** | **24,6%** | |

- Danh sách **trúng 1.383 / 1.600 sinh viên** không hoàn thành. Không module-kỳ nào đạt 70% recall với 200 suất.
- Với năng lực 200 mỗi module-kỳ, không thể đạt mục tiêu 70%; mục tiêu này cần khoảng một nửa cohort được gắn cờ.
- Điểm rủi ro ngoài mẫu trên toàn bộ cohort được xếp hạng trong từng module-kỳ, nên con số trúng là kết quả thử ngoài mẫu, không phải kết quả huấn luyện.
- File `aq4_decision_params.json` có tỉ lệ chuyển đổi giả định 14%, nhưng không nêu rõ định nghĩa và nguồn. Tôi không dùng tỉ lệ này trong các con số trên.

## Câu 5 — Đặc trưng đóng góp nhiều nhất cho từng sinh viên trong danh sách

- **Cách tính**: với logistic, đóng góp của từng đặc trưng vào log-odds bằng hệ số × (giá trị của sinh viên − trung bình cohort) / độ lệch chuẩn. Tôi lấy 2 đặc trưng đóng góp dương lớn nhất. Đặc trưng có giá trị đã điền thay thế (thiếu điểm TMA1) bị loại khỏi phần giải thích.
- **Đặc trưng hàng đầu** (số sinh viên trong 1.600): chưa nộp TMA1 đến ngày 28 (~1.375), tổng ngày hoạt động đến ngày 28 thấp (~101), tổng lượt nhấp đến ngày 28 thấp (~58), trình độ học vấn trước khóa (~19), lượt nhấp tuần 3 thấp (~14), số tín chỉ (~11), điểm TMA1 (~11).
- **Ví dụ câu cho cố vấn** (sinh viên 79378, BBB 2013B):
  > Sinh viên 79378 (BBB 2013B) nằm trong nhóm 200 sinh viên có điểm rủi ro cao nhất của module-kỳ này. Yếu tố đóng góp nhiều nhất là chưa nộp TMA1 đến ngày 28, tiếp theo là tổng số ngày hoạt động đến ngày 28 thấp hơn mức trung bình. Cố vấn nên hỗ trợ lập kế hoạch nộp bài đánh giá TMA1 đúng hạn.
- Toàn bộ 1.600 câu nằm trong `cau5_giai_thich_tung_sinh_vien.csv` (cột `giai_thich_cho_co_van`).
- Giải thích này mô tả sự liên quan trong dữ liệu. Nó không chứng minh nguyên nhân.

## Phương pháp, giả định và hạn chế

- **Mô hình**: logistic regression, chuẩn hóa đặc trưng, điền trung vị từ tập train. Ngưỡng chọn trên validation.
- **Tập test là kỳ 2014J**, khác với train (2013). Điểm AUC giảm từ 0,75 (validation) xuống 0,67 (test) có thể phản ánh khác biệt giữa các kỳ. Nên theo dõi thêm khi áp dụng cho kỳ mới.
- **Mục tiêu dự báo** gồm cả sinh viên rút sau ngày 28 (họ vẫn còn đăng ký lúc ngày 28). Mô hình không thể biết trước các lần rút muộn khi chưa có dấu hiệu trong dữ liệu đến ngày 28.
- **Chưa xác nhận** `tma1_score` chỉ chứa điểm của bài nộp đến ngày 28. Nếu không đúng, đặc trưng này có thể rò rỉ thông tin sau ngày 28.
- **Hiệu ứng nhỏ**: các chỉ báo đơn lẻ có AUC 0,59–0,67. Mô hình kết hợp đạt 0,67–0,75; đây là công cụ sàng lọc, không phải chẩn đoán.
- **Quan hệ là liên kết, không phải nhân quả**. Ví dụ, ít hoạt động không có nghĩa là hoạt động nhiều sẽ cải thiện kết quả.
- Phân tích không dùng giới tính, khuyết tật, vùng, IMD, độ tuổi trong mô hình. Nếu đưa các thuộc tính này vào, cần đánh giá công bằng riêng.

## File đầu ra

- `analysis.py`: toàn bộ mã phân tích (chạy lại được từ thư mục workspace).
- `cau1_so_sanh_3_nhom.csv`, `cau1_cap_nhom.csv`, `cau1_trung_vi_theo_tuan.csv`, `cau1_tuong_tac_4_tuan.png`
- `cau2_chi_bao_hoan_thanh_vs_khong.csv`, `cau2_auc_theo_tuan.csv`, `cau2_khac_biet_theo_tuan.png`
- `cau3_so_sanh_mo_hinh_validation.csv`, `cau3_ket_qua_test.csv`, `cau3_duong_cong_recall_test.csv`, `cau3_recall_theo_ti_le_gan_co.png`
- `cau4_hieu_qua_danh_sach_200.csv`, `cau4_trung_theo_module_ky.png`
- `cau5_giai_thich_tung_sinh_vien.csv`, `cau5_dac_trung_hang_dau.csv`
- `results.json`, `run_log.txt`
