# Dự đoán khách hàng đăng ký tiền gửi trước khi gọi

## Trả lời ngắn

- **Mô hình tốt hơn baseline đơn giản rất nhiều.** Gradient boosting đạt ROC AUC **0,814** trên tập kiểm tra (CV 5 fold: 0,804 ± 0,016). Baseline "chọn ngẫu nhiên / tỷ lệ chung" có AUC 0,50. Baseline luật đơn giản "ưu tiên khách có kết quả chiến dịch trước là success" có AUC 0,621.
- **Với ngân sách gọi cố định, lợi ích rõ rệt.** Nếu chỉ gọi **10%** khách có điểm cao nhất, tổng đài tiếp cận **46,5%** tổng số khách sẽ đăng ký (tỷ lệ đăng ký trong nhóm này là 52,3%, gấp 4,6 lần tỷ lệ chung 11,3%). Gọi **20%** khách đầu tiên thu được **66,5%** tổng số khách đăng ký. Luật đơn giản chỉ thu được 37,7% với 20% đầu tiên.
- **Yếu tố quan trọng nhất là bối cảnh kinh tế vĩ mô tại thời điểm gọi** (số lao động có việc, tỷ lệ biến động việc làm, chỉ số giá, lãi suất euribor), kế đến là **loại liên lạc (di động hay cố định)**, **tháng liên lạc**, và **số lần đã gọi trong chiến dịch**. Kết quả chiến dịch trước (`poutcome`) mạnh khi xét riêng, nhưng hầu như trùng thông tin với các yếu tố trên nên mức đóng góp độc lập thấp.
- **Khuyến nghị triển khai:** dùng phiên bản **không có chỉ số vĩ mô** nếu không thể dự báo chúng cho chiến dịch sắp tới. AUC khi đó là 0,781 và gọi 20% đầu tiên thu được 59,4% số khách đăng ký. Mô hình có chỉ số vĩ mô chỉ nên dùng khi đã có dự báo đáng tin cậy cho các chỉ số này.

## Dữ liệu và phương pháp

- **Nguồn:** `data/bank-additional/bank-additional-full.csv`. Đây là phiên bản đầy đủ nhất về số đặc trưng (20 biến đầu vào, 41.188 dòng). Sau khi bỏ 12 dòng trùng lặp hoàn toàn còn 41.176 dòng. Tỷ lệ đăng ký là 11,3%.
- **Chưa dùng `duration`** (thời lượng cuộc gọi). Biến này chỉ biết sau khi gọi xong nên sẽ làm rò rỉ kết quả, không phù hợp để quyết định trước khi gọi.
- **Đặc trưng:** `pdays` = 999 (chưa từng được liên lạc) được mã hóa thành cờ `pdays_contacted` và giá trị `pdays_num`. Các mức "unknown" được giữ như một nhóm riêng.
- **Đánh giá:** tách 25% holdout phân tầng theo nhãn (seed 42), kèm 5-fold CV phân tầng trên toàn bộ dữ liệu.
- **Các mô hình so sánh:**
  - Baseline 1: tỷ lệ chung (AUC = 0,5 theo định nghĩa, không có thông tin để xếp hạng).
  - Baseline 2: luật đơn giản theo `poutcome` (success > failure > khác).
  - Hồi quy logistic (one-hot cho biến phân loại, chuẩn hóa biến số).
  - Gradient boosting (HistGradientBoosting, có early stopping).
- **Quan trọng đặc trưng:** permutation importance trên holdout, đo mức giảm ROC AUC khi xáo trộn từng biến (10 lần lặp).

## Kết quả chi tiết (holdout 25%)

