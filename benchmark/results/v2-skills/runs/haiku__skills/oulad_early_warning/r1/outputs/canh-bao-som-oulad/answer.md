# Cảnh báo sớm sinh viên OULAD (BBB, FFF; 2013B–2014J): trả lời 5 câu hỏi

**Kết luận nhanh:** Dữ liệu 28 ngày đầu đủ để phân biệt tương đối sinh viên có nguy cơ không hoàn thành (AUC 0.72 trên tập test). Mục tiêu bắt ít nhất 70% sinh viên không hoàn thành **chỉ đạt được khi cảnh báo khoảng 54% số sinh viên**, không đạt với ngưỡng cố định chốt trên validation (64%). Với giới hạn 200 sinh viên mỗi module-kỳ, danh sách ưu tiên có 80% trúng, nhưng chỉ bắt được 23% tổng số sinh viên không hoàn thành.

## Phạm vi và định nghĩa

- **Quần thể:** 13,020 lượt đăng ký còn học đến cuối ngày 28 (`aq3_model_table.csv`). 2,644 lượt đã rút trước ngày 28 nằm ngoài quần thể này theo đề bài, nên không tính vào các tỷ lệ bên dưới.
- **Không hoàn thành** = `Fail` hoặc `Withdrawn`. Tỷ lệ 43.2%. `Pass` gộp cả `Distinction` (như `label3`).
- **Tuần 1–4** = `week` 1–4 trong `aq1_student_week.csv`.
- **Tách dữ liệu theo thời gian có sẵn trong file:** train = 2013B và 2013J (6,795), validation = 2014B (2,581), test = 2014J (3,644). Mô hình và ngưỡng được chọn trên validation; test chỉ dùng một lần.

## Câu 1: Tương tác 4 tuần đầu khác nhau thế nào giữa Pass / Fail / Withdrawn?

Cả ba nhóm khác nhau rõ, và thứ tự nhất quán: **Pass > Withdrawn > Fail** ở hầu hết chỉ số.

| Chỉ số (trung bình / trung vị) | Pass | Withdrawn | Fail |
|---|---|---|---|
| Lượt truy cập tuần 1 | 102.9 / 59 | 71.3 / 33 | 55.2 / 20 |
| Lượt truy cập tuần 4 | 92.7 / 43 | 58.7 / 21 | 44.4 / 10 |
| Số ngày hoạt động tuần 1 | 3.2 / 3 | 2.4 / 2 | 2.0 / 2 |
| Lượt truy cập 0–28 | 404.8 / 257 | 270.7 / 160.5 | 208.0 / 112 |
| Số ngày hoạt động 0–28 | 13.3 / 12 | 9.9 / 9 | 8.1 / 7 |
| Số ngày kể từ lần hoạt động cuối (tính đến ngày 28) | 2.9 / 1 | 6.2 / 3 | 7.3 / 4 |
| Đã nộp TMA1 trước ngày 28 | 97.3% | 76.4% | 74.9% |
| Không có hoạt động trên hệ thống học trực tuyến trong 0–28 | 0.9% | 7.4% | 9.1% |

Kiểm định Kruskal–Wallis cho cả 3 nhóm đều rất nhỏ (p < 1e-100). Cả ba cặp nhóm đều khác nhau có ý nghĩa sau hiệu chỉnh Holm (kiểm định trên 4 chỉ số: lượt truy cập và số ngày hoạt động, tuần 1 và 0–28). Điểm khác biệt rõ nhất là Pass so với Fail (AUC về số ngày hoạt động 0–28 = 0.70). Withdrawn nằm giữa Pass và Fail, và có nhiều lượt truy cập hơn Fail ở cả 4 tuần.

## Câu 2: Chỉ báo nào khác biệt có ý nghĩa giữa hoàn thành và không hoàn thành, và từ tuần nào?

Hầu hết chỉ báo được kiểm định đều có ý nghĩa sau hiệu chỉnh Holm (`q2_chi_bao_hoan_thanh_vs_khong.csv`). Không có ý nghĩa: `registration_lead_days` (p = 0.86).

Mạnh nhất (AUC = xác suất một sinh viên không hoàn thành có giá trị cao hơn; 0.5 là không khác biệt):

- Số ngày hoạt động 0–28: AUC 0.326 (tương đương khả năng phân tách 0.67).
- Lượt truy cập 0–28: AUC 0.346. Số tài nguyên đã mở 0–28: AUC 0.380.
- Đã nộp TMA1 trước ngày 28: 97.3% ở nhóm hoàn thành so với 75.5% ở nhóm không hoàn thành.
- Ngày kể từ lần hoạt động cuối: AUC 0.651 (không hoàn thành có khoảng cách lớn hơn).
- Không có hoạt động trên hệ thống học trực tuyến: 8.5% so với 0.9%.

