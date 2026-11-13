# Hệ thống cảnh báo sớm OULAD (mốc cuối ngày 28) — BBB & FFF, 2013B–2014J

## Trả lời ngắn
1. **Tương tác 4 tuần đầu:** Pass > Withdrawn > Fail ở cả 4 tuần. Trung vị click/tuần của Pass 43–60, Withdrawn 21–36, Fail 10–23. Khoảng cách đã có từ tuần 1.
2. **Chỉ báo khác biệt:** 26/30 chỉ báo khác biệt có ý nghĩa và đủ lớn (FDR < 0,01, |Cliff's delta| ≥ 0,1) giữa hoàn thành và không hoàn thành. Mạnh nhất: số ngày vào học 0–28 (δ=0,35), click trang chủ, click diễn đàn, số ngày chưa vào học tính đến ngày 28, nộp TMA1 đúng hạn. **Khác biệt xuất hiện ngay từ tuần 1** (δ≈0,26) và tăng nhẹ đến δ≈0,35 khi gộp 4 tuần. Cả tuần 0 (trước khi khóa bắt đầu) cũng đã khác (δ=0,26 với click trước khóa).
3. **Dự báo được, nhưng chỉ ở mức vừa phải và chưa đạt 70% một cách ổn định.** Mô hình GradientBoosting, kiểm tra trên kỳ 2014J chưa từng thấy: AUC 0,705 (KTC 95% 0,688–0,721). Với ngưỡng chọn trên validation để nhắm recall 70%, trên test chỉ đạt **recall 67,8%**, precision 51,3%, gắn cờ 49,9% sinh viên. Mô hình tốt hơn quy tắc "ít click nhất" (AUC 0,652) nhưng không vượt trội.
4. **Danh sách 200 người/module-kỳ:** xếp theo điểm rủi ro giảm dần. Trên 2014J: **BBB trúng 127/200 (63,5%), FFF trúng 180/200 (90%)**, tổng 307/400 (76,8%; ngẫu nhiên khoảng 150/400). Nhưng 200 người chỉ phủ **20% (BBB) và 24% (FFF)** số sinh viên không hoàn thành — không thể đạt mục tiêu 70% với 200 người. Để bắt 70% cần liên hệ ~1.051 người (BBB) và ~836 người (FFF), tức 59% và 45% số sinh viên.
5. **Giải thích từng sinh viên:** xem `q5_priority_list_with_explanations.csv` (cột `explanation_vi`). Lý do số 1 là bài TMA1 đầu tiên ở 399/400 người (288/400 chưa nộp), kế đến là hoạt động từng tuần thấp, ít dùng nội dung chính, lâu không vào học.

## Bằng chứng
### Q1 — ba nhóm kết quả (label3: Pass gồm cả Distinction; n = 7.399 / 3.469 / 2.152)
| Chỉ số 0–28 ngày (trung vị) | Pass | Fail | Withdrawn |
|---|---|---|---|
| Click | 257 | 112 | 160,5 |
| Ngày vào học | 12 | 7 | 9 |
| Đã nộp TMA1 (tỷ lệ) | 97% | 75% | 76% |
| Số ngày chưa vào học tính đến ngày 28 | 1 | 4 | 3 |

Tỷ lệ sinh viên không click nào trong tuần: Pass 8–12%, Fail 25–34%, Withdrawn 20–27%. Kruskal-Wallis p < 0,001 mọi tuần; Pass–Fail δ≈0,30–0,34, Pass–Withdrawn δ≈0,19–0,24, Fail–Withdrawn δ≈0,11–0,13. Ghi chú: Withdrawn (rút lui) ban đầu hoạt động nhiều hơn Fail nhưng vẫn thấp hơn Pass rõ rệt; cả hai đã tách khỏi Pass từ tuần 1. (`q1_*.csv`, `q1_tuong_tac_theo_nhom.png`)

### Q2
Bảng đầy đủ: `q2_indicator_tests.csv`, `q2_by_week.csv`, biểu đồ `q2_chi_bao_khac_biet.png`. Dấu của khác biệt giống nhau ở cả 8 module-kỳ cho 26 chỉ báo có ý nghĩa. Không có ý nghĩa thực tế: `clicks_change_w1_w4`, `registration_lead_days`, `studied_credits`, `num_of_prev_attempts` (|δ|<0,1). Vì n lớn, p-value gần như luôn nhỏ, nên tiêu chí "có ý nghĩa" dựa chủ yếu vào cỡ hiệu ứng.

### Q3
| Mô hình (test = 2014J) | AUC | Recall | Precision | % gắn cờ |
|---|---|---|---|---|
| GradientBoosting | 0,705 | 67,8% | 51,3% | 49,9% |
| Logistic L2 | 0,685 | 63,7% | 52,2% | 46,1% |
| Baseline: ít click 0–28 | 0,652 | 70,4% | 45,2% | 58,8% |

Tỷ lệ không hoàn thành ở test là 37,8% (validation 46,5%) nên ngưỡng chọn trên validation lệch nhẹ. Để đạt đúng 70% recall trên test cần gắn cờ ~51%+ sinh viên với precision ~51%. Kiểm toán nhóm (`q3_group_audit.csv`): recall thấp hơn ở nhóm học vấn A-Level (59,5%) và HE (61,9%) so với "Lower Than A Level" (74,6%); nữ 64,3% so với nam 71,1%. Các nhóm này chỉ dùng để kiểm tra, không đưa vào mô hình.

### Q4 (test 2014J; K = 100 / 200 / 300 xem `q4_topk.csv`)
| Module | K | Mô hình | Quy tắc: chưa nộp TMA1 rồi ít click | Ít click nhất | Ngẫu nhiên |
|---|---|---|---|---|---|
| BBB | 200 | 127 | 137 | 121 | 70 |
| FFF | 200 | 180 | 178 | 168 | 80 |

Quy tắc đề xuất: **xếp theo điểm rủi ro của mô hình, lấy 200 người cao nhất mỗi module-kỳ** (đơn giản hơn để vận hành: ưu tiên người chưa nộp TMA1, rồi ít click — quy tắc này ngang hoặc nhỉnh hơn mô hình trong BBB, chênh lệch 10 người trên một kỳ test duy nhất nên chưa kết luận được ai hơn). Nếu giả định tỷ lệ hỗ trợ thành công 14% (từ tham số đề bài, chưa kiểm chứng), 200 người/module-kỳ cứu được khoảng 18 (BBB) + 25 (FFF) sinh viên. Dữ liệu không có thông tin về can thiệp, nên không đo được sinh viên nào *được lợi* từ liên hệ (uplift).

### Q5 — ví dụ lời giải thích cho cố vấn
> "Sinh viên này được ưu tiên chủ yếu vì chưa nộp bài kiểm tra TMA1 đầu tiên; hoạt động từng tuần thấp hoặc giảm dần (tuần 1-4: 0/0/0/0 lượt click); ít dùng nội dung học chính. Nên liên hệ sớm để hỏi về khó khăn và giúp bắt kịp tiến độ."

Phương pháp: với mỗi sinh viên, thay từng nhóm đặc trưng bằng giá trị điển hình (trung vị train) và đo mức giảm của điểm rủi ro; 3 nhóm giảm nhiều nhất là lý do. Đây là mối liên quan, không phải nguyên nhân. (`q5_ly_do_uu_tien.png`)

## Phương pháp
- Dữ liệu: `aq1` (tuần × sinh viên), `aq2` (bảng chẩn đoán), `aq3_model_table`, `aq3_audit_attributes`. 13.020 lượt đăng ký còn theo học đến ngày 28, không trùng khóa.
- Chia theo thời gian: train = 2013B/2013J (6.795), validation = 2014B (2.581), test = 2014J (3.644). Chọn mô hình và ngưỡng chỉ trên validation; test chỉ đánh giá một lần.
- Loại khỏi mô hình: `flag_withdrawn_no_unreg_date`, `flag_unreg_date_not_withdrawn`, `date_registration_missing` (cờ kiểm toán, có nguy cơ rò rỉ), `final_result`, `flag_high_activity`, và các cột nhận diện. Điểm TMA1 thiếu được điền trung vị + cờ thiếu.
- Thống kê: Mann-Whitney / Kruskal-Wallis, cỡ hiệu ứng Cliff's delta, hiệu chỉnh Benjamini-Hochberg. Mã: `analysis.py`, `charts.py`.

## Giả định và hạn chế
- "Không hoàn thành" = Fail hoặc Withdrawn; Distinction tính là hoàn thành.
- Giả định `tma1_score` và `tma1_submitted_by_d28` đã biết trước cuối ngày 28 (theo tên cột). Nếu điểm TMA1 chưa được chấm kịp vào ngày 28 thì cần bỏ cột này; mô hình sẽ yếu hơn.
- Chỉ một kỳ test (2014J) với 2 module; tỷ lệ nền thay đổi theo kỳ (37,8% so với 46,5%), nên số liệu có độ bất định lớn, nhất là khi so sánh các quy tắc xếp hạng gần nhau.
- Tập chỉ gồm sinh viên còn theo học đến ngày 28; những người rút trước ngày 28 (2.644) không thuộc phạm vi hệ thống.
- Quan sát, không phải nhân quả. Click thấp có thể là hệ quả của việc sắp bỏ học, chứ không phải nguyên nhân.
