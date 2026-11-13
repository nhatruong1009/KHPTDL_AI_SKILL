# Hệ thống cảnh báo sớm OULAD (BBB + FFF, mốc cuối ngày 28)

**Trả lời ngắn:** Dự báo được, nhưng chỉ ở mức vừa phải (AUC test 0,71, so với 0,50 của dự đoán theo tỷ lệ nền). Mục tiêu "bắt ≥70% sinh viên không hoàn thành" **đạt được về mặt mô hình** (recall test 70,4%, KTC95% 68,0–72,7%), nhưng phải gắn cờ **53% sinh viên với độ chính xác chỉ 50%**. Với giới hạn **200 sinh viên/module-kỳ** thì mục tiêu 70% **không thể đạt**: danh sách top-200 trúng **80,5%** (322/400) nhưng chỉ bắt được **23,4%** (322/1.376) số sinh viên không hoàn thành; trần lý thuyết là 27–32%.

Định nghĩa: "không hoàn thành" = Fail hoặc Withdrawn (`target_noncompletion`); "hoàn thành" = Pass + Distinction. Quần thể: 13.020 lượt đăng ký còn học đến hết ngày 28 (tỷ lệ không hoàn thành 43,2%).

## Q1. Ba nhóm khác nhau thế nào trong 4 tuần đầu?
Pass > Withdrawn > Fail ở cả 4 tuần, cả click lẫn số ngày hoạt động (Kruskal-Wallis p < 1e-150 mọi tuần; n: Pass 7.399, Fail 3.469, Withdrawn 2.152).

| | Pass | Withdrawn | Fail |
|---|---|---|---|
| Click trung vị tuần 1 | 59 | 33 | 20 |
| Click trung vị tuần 4 | 43 | 21 | 10 |
| Ngày hoạt động TB tuần 1 / tuần 4 | 3,15 / 3,26 | 2,42 / 2,33 | 2,02 / 1,90 |
| % không click tuần 1 / tuần 4 | 12% / 12% | 22% / 27% | 27% / 34% |
| Trung vị click 0–28 | 257 | 160,5 | 112 |
| Nộp TMA1 trước ngày 28 | 97,3% | 76,4% | 74,9% |

Fail thấp hơn cả Withdrawn (AUC Fail>Withdrawn về click = 0,43): sinh viên sau này Fail là nhóm ít tương tác nhất ngay từ đầu. Pass luôn ổn định hoặc nhích lên, hai nhóm kia thấp hơn và tuần 4 tụt thêm. Biểu đồ: `q1_weekly_by_outcome.png`; bảng: `q1_profile_by_outcome.csv`.

## Q2. Chỉ báo nào khác biệt, từ tuần nào?
Mọi chỉ báo hoạt động đều khác biệt có ý nghĩa (Mann-Whitney, hiệu chỉnh Holm, p_holm < 0,001), và **khác biệt đã có từ tuần 1**, thậm chí trước ngày 0 (`clicks_pre_start`). Độ mạnh (AUC, 0,5 = không phân biệt; chiều "hoàn thành cao hơn"):

- Mạnh nhất (AUC theo chiều "hoàn thành cao hơn"): số ngày hoạt động 0–28 (0,674), click trang chủ (0,665), số ngày hoạt động tuần 4 (0,656), click tổng 0–28 (0,654), click diễn đàn (0,652), số ngày kể từ lần hoạt động cuối (0,651, chiều ngược), nộp TMA1 đúng hạn (0,635).
- Tuần 1 đã có: `clicks_w1` AUC 0,630, `active_days_w1` 0,631. Các tuần sau chỉ nhỉnh hơn chút (click tuần 2–4: 0,630–0,649; ngày hoạt động tuần 2–4: 0,648–0,657), nên tín hiệu **xuất hiện ngay tuần 1** và tăng nhẹ theo thời gian, không phải đến tuần sau mới có.
- Hầu như không khác: `registration_lead_days` (0,499, p = 0,86); `studied_credits`, `num_of_prev_attempts` rất nhỏ (|AUC−0,5| ≤ 0,05).
- Tỷ lệ không hoàn thành khi 0 click: 61% (tuần 1, n = 2.345) → 66% (tuần 2) → 69% (tuần 3) → 66% (tuần 4), so với 37–39% nếu có click.
- Nhất quán ở cả 8 module-kỳ (`q2_consistency_by_module_presentation.csv`). Chỉ là *liên quan*, không chứng minh nguyên nhân. Effect size nhỏ-vừa, không có chỉ báo nào tách bạch một mình.

