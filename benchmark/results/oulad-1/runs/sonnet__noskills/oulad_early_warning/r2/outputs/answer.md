# Cảnh báo sớm OULAD (BBB + FFF, mốc cuối ngày 28)

**Dữ liệu & thiết lập.** 13.020 lượt đăng ký còn theo học đến ngày 28 (7 lượt đăng ký sau ngày 28 và 2.644 lượt đã hủy trước ngày 28 không nằm trong tập). "Không hoàn thành" = Fail hoặc Withdrawn (43,2%); Distinction được gộp vào Pass (label3). Chia theo thời gian: train = 2013B/2013J, validation = 2014B, test = 2014J (kỳ chưa từng thấy khi huấn luyện). Mọi đặc trưng chỉ dùng dữ liệu ngày 0–28 (kể cả hoạt động trước ngày bắt đầu và bài TMA1 nộp trước ngày 28).

## 1. Tương tác 4 tuần đầu theo nhóm kết quả
Median click/tuần (tuần 1→4): **Pass 59→50→60→43**, **Withdrawn 33→25→36→21**, **Fail 20→15→23→10**. Tổng 0–28: median Pass 257, Withdrawn 161, Fail 112 click; số ngày hoạt động trung bình Pass 13,3 – Withdrawn 9,9 – Fail 8,1. Thứ tự Pass > Withdrawn > Fail giữ nguyên ở cả 4 tuần. Fail là nhóm yếu nhất (không phải Withdrawn); 9% Fail và 7% Withdrawn không có hoạt động VLE nào trong 28 ngày (Pass: 1%). Tỷ lệ nộp TMA1 trước ngày 28: Pass 97%, Withdrawn 76%, Fail 75% — Withdrawn và Fail gần như giống nhau ở chỉ báo này. Xem `chart1_clicks_by_week.png`.

## 2. Chỉ báo khác biệt giữa hoàn thành và không hoàn thành
Tất cả chỉ báo chính đều khác biệt rất có ý nghĩa (Mann-Whitney, p < 1e-70; mẫu lớn nên p-value ít phân biệt — nên nhìn kích cỡ hiệu ứng AUC, 0,5 = không khác). Mạnh nhất: **số ngày hoạt động 0–28 (AUC 0,67; median 12 vs 7)**, click trang chủ (0,67), click diễn đàn (0,65), tổng click (0,65), nộp TMA1 đúng hạn (0,64), điểm TMA1 (0,61, median 80 vs 74). Yếu/không đáng kể: số tín chỉ, xu hướng thay đổi w1→w4 (AUC 0,52), số lần học lại.
**Khác biệt có ngay từ tuần 1** (click w1 AUC 0,63, p≈1e-144; median 59 vs 24) và hoạt động *trước khi khóa bắt đầu* cũng đã phân biệt (AUC 0,63). Từ tuần 2 mạnh nhất (0,65) rồi đi ngang; cộng dồn thêm tuần chỉ tăng AUC từ 0,63 (tuần 1) lên 0,65 (tuần 2) và 0,653 (tuần 4) — tức tuần 1–2 đã chứa gần hết tín hiệu. Lưu ý: đây là liên hệ, không phải nhân quả; mỗi chỉ báo riêng lẻ chỉ phân biệt vừa phải.

## 3. Dự báo được không, tốt đến đâu?
**Được, nhưng ở mức vừa phải và không đạt yêu cầu 70% recall một cách ổn định.**
- Logistic regression (đặc trưng gọn, có chuẩn hóa): **AUC test 0,688 (CI 95% bootstrap 0,670–0,704)**, AP 0,60 (tỷ lệ nền 37,8%). GBM tương đương (AUC 0,699). Baseline "ít click nhất" 0,652.
- Chọn ngưỡng trên validation để đạt recall 70% (cờ ~49% sinh viên, precision 66%). Áp lên test 2014J: **recall chỉ 65,3% (CI 63,0–67,8%)**, precision 51,5%, cờ 47,9% sinh viên → *trượt mục tiêu 70%* do tỷ lệ không hoàn thành test (37,8%) thấp hơn validation (46,5%) — phân phối trôi theo kỳ. Muốn đạt 70% trên test cần cờ ~52,8% sinh viên (precision ≈50%).
- Chênh lệch giữa module: FFF 2014J AUC 0,79, recall 74,8%; **BBB 2014J AUC 0,64, recall 54,0%** — mô hình yếu hơn nhiều ở BBB.
- Bắt Fail (63,7%) và Withdrawn (67,1%) ngang nhau; cũng cờ nhầm 41% Pass.
- Công bằng (test): recall khác nhau giữa nhóm — nữ 57% vs nam 73%; HE Qualification 54% vs Lower Than A Level 69%; Wales/Scotland ~56–57% vs South 77%. Cần theo dõi nếu dùng thật (xem `q3_fairness_test.csv`).
→ Kết luận: dùng như công cụ xếp hạng ưu tiên, không phải bộ lọc đủ chính xác. Nếu bắt buộc ≥70% recall thì phải chấp nhận cờ >50% cohort và precision ~50%.