Yếu hơn: số lần học lại trước đó (AUC 0.548) và số tín chỉ đăng ký (AUC 0.531).

**Thời điểm xuất hiện:** khác biệt có ý nghĩa **ngay từ tuần 1** (lượt truy cập AUC 0.370; số ngày hoạt động AUC 0.369) và tiếp tục đến tuần 4 (`q2_khac_biet_theo_tuan.csv`). Khoảng cách không tăng dần qua các tuần, nên tín hiệu sớm nhất đã có sẵn trong tuần đầu. Đây là tương quan trong dữ liệu quan sát, không phải nguyên nhân.

## Câu 3: Chỉ dùng dữ liệu ngày 0–28, có dự báo được không, và tốt đến mức nào? Có đạt ít nhất 70% recall không?

**Có dự báo được, ở mức trung bình.**

- **Mô hình chính:** hồi quy logistic trên 26 đặc trưng 0–28 (tuần 1–4, hoạt động, tài nguyên, TMA1 đến ngày 28, số lần học lại, số tín chỉ, thời điểm đăng ký…). Mô hình này thắng mô hình cây tăng cường về AUC trên validation (0.727 so với 0.724), nên dùng hồi quy logistic vì dễ giải thích.
- **Test (2014J):** AUC 0.716, PR-AUC 0.649. Baseline chỉ dùng `clicks_0_28`: AUC 0.652.

| Cách đặt ngưỡng | Recall (test) | Precision | Tỷ lệ bị cảnh báo | Đạt 70%? |
|---|---|---|---|---|
| Ngưỡng xác suất 0.392, chốt trên validation để recall ≥ 70% | 64.2% | 53.4% | 45.4% | **Không** |
| Cùng tỷ lệ cảnh báo 53.6% (chốt trên validation), áp lên test theo thứ hạng | 71.9% | 50.6% | 53.6% | **Có** |

**Trả lời trực tiếp:** với ngưỡng xác suất cố định, **mục tiêu 70% không đạt** (64.2%). Muốn đạt 70% trên test thì phải cảnh báo khoảng **54% sinh viên** (1,954 trên 3,644). Mức đạt này có precision 51%, tức khoảng một nửa số được cảnh báo không rơi vào nhóm không hoàn thành. Đây là đánh đổi lớn; nên xem đây là mốc vận hành, không phải kết quả tốt.

Nhạy cảm (không dùng để quyết định): thêm `tma1_score` làm giảm AUC test xuống 0.667. Lý do là điểm TMA1 không có ngày chấm trong dữ liệu, nên không chắc đã có sẵn đến ngày 28, nên không đưa vào mô hình chính.

## Câu 4: Ưu tiên ai với 200 suất mỗi module-kỳ, và danh sách trúng bao nhiêu?

**Quy tắc:** trong mỗi module-kỳ, xếp theo xác suất không hoàn thành do mô hình chính ước tính (từ cao xuống thấp), lấy 200 sinh viên đầu. Áp dụng lên tập test (2014J).

| Module-kỳ | Sinh viên | Không hoàn thành | Trong danh sách | Trúng (không hoàn thành trong danh sách) | Precision | Recall của module-kỳ |
|---|---|---|---|---|---|---|
| BBB-2014J | 1,786 | 635 | 200 | 149 | 74.5% | 23.5% |
| FFF-2014J | 1,858 | 741 | 200 | 173 | 86.5% | 23.3% |
| **Tổng** | 3,644 | 1,376 | 400 | **322** | **80.5%** | **23.4%** |

- Trần recall lý thuyết với 200 suất/module-kỳ là 29.1%. **Mục tiêu 70% không thể đạt dưới giới hạn nhân lực này.**
- Độ nhạy theo số suất (`q4_do_nhay_suc_chua.csv`): 100 suất/module-kỳ trúng 185 (recall 13.4%); 300 suất/module-kỳ trúng 437 (recall 31.8%).
- Tệp danh sách: `q4_danh_sach_uu_tien_200_moi_module_ky.csv` (400 dòng).

Không dùng `assumed_conversion_rate` 0.14 trong `aq4_decision_params.json`: nguồn ghi "A5 (P1), C05 (P3)" không có trong dữ liệu, nên không kiểm chứng được.