Chi tiết: `q2_indicators.csv`, `q2_indicator_effects.png`. (Các AUC ở trên đọc từ file đó.)

## Q3. Dự báo từ dữ liệu ngày 0–28
Dùng đúng cách chia của dữ liệu: train = 2013B+2013J, validation = 2014B, test = 2014J (dùng một lần). Chọn mô hình và ngưỡng trên validation (ngưỡng cho recall ≥70%).

| Mô hình | AUC val | AUC test | PR-AUC test | Recall test | Precision test | Tỷ lệ gắn cờ |
|---|---|---|---|---|---|---|
| Dummy (tỷ lệ nền 37,8%) | 0,500 | 0,500 | 0,378 | – | – | – |
| **Logistic (chọn)** | 0,731 | 0,713 | 0,644 | **70,4%** | 50,1% | 53% |
| HistGB | 0,730 | 0,723 | 0,664 | 66,5% | 51,8% | 48,5% |

Logistic được chọn vì AUC validation ngang HistGB (chênh 0,001) mà giải thích được. Ma trận nhầm lẫn test: bắt 969 / bỏ sót 407 sinh viên không hoàn thành; 964 báo động nhầm. Mục tiêu 70%: **đạt trên test** (KTC 68,0–72,7% nên không dư địa), nhưng cái giá là gắn cờ hơn một nửa số sinh viên, nên **không khả thi với 200 người/module-kỳ**. Tỷ lệ nền test (37,8%) thấp hơn train (44,8%) và validation (46,5%); recall vẫn rơi đúng 70% có thể là may mắn một phần (KTC 68–73%).

Độ nhạy: thêm `tma1_score` (không rõ ngày công bố điểm nên chỉ chạy thử, không dùng chính) **không cải thiện** trên test (Logistic AUC 0,665, thấp hơn) → kết luận chính không đổi.

Kiểm toán nhóm (ngưỡng đó, test; chỉ để kiểm sai số, không là biến dự báo): recall dao động 63–81% theo nhóm (một số nhóm nhỏ, vài trăm người); thấp hơn ở sinh viên có khuyết tật (64%) và tuổi 35–55 (65%) so với 70–73% ở nam, nữ, tuổi 0–35 và nhóm không khuyết tật; tỷ lệ báo động nhầm cao hơn ở nữ (48% so với 35% ở nam). Xem `q3_fairness_audit_test.csv`. Cần theo dõi khi triển khai.

## Q4. Ưu tiên ai khi chỉ liên hệ được 200/module-kỳ?
Quy tắc: **xếp hạng theo điểm rủi ro của mô hình trong từng module-kỳ và lấy 200 người cao nhất** (test 2014J):

| Module-kỳ | Số SV | Không hoàn thành | Trúng trong top-200 | Precision | Recall | Lift so với nền |
|---|---|---|---|---|---|---|
| BBB 2014J | 1.786 | 635 (35,6%) | 146 | 73,0% | 23,0% | 2,05 |
| FFF 2014J | 1.858 | 741 (39,9%) | 176 | 88,0% | 23,8% | 2,21 |
| Gộp | 3.644 | 1.376 | 322 | 80,5% | 23,4% | 2,1 |

