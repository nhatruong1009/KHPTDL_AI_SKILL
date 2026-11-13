# Dự đoán khách hàng đăng ký tiền gửi có kỳ hạn trước khi gọi

## Trả lời ngắn

- **Mô hình tốt hơn baseline đáng kể.** Gradient boosting đạt AUC 0,80 (CV 5 fold), so với 0,50 của chọn ngẫu nhiên và 0,61 của quy tắc đơn giản theo `poutcome`. Khi gọi 20% khách hàng xếp hạng cao nhất, mô hình bắt được 62% số người đăng ký, tức lift 3,1x so với 1,0x của ngẫu nhiên và 1,8x của quy tắc poutcome.
- **Khi kiểm tra theo thời gian, lợi thế thu hẹp.** Trên 20% dữ liệu cuối (train trên 80% đầu), AUC của GBM là 0,687, chỉ cao hơn quy tắc poutcome (0,644) khoảng 0,04. Precision top 20% của GBM (52,5%) thậm chí thấp hơn quy tắc poutcome (55,8%) và hồi quy logistic (57,3%). Vì vậy hồi quy logistic là lựa chọn thực tế gần như ngang bằng và dễ giải thích hơn.
- **Yếu tố quan trọng nhất:** kết quả chiến dịch trước (`poutcome`), tháng liên hệ (`month`), tuổi (`age`), số dư bình quân (`balance`). Biến `duration` có AUC 0,94 nhưng không dùng được vì chỉ biết sau khi gọi.

## Dữ liệu và cách làm

- **Bộ dữ liệu:** `data/bank-full.csv`, 45.211 khách hàng, tỷ lệ đăng ký nền 11,7%. Đây là bộ đầy đủ nhất theo tài liệu UCI. Bộ `bank-additional-full.csv` (41.188 dòng) có thêm 5 chỉ số kinh tế vĩ mô nhưng không có `balance` và `day`. Kết quả trên bộ này được báo cáo ở phần kiểm tra độ nhạy.
- **Biến loại bỏ:**
  - `duration`: thời lượng cuộc gọi chỉ biết sau khi gọi, nên rò rỉ kết quả.
  - `campaign`: đếm số lần liên hệ trong chiến dịch, bao gồm cuộc gọi quyết định kết quả. Thêm biến này vào chỉ làm AUC tăng 0,002 (0,802), nên loại bỏ không ảnh hưởng nhiều.
- **Biến dùng:** 9 biến phân loại (job, marital, education, default, housing, loan, contact, month, poutcome) và 5 biến số (age, balance, day, pdays, previous).
- **Mô hình:** hồi quy logistic (one-hot + chuẩn hóa) và HistGradientBoosting (300 vòng, learning rate 0,05).
- **Đánh giá:** stratified 5-fold CV; holdout theo thời gian (80% đầu để train, 20% cuối để test) vì dữ liệu được sắp xếp theo ngày từ 2008 đến 2010.

## Kết quả so sánh (CV 5 fold, trung bình ± độ lệch chuẩn)

| Mô hình | AUC | PR-AUC | Precision top 10% | Precision top 20% | Recall top 20% | Lift top 20% |
|---|---|---|---|---|---|---|
| Ngẫu nhiên (baseline 1) | 0,504 ± 0,012 | 0,118 | 11,3% | 11,5% | 19,7% | 0,98 |
| Quy tắc poutcome (baseline 2) | 0,614 ± 0,013 | 0,244 | 30,7% | 21,5% | 36,8% | 1,84 |
| Hồi quy logistic | 0,762 ± 0,009 | 0,401 | 47,5% | 32,4% | 55,4% | 2,77 |
| **Gradient boosting** | **0,800 ± 0,008** | **0,452** | **50,7%** | **36,3%** | **62,0%** | **3,10** |

Holdout theo thời gian (train 80% đầu, test 20% cuối):

| Mô hình | AUC | PR-AUC | Precision top 20% | Lift top 20% |
|---|---|---|---|---|
| Ngẫu nhiên | 0,498 | 0,315 | 30,8% | 0,98 |
| Quy tắc poutcome | 0,644 | 0,458 | 55,8% | 1,77 |
| Hồi quy logistic | 0,681 | 0,487 | 57,3% | 1,82 |
| Gradient boosting | 0,687 | 0,487 | 52,5% | 1,66 |

