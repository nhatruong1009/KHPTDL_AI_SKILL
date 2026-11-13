# Ưu tiên khách hàng gọi trong chiến dịch tiền gửi có kỳ hạn

## Trả lời ngắn
- **Dữ liệu dùng:** `bank-additional/bank-additional-full.csv` (41.188 khách, 20 biến + `y`, sắp theo thời gian 05/2008–11/2010). Đây là bản đầy đủ nhất. `bank-full.csv` có 45.211 dòng nhưng thiếu các chỉ số vĩ mô và không phải bản mới nhất theo tài liệu. Mình chọn bản additional vì có ngày/thứ tự thời gian và biến bối cảnh.
- **Mô hình tốt hơn baseline không nhiều, và rất kém ổn định theo thời gian.** Chia theo thời gian (train 60% đầu, validation 20%, test 20% cuối), mô hình chọn trên validation là Logistic Regression chỉ với thông tin biết trước cuộc gọi (bỏ chỉ số vĩ mô). Kết quả trên test, đọc một lần:

| Mô hình (test) | ROC-AUC | PR-AUC | Tỉ lệ đăng ký trong 20% khách xếp đầu | Lift@20% |
|---|---|---|---|---|
| Baseline gọi ngẫu nhiên | 0,49 | 0,30 | 29,8% | 0,97 |
| Baseline luật đơn giản "từng thành công ở chiến dịch trước" | 0,63 | 0,48 | **56,6%** | **1,84** |
| **Logistic (bỏ vĩ mô) – mô hình chọn** | **0,68** | 0,48 | 53,4% | 1,73 |
| HistGradientBoosting (cùng biến) | 0,68 | 0,43 | 45,2% | 1,47 |

  - So với gọi ngẫu nhiên: mô hình đưa tỉ lệ đăng ký trong nhóm được gọi trước từ 29,8% lên 53,4% (gấp 1,7–1,8 lần), thu được 34,6% tổng số người đăng ký chỉ bằng 20% số cuộc gọi.
  - So với luật đơn giản: **mô hình không thắng ở top 20%** (53,4% so với 56,6%). Chỉ hơn ở khả năng xếp hạng toàn bộ (AUC 0,68 so với 0,63). Với mục tiêu chọn danh sách gọi, luật "ưu tiên khách từng đăng ký ở chiến dịch trước" gần như đủ tốt.
- **Yếu tố quan trọng nhất: lịch sử chiến dịch trước** (`poutcome`, `pdays`, `previous`). Xáo trộn nhóm này làm AUC test giảm 0,060, trong khi mọi nhóm khác giảm dưới 0,004. Trên toàn dữ liệu, khách có `poutcome=success` đăng ký 65,1% (n=1.373), khách `nonexistent` 8,8% (n=35.563). Khách từng được liên hệ (`pdays`≠999) đăng ký 63,8% so với 9,3% nếu chưa. Yếu tố phụ yếu hơn nhiều: kênh liên lạc (di động 14,7% so với điện thoại bàn 5,2%), thứ trong tuần, nghề nghiệp, tình trạng tín dụng.

## Vì sao kết quả bị hạn chế (quan trọng)
1. **Trôi dữ liệu rất mạnh theo thời gian.** Tỉ lệ đăng ký: train 4,8% → validation 11,1% → test 30,8% (`split_base_rate.csv`). Giai đoạn test (2010) có euribor3m 0,63–1,30, hoàn toàn nằm ngoài khoảng của train (4,19–5,05). Vì vậy các mô hình dùng chỉ số vĩ mô và `month` sụp đổ khi dự báo tương lai (AUC test 0,50 và 0,42), không phải vì chúng vô ích mà vì chúng không ngoại suy được.
2. **Con số "đẹp" 0,79 AUC chỉ có khi chia ngẫu nhiên** (CV 5-fold, `metrics_random_cv_reference.csv`; lift@20% = 3,1). Con số này trộn lẫn các giai đoạn nên không phản ánh việc dự báo chiến dịch sắp tới; mình **không** dùng làm kết quả chính. Nó chỉ cho thấy chỉ số vĩ mô giải thích rất nhiều khác biệt *giữa các giai đoạn*.
3. Chọn mô hình dựa trên validation (AUC 0,63; bản đầy đủ chỉ 0,48), không dựa trên test. Cả validation và test đều có phân phối khác train, nên các con số có độ bất định lớn. Mình không có khoảng tin cậy cho chênh lệch giữa Logistic và luật đơn giản; coi hai cách là ngang nhau về mặt thực dụng.

## Kiểm toán thời điểm biết của biến (`feature_audit.csv`)
- **Loại:** `duration` (chỉ biết sau cuộc gọi; tài liệu cảnh báo rõ) và `campaign` (đếm cả cuộc gọi cuối, không kiểm chứng được trước gọi). Chạy riêng dạng sensitivity: thêm `campaign` gần như không đổi (AUC 0,60); thêm cả `duration` nâng AUC lên 0,80 – đó là **rò rỉ**, không dùng được khi lập danh sách gọi.
- **Không dùng làm biến dự đoán:** `age`, `marital` (thuộc tính nhạy cảm) – chỉ dùng kiểm tra công bằng. Trên test, tỉ lệ đăng ký trong nhóm top 20% khá đều giữa các nhóm tuổi (49,5–55,9%, riêng 60+ là 52,0%, nhưng 41,8% khách 60+ lọt vào nhóm được gọi do tỉ lệ nền cao 45,9%) và tình trạng hôn nhân (51,8–53,7%), AUC theo nhóm thấp nhất ở 60+ (0,56). Xem `audit_by_group.csv`.
- **Giữ:** hồ sơ khách (`job`, `education`, `default`, `housing`, `loan`), `contact`, `day_of_week`, lịch sử chiến dịch trước.

## Phương pháp
Chia theo thứ tự thời gian của file (đã sắp theo ngày) 60/20/20; mã hóa one-hot + chuẩn hóa trong Pipeline fit trên train; so sánh Dummy ngẫu nhiên, luật đơn giản, Logistic, HistGradientBoosting; chọn trên validation; test dùng một lần. Độ quan trọng = permutation importance theo nhóm biến trên test (20 lần). Mã: `analysis.py`.

## Hạn chế
- Quan hệ là tương quan, không phải nhân quả. Khách "đã đăng ký trước đây" có thể chính là nhóm bản thân vốn quan tâm.
- 12 dòng trùng hoàn toàn được giữ nguyên (có thể là khách khác nhau có thông tin giống nhau).
- Không có ngày chính xác nên tên giai đoạn dựa trên thứ tự dòng theo tài liệu.
- Chiến dịch sắp tới chỉ nên dùng mô hình này nếu tình hình lãi suất gần với dữ liệu huấn luyện; nên huấn luyện lại bằng dữ liệu mới nhất và theo dõi tỉ lệ đăng ký thực tế.

## Khuyến nghị
Bắt đầu bằng luật đơn giản (khách từng đăng ký/được liên hệ ở chiến dịch trước, gọi qua di động), dùng điểm Logistic để xếp thứ tự phần còn lại, và đánh giá lại sau vài tuần đầu của chiến dịch.

Tệp: `metrics.csv`, `feature_group_importance.csv`, `audit_by_group.csv`, `precision_top20.png`, `feature_importance.png`.