## Câu 5: Với mỗi sinh viên trong danh sách, đặc trưng nào đóng góp nhiều nhất? Diễn đạt cho cố vấn.

Đóng góp được tính bằng hồi quy logistic: hệ số × độ lệch chuẩn hóa so với trung bình. Với 400 sinh viên, đặc trưng đóng góp lớn nhất là **tổng lượt truy cập 28 ngày đầu** (là yếu tố hàng đầu của 268/400 sinh viên). Các yếu tố tiếp theo: nộp TMA1 đúng hạn/đã nộp, số ngày hoạt động trong tuần 2 và 4, số ngày hoạt động 0–28.

Mẫu diễn đạt đã được tạo cho từng sinh viên (`q5_giai_thich_cho_co_van.csv`, cột `giai_thich_cho_co_van`). Ví dụ, sinh viên 34756 (BBB 2013B):

> Sinh viên 34756 (BBB 2013B) được ưu tiên vì xác suất không hoàn thành ước tính khoảng 65%, các dấu hiệu chính là: tổng lượt truy cập 28 ngày đầu là 42 (thấp hơn mức trung vị 192.5 của cả nhóm); không nộp bài TMA1 đúng hạn; nộp bài TMA1 muộn 2 ngày so với hạn. Đây là tương quan trong dữ liệu, không phải nguyên nhân đã được chứng minh, nên cố vấn nên trao đổi sớm để hiểu hoàn cảnh cụ thể của sinh viên.

Lưu ý: đóng góp của các đặc trưng tương quan (tổng lượt truy cập và từng tuần) có thể bị chia nhỏ, nên xếp hạng giữa chúng chỉ mang tính tham khảo.

## Phương pháp (tóm tắt)

- Kiểm tra thời điểm có sẵn đặc trưng: mọi biến dùng đều có trước hoặc đúng ngày 28. Loại khỏi mô hình: `tma1_score` (không rõ ngày chấm), `final_result`/`label3`/`date_unregistration` (kết quả hoặc tương lai), thuộc tính nhân khẩu học và xã hội (giới tính, độ tuổi, khuyết tật, IMD, vùng, trình độ học vấn). Các thuộc tính này chỉ dùng để kiểm toán sai số theo nhóm (`q3_kiem_toan_theo_nhom_khong_dung_lam_bien.csv`).
- Kiểm toán theo nhóm (recall theo ngưỡng cố định): nữ 61%, nam 67%; khuyết tật 62%, không khuyết tật 65%; IMD 10–20% chỉ 58%, IMD không rõ 76%. Khoảng cách này cần theo dõi trước khi triển khai.
- Thiếu ngày nộp TMA1 khi sinh viên chưa nộp đến ngày 28 được điền 0; cờ `tma1_submitted_by_d28` cho biết trạng thái này.
- Kiểm định hai nhóm: Mann-Whitney và chi-square, hiệu chỉnh Holm.

## Hạn chế

- Dữ liệu quan sát: đây là tương quan, không phải nguyên nhân. Không thể kết luận can thiệp sẽ làm giảm việc không hoàn thành.
- Mô hình được huấn luyện trên các kỳ 2013 và kiểm tra trên 2014J. Tỷ lệ không hoàn thành khác nhau giữa các kỳ (test 37.8%, validation 46.5%), nên ngưỡng cố định không chuyển giao tốt. Xem lại ngưỡng trước khi dùng cho kỳ mới.
- Điểm TMA1 không có ngày chấm, nên không dùng trong mô hình chính.
- Chỉ có 4 tuần đầu trong bảng tuần; `clicks_0_28` nhiều hơn tổng 4 tuần tối đa 342 lượt (ngày 28 nằm ngoài các tuần 1–4). Phân tích tuần chỉ phản ánh phần tuần 1–4.
- Kỳ chỉ có hai module (BBB, FFF); không tổng quát hóa sang module khác.

## Tệp đầu ra

- `analysis.py`: toàn bộ phân tích (chạy lại được từ thư mục workspace).
- `q1_*.csv`, `q2_*.csv`, `q3_*.csv`, `q4_*.csv`, `q5_*.csv`: bảng kết quả.
- `bieu_do_1_tuong_tac_4_tuan.png`, `bieu_do_2_khac_biet_theo_tuan.png`, `bieu_do_3_roc_test.png`, `bieu_do_4_trung_danh_sach.png`.
- `tom_tat_ket_qua.json`, `log_chay.txt`: tóm tắt và nhật ký chạy.
