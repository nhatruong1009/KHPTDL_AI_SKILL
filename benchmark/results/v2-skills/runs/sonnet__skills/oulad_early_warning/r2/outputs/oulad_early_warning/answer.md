# Hệ thống cảnh báo sớm OULAD (BBB + FFF), mốc quyết định cuối ngày 28

## Trả lời ngắn
1. **Ba nhóm khác nhau rõ ngay từ tuần 1.** Trung vị clicks 4 tuần đầu: Pass 257, Withdrawn 160,5, Fail 112. Fail và Withdrawn đều thấp hơn Pass, và Fail thấp nhất.
2. **26/27 chỉ báo khác biệt có ý nghĩa** giữa hoàn thành và không hoàn thành (Holm, p < 0,05); chỉ `registration_lead_days` không khác. Khác biệt **có từ tuần 1** và không tăng nhiều ở các tuần sau (hiệu ứng 0,26 → 0,30).
3. **Dự báo được, nhưng ở mức trung bình, và mục tiêu 70% KHÔNG đạt trên test.** AUC test 0,736 (95% CI 0,718–0,750). Ngưỡng chọn trên validation để đạt recall 70% chỉ cho recall **57,5%** trên test (CI 55,0–60,0%), precision 59,0%.
4. **Quy tắc ưu tiên:** xếp theo điểm rủi ro của mô hình, riêng từng module-kỳ, lấy 200 người đầu. Danh sách trúng **333/400 = 83,2%** là sinh viên không hoàn thành (nền 37,8%, gấp 2,2 lần). Danh sách này chỉ phủ **24,2%** trong 1.376 sinh viên không hoàn thành. Với 200 chỗ/module-kỳ thì **không thể** đạt recall 70%.
5. **Lý do hàng đầu cho từng sinh viên:** chưa nộp (hoặc nộp muộn) bài TMA1, rồi đến mức tương tác thấp. Danh sách kèm câu cho cố vấn nằm ở `q5_priority_list_with_reasons.csv`.

## Q1. Tương tác 4 tuần đầu theo nhóm (n: Pass 7.399 gồm cả Distinction; Fail 3.469; Withdrawn 2.152)
| Chỉ số | Pass | Withdrawn | Fail |
|---|---|---|---|
| Trung vị clicks tuần 1 | 59 | 33 | 20 |
| Trung vị clicks 0-28 | 257 | 160,5 | 112 |
| % không click nào ở tuần 1 | 12,3 | 22,4 | 27,4 |
| % không vào VLE lần nào trong 0-28 | 0,9 | 7,4 | 9,1 |
| % đã nộp TMA1 trước ngày 28 | 97,3 | 76,4 | 74,9 |
| Trung vị số ngày kể từ lần hoạt động cuối | 1 | 3 | 4 |

Kruskal-Wallis cho clicks 0-28: p < 1e-200. Pass so với Fail có rank-biserial 0,36, Pass so với Withdrawn 0,23, Fail so với Withdrawn −0,14. Withdrawn đang học đến ngày 28 nên vẫn tương tác hơn Fail một chút. Biểu đồ: `q1_tuong_tac_theo_nhom.png`. Số liệu: `q1_group_profile.csv`.

## Q2. Chỉ báo phân biệt hoàn thành và không hoàn thành
Mạnh nhất theo rank-biserial (|r|; 0 là không khác biệt, 1 là tách hoàn toàn):
- `active_days_0_28`: 0,35 (trung vị 12 so với 7 ngày).
- `clicks_homepage_0_28`: 0,33.
- `active_days_w4`: 0,31.
- `clicks_0_28`: 0,31 (trung vị 257 so với 127).
- `days_since_last_active_d28`: −0,30 (trung vị 1 so với 3 ngày).
- `tma1_on_time`: 0,27 (93,6% so với 66,5%).
- `tma1_submitted_by_d28`: 97,3% so với 75,5% đã nộp.

Hiệu ứng ở mức vừa (|r| ≈ 0,2–0,35). Với n ≈ 13.000, p rất nhỏ nên cần đọc theo độ lớn hiệu ứng, không đọc theo p.

**Theo tuần (clicks):** hiệu ứng tuần 1 là 0,26 (CI 0,25–0,28), tuần 2 là 0,30, tuần 3 là 0,26, tuần 4 là 0,29. Trung vị tuần 1 là 59 (hoàn thành) so với 24 (không hoàn thành). Tỷ lệ không click nào ở tuần 1 là 12,3% so với 25,5%. Trong cả 8 module-kỳ, khác biệt đều có ý nghĩa (p < 0,05) ở mọi tuần. Vậy **dấu hiệu đã xuất hiện từ tuần 1**, và các tuần sau củng cố thêm chứ không tạo ra khác biệt mới. Bảng: `q2_noncompleter_vs_completer.csv`, `q2_weekly_pooled.csv`, `q2_weekly_by_module_presentation.csv`. Biểu đồ: `q2_khac_biet_theo_tuan.png`.