**Lưu ý quan trọng:** tỷ lệ đăng ký ở 20% cuối là 31,6%, trong khi ở 80% đầu chỉ là 6,7%. Dữ liệu có sự trôi dạt lớn theo thời gian, nên xác suất mô hình dự đoán không nên dùng trực tiếp làm ngưỡng cho chiến dịch mới mà không hiệu chỉnh lại.

## Yếu tố quan trọng nhất

Permutation importance trên holdout theo thời gian (mức giảm AUC khi xáo trộn biến):

| Biến | Mức giảm AUC | Ghi chú |
|---|---|---|
| poutcome | 0,081 | Đăng ký 64,7% khi kết quả trước là `success`, 12,6% khi `failure`, 9,2% khi `unknown` (82% dữ liệu) |
| month | 0,055 | Tỷ lệ thay đổi mạnh theo tháng, nhưng cũng bị lẫn với giai đoạn chiến dịch |
| age | 0,019 | Khách trên 60 tuổi đăng ký 42,3%, dưới 30 tuổi 16,3%, 41–50 tuổi 9,1% |
| balance | 0,012 | |
| day | 0,008 | |
| contact | 0,006 | `unknown` chỉ đăng ký 4,1%, `cellular` 14,9% |
| marital | 0,006 | |
| housing, pdays, education, job | < 0,004 | Ảnh hưởng nhỏ |
| loan, default, previous | ≈ 0 hoặc âm | Không có giá trị dự đoán thêm |

Biểu đồ: `bieu_do_so_sanh_mo_hinh.png` và `bieu_do_do_quan_trong.png`.

## Khuyến nghị

1. Dùng hồi quy logistic làm mô hình chính cho danh sách gọi: hiệu năng gần với GBM, ổn định hơn trên holdout theo thời gian và dễ giải thích.
2. Nếu muốn GBM, tái huấn luyện định kỳ và kiểm tra lại trên dữ liệu gần nhất trước khi dùng.
3. Đừng dùng xác suất thô làm ngưỡng; xếp hạng theo điểm và gọi theo thứ tự ưu tiên.
4. Ưu tiên khách có `poutcome = success` và khách trên 60 tuổi; loại khách `contact = unknown` khỏi danh sách ưu tiên hoặc thu thập thêm thông tin liên hệ.

## Hạn chế

- Dữ liệu là chiến dịch của một ngân hàng Bồ Đào Nha từ 2008 đến 2010. Tỷ lệ đăng ký và hành vi khách hàng hiện nay có thể đã khác.
- `month` và `contact = unknown` có thể lẫn với giai đoạn chiến dịch và cách thu thập dữ liệu, nên không nên hiểu là nguyên nhân.
- Holdout theo thời gian có tỷ lệ nền khác hẳn train, nên các chỉ số lift và precision không so sánh trực tiếp với CV.
- Bộ `bank-additional-full` (có chỉ số vĩ mô, không có `balance`/`day`) cho kết quả tương đương: GBM AUC 0,802, hồi quy logistic 0,791, ngẫu nhiên 0,497 (CV 5 fold). Lift top 20% là 3,23 cho GBM và 3,13 cho logistic.
- Bước kiểm tra màu bằng `validate_palette.js` không chạy được vì lệnh bị từ chối quyền thực thi. Bốn màu dùng trong biểu đồ lấy từ slot 1–4 của bảng màu tham chiếu, đã được tài liệu ghi nhận là đạt kiểm tra cho các cặp liền kề, nhưng chưa được xác minh lại trong phiên này.

## Tệp đầu ra

- `ket_qua_cv5.csv`, `ket_qua_holdout_thoi_gian.csv`, `ket_qua.json`: số liệu đánh giá.
- `do_quan_trong_bien.csv`, `he_so_logistic.csv`: độ quan trọng và hệ số.
- `ty_le_theo_*.csv`: tỷ lệ đăng ký theo nhóm.
- `code/analysis.py`, `code/charts.py`: mã nguồn.