## 4. Ưu tiên 200 sinh viên/module-kỳ
**Quy tắc đề xuất:** xếp theo điểm rủi ro từ mô hình logistic (xác suất không hoàn thành) giảm dần, lấy 200 đầu mỗi module-kỳ. Trên test 2014J (BBB + FFF = 400 sinh viên):
- **Trúng 305/400 = 76,2% precision** (nền 37,8% → lift 2,0×). BBB 122/200, FFF 183/200.
- So sánh: ít ngày hoạt động nhất 74,0% (296), ít click nhất 72,0% (288), GBM 76,5% (306), ngẫu nhiên 35,2% (141). Mô hình hơn quy tắc đơn giản ~2–4 điểm %; hơn quy tắc đơn giản nhưng không hơn GBM đáng kể → chọn LR vì giải thích được.
- Với k=100: precision 81%; k=300: 69,7% (`q4_rule_comparison.csv`).
- **Giới hạn quan trọng:** 400 liên hệ chỉ chạm **22,2% (305/1.376)** tổng số sinh viên sẽ không hoàn thành; dù hoàn hảo cũng tối đa 29%. Mục tiêu 70% recall không khả thi với năng lực 200/module-kỳ (cần ~1.900 liên hệ). Nếu tỷ lệ chuyển đổi giả định 14% thì ước tính chỉ ~43 sinh viên thực sự được cứu (305×0,14) — đây là giả định của nhà trường, chưa được kiểm chứng từ dữ liệu. Trong 400 người: 171 Fail, 134 Withdrawn, 90 Pass, 5 Distinction.
- Danh sách: `q4_priority_list_top200.csv` (cột `rank`, `score`, lý do, lời nhắn).

## 5. Đặc trưng đóng góp nhiều nhất & diễn đạt cho cố vấn
Đóng góp mỗi sinh viên = hệ số logistic × giá trị chuẩn hóa (tách theo từng đặc trưng; bỏ "module" khỏi lý do vì cố vấn không can thiệp được). Trong 400 người được ưu tiên, nguyên nhân thường gặp nhất trong top-3: ít ngày có hoạt động (313), nộp TMA1 trễ (253), chưa nộp TMA1 (226), điểm TMA1 thấp (173), học vấn đầu vào thấp (142). Nguyên nhân số 1: chưa nộp TMA1 (225) hoặc điểm TMA1 thấp (173).
Ví dụ lời nhắn (tự sinh cho từng người, cột `loi_nhan_cho_co_van`): *"Sinh viên có nguy cơ cao (điểm rủi ro 0,98), chủ yếu do: điểm TMA1 thấp; nộp TMA1 không đúng hạn; ít ngày có hoạt động. Nên liên hệ sớm để hỏi thăm khó khăn và hướng dẫn cách vào học."*
Lưu ý với cố vấn: đây là dấu hiệu thống kê, không chắc chắn — khoảng 1/4 người trong danh sách vẫn hoàn thành khóa; nên hỏi thăm chứ không kết luận.

## Giả định & hạn chế
- Tỷ lệ chuyển đổi 14% lấy từ `aq4_decision_params.json`, không kiểm chứng. Tập chỉ gồm người còn theo học ngày 28, nên kết quả không áp dụng cho người đã bỏ trước đó.
- `tma1_score` thiếu (nộp muộn/chưa nộp) được điền trung vị, cộng cờ `tma1_submitted_by_d28`. Chỉ một lần chia theo thời gian (1 kỳ test cho mỗi module) nên ước lượng có độ không chắc chắn theo kỳ.
- Mô hình chọn qua validation; không tinh chỉnh trên test.

Tệp: `chart1_clicks_by_week.png`, `chart2_recall_vs_capacity.png`, `q2_weekly_tests.csv`, `q3_metrics.json`, `q3_fairness_test.csv`, `q4_*.csv`; mã trong `scripts/`.