## Q3. Dự báo Fail/Withdrawn bằng dữ liệu ngày 0–28
Target `target_noncompletion` (Fail hoặc Withdrawn = 1). Tỷ lệ nền: train 44,8%, validation 46,5%, test 37,8%. Dùng đúng cột `split` của dữ liệu: train 2013B và 2013J, validation 2014B, test 2014J.

| Mô hình | AUC val | AUC test | PR-AUC test (nền 0,378) |
|---|---|---|---|
| Dummy theo tỷ lệ nền | 0,50 | 0,50 | 0,378 |
| Quy tắc "ít click 0-28" | 0,647 | 0,652 | 0,541 |
| **Logistic (chọn, chính)** | 0,756 | **0,736** | 0,671 |
| HistGradientBoosting | 0,755 | 0,748 | 0,683 |
| Logistic cộng `tma1_score` (độ nhạy) | 0,771 | 0,691 | 0,610 |

- **Chọn mô hình:** theo AUC validation. Logistic và HistGB gần như hòa, nên giữ Logistic vì dễ giải thích cho Q5.
- **Ngưỡng recall 70% trên validation:** ngưỡng 0,445 cho recall 0,700 ở validation (precision 0,645, gắn cờ 50,5%).
- **Cùng ngưỡng trên test (chạm test một lần):** recall **0,575**, precision 0,590, specificity 0,757, gắn cờ 36,8% (1.341 người).
  - Ma trận nhầm lẫn: TP 791, FP 550, FN 585, TN 1.718.
  - **Mục tiêu "bắt ≥ 70%": KHÔNG đạt.**
  - Nguyên nhân có thể: tỷ lệ nền giảm từ 46,5% xuống 37,8% giữa validation và test, nên mô hình hiệu chỉnh lệch.
- **Muốn recall 70% trên test:** theo đường PR (`q3_q4_recall_precision.png`) precision chỉ còn khoảng 53%, và phải gắn cờ gần một nửa sinh viên.
- **Độ nhạy `tma1_score`:** điểm TMA1 không rõ ngày công bố nên bị loại khỏi mô hình chính. Thêm vào cũng **không cải thiện test** (AUC 0,691 so với 0,736), nên kết luận không đổi.
- **Kiểm tra theo nhóm (chỉ để kiểm tra, không dùng làm đặc trưng)** ở `q3_audit_by_group.csv`. Recall chênh nhiều giữa các nhóm: nữ 0,46 so với nam 0,69; học vấn "HE Qualification" 0,35 so với "Lower Than A Level" 0,65. Chênh lệch này một phần phản ánh tỷ lệ nền khác nhau (nữ 35%, nam 41%). Nhà trường nên theo dõi khi triển khai.

### Kiểm toán thời điểm biết của đặc trưng
| Đặc trưng | Biết khi nào | Quyết định |
|---|---|---|
| clicks/active_days theo tuần 1–4, tổng 0-28, n_sites, loại tài nguyên, `days_since_last_active_d28`, `no_vle_activity_0_28` | Ngày 0–28 | Dùng |
| `clicks_pre_start`, `active_days_pre_start`, `registration_lead_days`, `late_registration_1_28` | Trước hoặc trong ngày 28 | Dùng |
| `tma1_submitted_by_d28`, `tma1_on_time`, `tma1_days_before_deadline` | Theo tên cột là "đến d28"; ngày nộp nằm trong dữ liệu | Dùng (giả định đúng như tên cột) |
| `num_of_prev_attempts`, `studied_credits`, `highest_education_ord`, `seen_in_earlier_presentation`, module | Đăng ký, lịch sử trước đó | Dùng |
| `tma1_score` | Ngày công bố điểm không có trong dữ liệu | **Loại khỏi mô hình chính**, chỉ chạy độ nhạy |
| `flag_high_activity`, `days_observable_0_28` | Định nghĩa không rõ | Loại |
| `final_result`, `label3`, `flag_withdrawn_no_unreg_date`, `flag_unreg_date_not_withdrawn`, `date_unregistration` | Gắn với kết quả hoặc sau mốc | Loại |
| gender, age_band, disability, imd_band, region | Thuộc tính nhạy cảm | Không dùng làm đặc trưng, chỉ kiểm toán |

## Q4. Danh sách ưu tiên theo sức chứa 200 mỗi module-kỳ (test: BBB-2014J và FFF-2014J)
**Quy tắc:** trong từng module-kỳ, xếp giảm dần theo điểm rủi ro rồi lấy 200 người đầu. Không gộp hai module vì sức chứa tính riêng.

| Quy tắc (k = 200 mỗi module-kỳ, 400 liên hệ) | Trúng | Precision | Recall | Gấp mấy lần nền |
|---|---|---|---|---|
| **Điểm rủi ro mô hình** | 333 | **83,2%** | 24,2% | 2,2× |
| Ít click nhất 0-28 | 289 | 72,2% | 21,0% | 1,9× |
| Ngẫu nhiên (TB 20 lần) | 150 | 37,6% | 10,9% | 1,0× |