- So với quy tắc đơn giản: "chưa nộp TMA1 rồi ít click nhất" trúng 78,8% (315/400), "ít ngày hoạt động nhất" 74,2%, "ít click nhất" 72,0%. Mô hình chỉ hơn quy tắc TMA1 khoảng 1,7 điểm %; **quy tắc đơn giản gần như tốt ngang mô hình** ở độ dài 200.
- Với K=100: 92,0% trúng (recall 13,4%); K=300: 73,2% trúng (recall 31,9%).
- Để đạt 70% recall cần danh sách 1.032 (BBB) và 888 (FFF) người, gấp 4,4–5,2 lần năng lực. Nếu giữ 200, nên coi mục tiêu là "độ chính xác cao", không phải "bao phủ 70%".
- Nếu dùng tỷ lệ chuyển đổi giả định 14% (từ tham số của nhà trường, chưa kiểm chứng), 322 người trúng tương ứng khoảng 45 sinh viên được hỗ trợ thành công, đó là ước tính theo giả định, không phải đo lường.

Danh sách: `q4_q5_priority_list_test_2014J.csv`; kết quả K khác: `q4_capacity_results.csv`; biểu đồ `q4_top200_precision.png`.

## Q5. Yếu tố đóng góp nhiều nhất cho từng sinh viên ưu tiên
Điểm rủi ro là hồi quy logistic, nên đóng góp mỗi đặc trưng = hệ số × (giá trị chuẩn hóa), gom thành 6 nhóm dễ hiểu. Trong danh sách top-200 của mỗi module-kỳ, yếu tố số 1 là **bài TMA1** với 354/400 người (BBB 154, FFF 200; toàn bộ 200 người FFF đều chưa nộp TMA1), còn lại là click học liệu (29, đều ở BBB), lịch sử học lại/tải tín chỉ (14) và số ngày vào học (3). Trung vị của danh sách: ~33–34 click và 2,5–3 ngày hoạt động trong 28 ngày.

Mẫu diễn đạt cho cố vấn (cột `explanation_vi` có sẵn cho cả 400 sinh viên, mỗi người một câu riêng theo 3 yếu tố đóng góp lớn nhất; dưới đây là ví dụ thật):

> *"Sinh viên này được ưu tiên chủ yếu vì chưa nộp bài TMA1 đầu tiên, chỉ có 68 lượt click trong 28 ngày đầu và chỉ vào học 4 ngày. Đây là những dấu hiệu thường đi cùng với nguy cơ bỏ học hoặc trượt, không chắc là nguyên nhân; nên liên hệ hỏi thăm khó khăn."*

## Phương pháp
- Bảng `aq3_model_table.csv` (13.020 dòng, khóa module-kỳ-sinh viên duy nhất), tách theo cột `split` có sẵn. Kiểm toán thời điểm biết của từng đặc trưng: `feature_timing_audit.csv`. Loại `tma1_score` (không biết ngày công bố điểm), `flag_high_activity` (không rõ định nghĩa), nhóm nhạy cảm (giới tính, tuổi, khuyết tật, IMD, vùng) và `highest_education_ord` (thận trọng).
- Tuần 1–4 = ngày 1–28; `clicks_0_28` có thêm ngày 0 (đối chiếu với `aq1_student_week.csv`: tổng 4 tuần khớp từng sinh viên).
- Mã: `q1_q2.py`, `model.py` (chạy lại bằng `python outputs/oulad-early-warning/<file>.py` từ thư mục gốc).

## Lưu ý
- Quần thể chỉ gồm người còn học đến ngày 28 (2.644 người đã hủy đăng ký trước đó nằm ngoài), nên tỷ lệ Withdrawn ở đây thấp hơn toàn bộ.
- `tma1_on_time = 0` gộp cả "nộp muộn" và "chưa nộp"; dữ liệu không có hạn nộp, nên "chưa nộp" có thể chưa đến hạn với một số sinh viên. Trong FFF, 100% top-200 chưa nộp TMA1: cần kiểm tra hạn TMA1 của FFF trước khi dùng làm lý do liên hệ.
- Test chỉ là một kỳ (2014J, 3.644 SV, hai module); hiệu năng ở kỳ khác có thể khác. Quan sát, không phải nhân quả: chưa biết liên hệ có thực sự giúp sinh viên ở lại hay không.
- Với danh sách 200, bản đã chọn gần như tương đương quy tắc TMA1 + ít click, vì vậy mô hình bổ sung ít so với quy tắc đơn giản.