| Mô hình | ROC AUC | PR AUC | Lift top 10% | Thu hồi top 10% | Lift top 20% | Thu hồi top 20% |
|---|---|---|---|---|---|---|
| Baseline: tỷ lệ chung | 0,500 | 0,113 | 1,07 | 10,7% | 0,99 | 19,7% |
| Baseline: luật poutcome | 0,621 | 0,275 | 2,76 | 27,6% | 1,88 | 37,7% |
| Hồi quy logistic | 0,802 | 0,452 | 4,42 | 44,2% | 3,20 | 64,1% |
| **Gradient boosting** | **0,814** | **0,491** | **4,65** | **46,5%** | **3,32** | **66,5%** |
| GB, không chỉ số vĩ mô | 0,781 | 0,434 | 4,30 | 43,0% | 2,97 | 59,4% |

"Thu hồi top k%" là tỷ lệ tổng số khách đăng ký nằm trong k% khách được xếp hạng cao nhất. Lift là tỷ lệ đăng ký trong nhóm đó chia cho tỷ lệ chung.

Gradient boosting tốt hơn hồi quy logistic khoảng 0,01 AUC (cả trên holdout lẫn CV). Đây là chênh lệch nhỏ nhưng nhất quán. Mô hình có thể dùng ngay với logistic nếu cần đơn giản và dễ giải thích.

**Lift theo decile (gradient boosting):** nhóm 1 có tỷ lệ đăng ký 52,3% (lift 4,6), nhóm 2 là 22,5% (lift 2,0), nhóm 3 là 8,3% (lift 0,73, đã dưới mức trung bình). Từ nhóm 3 trở đi, tỷ lệ luôn dưới mức trung bình (xem `lift_theo_decile_chinh.csv`).

## Yếu tố quan trọng nhất

Permutation importance (gradient boosting, giảm ROC AUC khi xáo trộn biến):

| Thứ hạng | Yếu tố | Giảm AUC | Ghi chú |
|---|---|---|---|
| 1 | Số lao động có việc (`nr.employed`) | 0,050 | Chỉ số vĩ mô theo quý |
| 2 | Tỷ lệ biến động việc làm (`emp.var.rate`) | 0,020 | Chỉ số vĩ mô theo quý |
| 3 | Loại liên lạc (`contact`) | 0,016 | Di động: 14,7% đăng ký; cố định: 5,2% |
| 4 | Tháng liên lạc (`month`) | 0,015 | Mar 50,5%, Sep 44,9%, Oct 43,9%, Dec 48,9%; May 6,4% |
| 5 | Chỉ số giá tiêu dùng (`cons.price.idx`) | 0,015 | Chỉ số vĩ mô theo tháng |
| 6 | Chỉ số niềm tin tiêu dùng (`cons.conf.idx`) | 0,014 | Chỉ số vĩ mô theo tháng |
| 7 | Lãi suất euribor 3 tháng (`euribor3m`) | 0,010 | Chỉ số vĩ mô theo ngày |
| 8 | Số lần gọi trong chiến dịch (`campaign`) | 0,005 | Gọi càng nhiều, tỷ lệ càng thấp: 13% (1 lần) → 3,1% (trên 10 lần) |
| 9 | Số ngày từ lần liên lạc trước (`pdays_num`) | 0,003 | |
| 10 | Tuổi (`age`) | 0,002 | |
| 11 | Kết quả chiến dịch trước (`poutcome`) | 0,002 | Success: 65,1% đăng ký; nonexistent: 8,8% |

Ghi chú về cách đọc:

- **Các chỉ số vĩ mô tương quan mạnh với nhau** nên permutation importance chia phần đóng góp giữa chúng và đánh giá thấp từng biến riêng lẻ. Phép đo trực tiếp hơn là bỏ cả nhóm: AUC giảm từ 0,814 xuống 0,781. Các chỉ số này phần lớn đang mã hóa **thời kỳ** chiến dịch (ví dụ giai đoạn kinh tế khó khăn có tỷ lệ đăng ký cao hơn). Theo biến `emp.var.rate`, nhóm có chỉ số thấp nhất đạt 21,5% đăng ký, nhóm cao nhất đạt 5,3%.
- **Hệ số hồi quy logistic** (xem `he_so_logistic_chinh.csv`) cùng chiều với các phát hiện trên. Tuy nhiên, với one-hot và regularization L2, độ lớn từng hệ số chỉ mang tính tương đối nên không nên diễn giải tuyệt đối.
- **Biến `contact`, `month` và `poutcome`** được kiểm tra thêm bằng tỷ lệ thô, khớp với hướng tác động của mô hình.