- **Theo từng module-kỳ:** BBB-2014J trúng 151/200 (75,5%) trong 635 người không hoàn thành; FFF-2014J trúng 182/200 (91,0%) trong 741 người.
- **Các mức k khác:** k = 100 cho precision 94,0% và recall 13,7%; k = 300 cho precision 74,3% và recall 32,4%.
- **Hiệu quả kỳ vọng:** với giả định chuyển đổi 14% (`assumed_conversion_rate` trong tham số, chưa kiểm chứng), danh sách k = 200 giữ lại khoảng 47 sinh viên (333 × 0,14). Quy tắc ít click cho khoảng 40, ngẫu nhiên khoảng 21.
- **Muốn bắt 70%:** cần khoảng 933 liên hệ ở BBB và 861 ở FFF, tức gấp 4–5 lần sức chứa (`q4_contacts_needed_for_70pct.csv`).
- **Kết luận:** với 200 chỗ, danh sách có độ chính xác cao nhưng phủ thấp. Nên coi đây là "những ca chắc chắn nhất", và cân nhắc kênh nhẹ hơn (tin nhắn tự động) cho nhóm rủi ro vừa.

Bảng: `q4_topk_summary.csv`, `q4_topk_by_module_presentation.csv`. Biểu đồ: `q3_q4_recall_precision.png`.

## Q5. Đóng góp của đặc trưng vào điểm rủi ro (200 người mỗi module-kỳ, 400 người)
Dùng mô hình logistic: đóng góp của mỗi đặc trưng là hệ số nhân với giá trị đã chuẩn hóa (so với sinh viên trung bình ở train), gộp theo chủ đề. Chủ đề đứng đầu cho từng sinh viên:
- Bài TMA1: 336/400 người.
- Mức tương tác tổng 4 tuần đầu: 41 người.
- Học vấn đầu vào: 16 người.
- Học lại: 6 người.
- Số tín chỉ: 1 người.

Trong danh sách có 76% chưa nộp TMA1. Đóng góp trung bình của TMA1 là 1,20 log-odds, cao hơn hẳn mức tương tác (0,28) hay module (0,27). Biểu đồ: `q5_dong_gop_rui_ro.png`.

Câu mẫu cho cố vấn (mỗi sinh viên một câu riêng trong `advisor_note`):
> "Sinh viên này được ưu tiên (điểm rủi ro 0,97) chủ yếu vì chưa nộp bài TMA1; chỉ có 0 lượt click trong 0 ngày học ở 4 tuần đầu; đã 29 ngày chưa vào học tính đến ngày 28. Nên liên hệ sớm để hỏi về khó khăn khi vào học và nhắc bài tiếp theo."

Lời nhắn cho cố vấn chỉ nêu các yếu tố hành vi, có thể hành động được. Module, học vấn đầu vào và số tín chỉ vẫn nằm trong các cột `reason1`–`reason3` của file CSV nhưng không đưa vào câu chữ.

## Phương pháp
- **Dữ liệu:** `aq1` (tuần, dùng cho Q1–2 và đối chiếu, 0 sai lệch với `aq2`), `aq2` (bảng chẩn đoán, 13.020 sinh viên-module-kỳ), `aq3_model_table` (bảng mô hình), `aq3_audit_attributes` (chỉ kiểm toán), `aq4_decision_params.json`.
- **Q1–2:** mô tả theo nhóm, Kruskal-Wallis, Mann-Whitney với rank-biserial, hiệu chỉnh Holm cho 27 chỉ báo, bootstrap 200 lần cho CI theo tuần. Dùng toàn bộ 13.020 dòng (mô tả, không phải dự báo).
- **Q3–5:** pipeline imputation trung vị, chuẩn hóa, log1p cho số click, hồi quy logistic (C = 0,3, class_weight balanced), so với HistGB và các baseline.
- **Chọn mô hình và ngưỡng:** trên validation. Test chỉ báo cáo một lần.
- **Mã nguồn:** `analysis.py`; log chạy: `run_log.txt`.

## Giả định và hạn chế
- Dữ liệu chỉ gồm sinh viên còn học đến ngày 28; không dự báo cho người đã rút trước ngày 28.
- "Không hoàn thành" = Fail hoặc Withdrawn; Pass đã gộp Distinction.
- Test chỉ có một kỳ (2014J, 3.644 sinh viên). Tỷ lệ nền thay đổi giữa các kỳ (44,8% → 46,5% → 37,8%) nên ngưỡng cần hiệu chỉnh lại theo từng kỳ.
- TMA1 "nộp trước d28" được giả định đúng như tên cột. Không biết hạn nộp có rơi trước ngày 28 hay không, nên "chưa nộp" có thể gộp cả người chưa tới hạn.
- 392 sinh viên xuất hiện ở nhiều kỳ. Tách theo kỳ (đúng thiết kế dữ liệu) nên không rò rỉ giữa train và test về kỳ, nhưng cùng một người có thể có mặt ở cả hai bên.
- Đây là quan hệ thống kê, không chứng minh nguyên nhân. Đóng góp đặc trưng mô tả vì sao mô hình cho điểm cao, không phải vì sao sinh viên bỏ học.
- Con số 14% chuyển đổi là giả định từ tệp tham số, không phải kết quả đo.
