# Cảnh báo sớm sinh viên không hoàn thành (OULAD, BBB + FFF, mốc cuối ngày 28)

**Dữ liệu:** 13.020 lượt đăng ký còn theo học đến ngày 28 (mỗi sinh viên được xác định bằng module + kỳ + id_student, vì một id có thể xuất hiện ở nhiều khóa). Tỉ lệ không hoàn thành (Fail + Withdrawn) là 43,2%.
**Cách chia dữ liệu theo thời gian:** train = 2013B + 2013J; validation = 2014B; test = 2014J (3.644 sinh viên). Mô hình chỉ học từ train, chọn ngưỡng trên validation và đánh giá một lần trên test. Câu 1–2 là mô tả và kiểm định trên toàn bộ dữ liệu, không dùng để huấn luyện.

## 1. Tương tác 4 tuần đầu của Pass / Fail / Withdrawn
Pass tương tác nhiều nhất, **Fail thấp nhất**, Withdrawn nằm giữa. Khoảng cách có ngay từ tuần 1 và duy trì suốt 4 tuần (Kruskal-Wallis p < 1e-150 ở mọi tuần).

| | Pass | Withdrawn | Fail |
|---|---|---|---|
| Trung vị click tuần 1 / 2 / 3 / 4 | 59 / 50 / 60 / 43 | 33 / 24,5 / 36 / 21 | 20 / 15 / 23 / 10 |
| Số ngày hoạt động TB tuần 1 → 4 | 3,2 / 3,1 / 3,5 / 3,3 | 2,4 / 2,3 / 2,6 / 2,3 | 2,0 / 1,8 / 2,2 / 1,9 |
| Trung vị tổng click 0–28 | 257 | 160,5 | 112 |
| % không click tuần 1 | 12% | 22% | 27% |
| % chưa nộp TMA1 đến ngày 28 | 2,7% | 23,6% | 25,1% |

Withdrawn và Fail giống nhau ở điểm đều có tỉ lệ chưa nộp TMA1 cao (~24–25%, so với 2,7% ở Pass). Không nhóm nào cho thấy "sụt dốc" rõ rệt trong 4 tuần. Khác biệt là mức nền thấp ngay từ đầu. Hình: `q1_weekly.png`; bảng: `q1_group_summary.csv`.

## 2. Chỉ báo khác biệt giữa hoàn thành và không hoàn thành
Dùng Mann-Whitney, hiệu chỉnh Holm cho 32 chỉ báo, kèm Cliff's delta làm độ lớn hiệu ứng và kiểm tra cùng chiều trong 8 nhóm module-kỳ. **31/32 chỉ báo khác biệt có ý nghĩa** (Holm p < 0,01) và cùng chiều ở cả 8 nhóm. Ngoại lệ là `registration_lead_days` (p = 0,86). Với n lớn, ý nghĩa thống kê là điều dễ đạt, nên cần nhìn độ lớn hiệu ứng:

- **Mạnh nhất (|delta| ≈ 0,26–0,35):** `active_days_0_28` (trung vị 7 so với 12), `clicks_homepage_0_28`, `clicks_0_28` (127 so với 257), `clicks_forumng_0_28`, `days_since_last_active_d28` (3 so với 1 ngày), `tma1_on_time` (đúng hạn 66,5% so với 93,6%).
- **Trung bình (0,17–0,24):** n_sites, TMA1 nộp/điểm/số ngày trước hạn, hoạt động trước khai giảng, học vấn đầu vào.
- **Yếu (< 0,1):** số lần học lại, tín chỉ, `no_vle_activity_0_28`, `clicks_change_w1_w4`.

**Từ tuần nào?** Từ **tuần 1**. Mọi chỉ báo theo tuần đều có ý nghĩa ngay tuần 1 (AUC tuần 1: click 0,630, số ngày hoạt động 0,631). AUC tăng nhẹ lên 0,645–0,657 ở tuần 2–4. Tức là tín hiệu có sớm nhưng không mạnh lên nhiều. Xem `q2_indicator_tests.csv` và `q2_weekly_auc.png`.

## 3. Dự báo bằng dữ liệu ngày 0–28
Có dự báo được, nhưng **chỉ ở mức vừa phải, và chưa đạt mục tiêu 70% bắt được ở mức chính xác tốt**. Mô hình là hồi quy logistic (C = 0,1), dùng các đặc trưng hoạt động VLE, TMA1 và hồ sơ đăng ký. Không dùng nhân khẩu học hay `final_result`.

| Chỉ số (test 2014J, tỉ lệ nền 37,8%) | Giá trị |
|---|---|
| AUC (hồi quy logistic) | **0,685** (validation 0,760) |
| AUC (gradient boosting, để so sánh) | 0,708 (validation 0,764) |
| Quy tắc đơn giản: ít ngày hoạt động | AUC 0,661 |
| BBB / FFF | 0,620 / 0,787 |

Ngưỡng chọn trên validation để bắt 70% cho recall **66,7%** trên test (hụt 3,3 điểm do phân phối trôi giữa các kỳ), với precision 51,9% và gắn cờ 48,5% sinh viên.

| Mục tiêu recall (đặt trên chính test) | Tỉ lệ SV bị gắn cờ | Precision |
|---|---|---|
| 50% | 35% | 54% |
| 60% | 43% | 53% |
| **70%** | **52%** | **51%** |
| 80% | 63% | 48% |