## Độ nhạy: bank-full.csv

Chạy lại cùng quy trình trên `data/bank-full.csv` (45.211 dòng, có `balance`, không có chỉ số vĩ mô, `poutcome` có nhiều giá trị "unknown"):

| Mô hình | ROC AUC holdout |
|---|---|
| Baseline luật poutcome | 0,606 |
| Hồi quy logistic | 0,773 |
| Gradient boosting | 0,803 |

Kết luận không đổi: gradient boosting tốt hơn logistic và baseline rất nhiều. Yếu tố hàng đầu cũng là loại liên lạc và tháng liên lạc, tiếp theo là ngày trong tháng và `poutcome`. Trên bank-full, khoảng cách giữa gradient boosting và logistic lớn hơn (0,03 AUC so với 0,01 trên bộ chính), nên lợi thế của mô hình phi tuyến phụ thuộc vào bộ dữ liệu.

## Hạn chế

- **Không kiểm định theo thời gian.** Dữ liệu được sắp theo ngày nhưng không có cột ngày đầy đủ, nên việc chia là ngẫu nhiên (phân tầng theo nhãn). Nếu chia theo thời gian (train trên giai đoạn cũ, test trên giai đoạn mới), hiệu năng thực tế có thể thấp hơn. Đây là ước lượng có thể lạc quan.
- **Chỉ số vĩ mô là đặc trưng theo thời kỳ.** Dữ liệu thuộc giai đoạn 2008–2010 của một ngân hàng Bồ Đào Nha. Để dùng cho chiến dịch sắp tới, cần dự báo các chỉ số này hoặc dùng phiên bản không có chúng. Mô hình cũng cần được theo dõi lại khi điều kiện kinh tế thay đổi.
- **Quan hệ là tương quan, không phải nhân quả.** Ví dụ, gọi di động đi cùng tỷ lệ đăng ký cao hơn, nhưng điều này có thể phản ánh cách chọn khách, không phải hiệu quả của kênh.
- **Không có kiểm định độ hiệu chỉnh xác suất chi tiết** (calibration curve). Tuy vậy, Brier score (0,075) và log loss (0,265) của gradient boosting đều tốt hơn logistic (0,078 và 0,274), nên xác suất đầu ra đủ tin cậy để xếp hạng.
- **12 dòng trùng lặp** đã được bỏ. Đây có thể là các khách hàng khác nhau có đặc điểm giống hệt nhau. Việc bỏ hay giữ không làm thay đổi kết luận.
- **Thiếu dữ liệu:** một số biến phân loại có mức "unknown" (nghề nghiệp, học vấn, nợ xấu, vay nhà, vay tiêu dùng). Các mức này được giữ như một nhóm riêng và không được gán giá trị.

## File đầu ra

Tất cả nằm trong `outputs/du-doan-dang-ky-tien-gui/`:

- `analysis.py`: toàn bộ mã phân tích, chạy được từ bất kỳ thư mục nào (đường dẫn tương đối theo vị trí script).
- `ket_qua_mo_hinh_chinh.csv`, `ket_qua_mo_hinh_bank-full.csv`: bảng so sánh mô hình.
- `lift_theo_decile_*.csv`: lift theo decile.
- `quan_trong_dac_trung_*.csv`: permutation importance.
- `he_so_logistic_*.csv`: hệ số hồi quy logistic và odds ratio.
- `duong_loi_ich_chinh.png`, `quan_trong_dac_trung_chinh.png`, `ty_le_theo_decile_chinh.png`: biểu đồ.