Để bắt 70% cần gắn cờ hơn một nửa số sinh viên, mà chỉ ~51% trong số đó thật sự không hoàn thành (lift 1,36). Hiệu năng giảm so với validation (AUC 0,76 xuống 0,685), nên nên kỳ vọng ở mức test. Mô hình dự báo FFF tốt hơn BBB rõ rệt. Xem `q3_model_metrics.csv`, `q3_recall_precision_tradeoff.csv`, `q3_tradeoff.png`.

## 4. Ưu tiên khi chỉ liên hệ được 200 sinh viên mỗi module-kỳ
**Quy tắc:** xếp hạng theo điểm rủi ro của mô hình ở ngày 28 và liên hệ 200 người cao nhất mỗi module-kỳ (2014J: BBB và FFF, tổng 400 người). Danh sách đầy đủ ở `q5_priority_list_with_explanations.csv`.

| Module (2014J) | Số SV | Không hoàn thành | Trúng trong top 200 | Precision | Recall | Chọn ngẫu nhiên | Quy tắc ít ngày hoạt động |
|---|---|---|---|---|---|---|---|
| BBB | 1.786 | 635 | 104 | 52% | 16,4% | ~70 | 126 |
| FFF | 1.858 | 741 | 176 | 88% | 23,8% | ~80 | 171 |
| Tổng | 3.644 | 1.376 | **280** | **70%** | **20,3%** | ~150 | 297 |

- Danh sách trúng 280/400 sinh viên không hoàn thành (precision 70%), cao gần gấp đôi chọn ngẫu nhiên (37,8%).
- **Với giới hạn 200, mục tiêu 70% là bất khả thi về số học.** Trần recall chỉ là 200/635 = 31,5% (BBB) và 200/741 = 27% (FFF), kể cả khi mọi người trong danh sách đều đúng. Thực tế đạt 20,3%. Muốn bắt 70% cần liên hệ khoảng 1.880 sinh viên, gấp ~4,7 lần nhân lực hiện có.
- **Ở BBB, quy tắc đơn giản (ít ngày hoạt động nhất) trúng 126, hơn mô hình (104).** Ở FFF mô hình hơn nhẹ (176 so với 171). Nhìn tổng, mô hình (280) kém quy tắc đơn giản (297), nên lợi thế của mô hình phức tạp là chưa được chứng minh. Quy tắc "ít ngày hoạt động" đơn giản hơn, dễ giải thích và cho kết quả tương đương trong top 200, nên nên cân nhắc. Tôi vẫn dùng mô hình cho danh sách và giải thích vì chỉ mô hình cho giải thích theo từng sinh viên (câu 5).
- Độ nhạy theo năng lực: top 100/module trúng 144 (precision 72%, recall 10,5%); top 300 trúng 398 (precision 66%, recall 28,9%).
- Với tỉ lệ chuyển đổi giả định 14% (theo `aq4_decision_params.json`), danh sách 400 người ước tính giúp được khoảng **39 sinh viên** (0,14 × 280).
- **Kiểm tra công bằng** (`q4_fairness_audit.csv`): tỉ lệ được chọn khá đều theo giới tính, tuổi, IMD. Điểm đáng chú ý: sinh viên có trình độ "Lower Than A Level" được chọn nhiều hơn (16,7%) và nhóm HE Qualification gần như không (1,2%), phản ánh tỉ lệ không hoàn thành nền khác nhau (45,7% so với 26,5%) và việc mô hình dùng trình độ đầu vào. Nên rà soát trước khi triển khai.

## 5. Đặc trưng đóng góp nhiều nhất vào điểm rủi ro
Với mô hình logistic, đóng góp của mỗi đặc trưng bằng hệ số nhân với độ lệch chuẩn hóa so với trung bình train, rồi cộng theo 9 nhóm đặc trưng tương quan với nhau. Trong 400 sinh viên ưu tiên, **399 người có nhóm "Bài TMA1" (chưa nộp hoặc nộp trễ/điểm thấp) đóng góp lớn nhất**. Hoạt động VLE (số ngày hoạt động, tổng click) thường xếp thứ hai và ba. Từng sinh viên có 3 nhóm hàng đầu và lời nhắn sẵn trong cột `loi_nhan_cho_co_van` của CSV.

Mẫu diễn đạt cho cố vấn (ví dụ thật từ danh sách):
> "Sinh viên này được ưu tiên liên hệ chủ yếu vì: chưa nộp bài TMA1; chỉ vào học 2 ngày trong 4 tuần đầu (trung vị toàn kỳ là 9). Đây là những dấu hiệu thường gặp ở sinh viên về sau không hoàn thành khóa, nên cố vấn hãy hỏi thăm sớm về khó khăn và giúp bạn ấy bắt kịp bài."

**Lưu ý:** đó là những dấu hiệu liên quan chứ không chứng minh nguyên nhân. Danh sách thực chất là "chưa nộp TMA1 và ít vào học", nên sinh viên có hoạt động thấp nhưng đã nộp TMA1 có thể bị bỏ sót.

## Giả định và hạn chế
- Dùng đúng bảng đã chuẩn bị, không tự dựng lại từ dữ liệu thô. Giá trị TMA1 thiếu được xử lý bằng trung vị của train kèm biến đánh dấu thiếu.
- Chỉ có một kỳ test (2014J) và hai module, nên số liệu có sai số mẫu. AUC giảm từ validation sang test cho thấy phân phối trôi theo kỳ.
- Câu 1–2 gộp mọi kỳ, nên tính độc lập giữa các quan sát chỉ gần đúng (một số sinh viên học nhiều khóa). Kết quả đều cùng chiều trong 8 nhóm module-kỳ.
- Mã nguồn: `scripts/a.py`.
