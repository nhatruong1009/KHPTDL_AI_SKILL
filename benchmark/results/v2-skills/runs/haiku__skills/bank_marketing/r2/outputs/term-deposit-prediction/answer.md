# Dự đoán khách hàng đăng ký tiền gửi trước khi gọi

## Trả lời ngắn gọn

- **Mô hình không tốt hơn baseline đơn giản một cách đo được.** Trên tập test được chia theo thời gian (6.179 khách, 38,5% đăng ký), mô hình được chọn (hồi quy logistic) đạt **ROC-AUC 0,577**, còn luật đơn giản "ưu tiên khách có kết quả chiến dịch trước" đạt **0,625**. Nhóm 20% khách xếp hạng đầu của mô hình có tỷ lệ đăng ký gấp **1,23 lần** mức nền, còn luật đơn giản gấp **1,77 lần**. Gradient boosting đạt AUC 0,496, tức là không có khả năng xếp hạng.
- **Con số AUC 0,80 có thể gây hiểu nhầm.** Nó xuất hiện khi chia ngẫu nhiên, nhưng cách chia đó không hợp lệ cho dự đoán tương lai (chi tiết ở phần "Độ nhạy"). Kết luận của tôi dựa trên chia theo thời gian.
- **Yếu tố quan trọng nhất theo mô hình** là `số người đang làm việc` (giảm AUC 0,083 khi xáo trộn), `đã từng được liên lạc`, `tháng liên lạc`, `kết quả chiến dịch trước`, `tỷ lệ việc làm`. Phần lớn là chỉ báo **giai đoạn** (chỉ số kinh tế và tháng gọi đánh dấu thời điểm chiến dịch), không phải nguyên nhân khách đăng ký. Lịch sử với chiến dịch trước (`kết quả chiến dịch trước`, `đã từng được liên lạc`) là tín hiệu nhất quán nhất qua các kiểm tra.

## Câu hỏi đã thu hẹp

Dữ liệu là chiến dịch lịch sử (5/2008 – 11/2010), không phải chiến dịch sắp tới. Tôi trả lời: *"Trước khi gọi, các đặc điểm đã biết của khách có dự đoán được ai đăng ký trong chiến dịch tương tự không, và mô hình có vượt luật đơn giản không?"*

## Dữ liệu và phương pháp

- **File chính:** `data/bank-additional/bank-additional-full.csv` (41.188 dòng, 21 cột). Đây là phiên bản có nhiều đặc trưng nhất (có 5 chỉ số kinh tế vĩ mô). Kiểm tra độ nhạy trên `data/bank-full.csv` (45.211 dòng, không có chỉ số vĩ mô).
- **Biến mục tiêu:** `y` = đăng ký tiền gửi (1 = có). Tỷ lệ nền 11,3%.
- **Kiểm tra rò rỉ (timing audit):**
  - Loại `duration` (thời lượng cuộc gọi, chỉ biết sau khi gọi). Chỉ dùng trong kiểm tra độ nhạy S1 để đối chiếu.
  - Loại `campaign` (số lần gọi tính cả cuộc hiện tại, chưa biết trước cuộc gọi). Kết quả S2 không đổi.
  - Loại `age` và `marital` khỏi mô hình (thông tin cá nhân nhạy cảm). Tuổi chỉ dùng để kiểm tra lỗi theo nhóm.
  - Giữ `month`, `day_of_week` vì lịch gọi có thể lên kế hoạch trước.
  - Giữ 5 chỉ số vĩ mô (tỷ lệ việc làm, CPI, niềm tin tiêu dùng, Euribor, số người có việc). Dữ liệu không có ngày công bố, nên đây là giả định.
- **Chia dữ liệu:** theo thời gian (dữ liệu được sắp theo ngày): train 70% (28.831), valid 15% (6.178), test 15% (6.179). Chọn mô hình trên valid, báo cáo test một lần.
- **Mô hình:** baseline ngẫu nhiên; baseline luật đơn giản (tỷ lệ đăng ký theo `kết quả chiến dịch trước`, học từ train); hồi quy logistic; gradient boosting (HistGradientBoosting).

## Kết quả chính (test theo thời gian, n = 6.179, tỷ lệ nền 38,5%)

| Mô hình | ROC-AUC | PR-AUC | Lift top 20% | Thu hồi top 20% |
|---|---|---|---|---|
| Ngẫu nhiên | 0,504 | – | 1,06 | – |
| **Luật đơn giản** (kết quả chiến dịch trước) | **0,625** | – | **1,77** | – |
| Hồi quy logistic (được chọn trên valid) | 0,577 | 0,447 | 1,23 | 24,7% |
| Gradient boosting | 0,496 | 0,389 | 0,96 | 19,2% |

Trên valid, hồi quy logistic đạt 0,660 so với 0,482 của luật đơn giản. Hai kết quả mâu thuẫn nhau, vì tỷ lệ nền valid (10,7%) khác nhiều so với test (38,5%). Đây là dấu hiệu rõ nhất rằng kết quả không ổn định theo thời gian.

## Độ nhạy và kiểm tra độ bền

| Kịch bản | Mô hình | AUC test | Ghi chú |
|---|---|---|---|
| Chính | Hồi quy logistic | 0,577 | luật đơn giản 0,625 |
| S1: thêm `duration` | Hồi quy logistic | 0,651 | rò rỉ, chỉ để đối chiếu |
| S2: thêm `campaign` | Hồi quy logistic | 0,577 | không đổi |
| S3: bỏ chỉ số vĩ mô | Hồi quy logistic / GB | 0,609 / 0,613 | luật đơn giản 0,625 |
| Bỏ vĩ mô và tháng | Hồi quy logistic / GB | 0,598 / 0,602 | luật đơn giản 0,625 |
| S4: `bank-full.csv`, bỏ tháng | Hồi quy logistic / GB | 0,659 / 0,602 | luật đơn giản 0,632 |
| Chia ngẫu nhiên phân tầng (đối chiếu, **không hợp lệ**) | Hồi quy logistic / GB | 0,804 / 0,813 | lift top 20% ≈ 3,3; luật đơn giản 0,627 |
| Trượt theo thời gian (train 60%, test 80–100%) | Hồi quy logistic | 0,475 | luật đơn giản 0,584 |
| Trượt theo thời gian (train 50%, test 70–85%) | Hồi quy logistic | 0,517 | luật đơn giản 0,496 |

**Tỷ lệ đăng ký nền thay đổi mạnh theo thời gian.** Theo khối 2.000 dòng liên tiếp, tỷ lệ tăng từ khoảng 2% (tháng 5/2008) lên khoảng 50% (cuối 2010). Các chỉ số kinh tế giảm trong cùng giai đoạn (`số người đang làm việc` từ 5.228 xuống 4.977). Mô hình học "giai đoạn" thay vì học hành vi khách, nên không tổng quát hóa được sang giai đoạn sau.

## Nhóm khách hàng

Tôi kiểm tra lỗi theo nhóm tuổi trên test (mô hình chọn xếp hạng top 20%):

| Nhóm tuổi | n | Tỷ lệ đăng ký | Tỷ lệ được gọi (top 20%) | AUC trong nhóm |
|---|---|---|---|---|
| <30 | 1.411 | 38,8% | 20,9% | 0,597 |
| 30–39 | 2.077 | 36,3% | 18,5% | 0,590 |
| 40–49 | 982 | 35,0% | 16,3% | 0,599 |
| 50–59 | 864 | 39,7% | 18,8% | 0,569 |
| 60+ | 845 | 45,9% | 27,8% | 0,467 |

Nhóm 60+ có tỷ lệ đăng ký cao nhất nhưng mô hình xếp hạng kém nhất trong nhóm này (AUC 0,467). Mô hình không dùng tuổi, nhưng vẫn gắn cờ 27,8% nhóm 60+ trong top 20%. Nguyên nhân cụ thể chưa được kiểm tra. Cần kiểm tra nếu triển khai.

## Yếu tố quan trọng nhất (hồi quy logistic, test)

Giảm ROC-AUC khi xáo trộn biến: `số người đang làm việc` 0,083; `đã từng được liên lạc` 0,051; `tháng liên lạc` 0,039; `kết quả chiến dịch trước` 0,030; `tỷ lệ việc làm` 0,028; `chỉ số giá tiêu dùng` 0,019. Các biến còn lại ≤ 0,007.

Cần đọc thận trọng:
- Năm biến đầu, trừ `kết quả chiến dịch trước` và `đã từng được liên lạc`, đều là chỉ báo giai đoạn. Chúng không có tác động nhân quả đã được chứng minh.
- Hệ số hồi quy (xem `logit_coefficients_top20.csv`): `kết quả chiến dịch trước = chưa từng liên lạc` có hệ số âm (−0,52), nghĩa là nhóm này có xu hướng đăng ký thấp hơn. Đây là liên hệ quan sát, không phải nguyên nhân.

## Hạn chế

1. **Không có dữ liệu chiến dịch hiện tại.** Mọi kết quả dựa trên 2008–2010. Điều kiện kinh tế và tỷ lệ đăng ký của chiến dịch sắp tới có thể khác rất nhiều.
2. **Không có ngày thực** trong file (chỉ có tháng và thứ). Thứ tự thời gian lấy từ thứ tự dòng.
3. **Có 12 dòng trùng hoàn toàn** trong `bank-additional-full.csv`. Giữ lại vì không có khóa khách để xác định là lỗi. Chưa kiểm tra xem loại bỏ chúng có đổi kết quả hay không.
4. **Giá trị "unknown"** trong `job`, `education`, `default`, `housing`, `loan` được coi là một danh mục riêng.
5. **Không có ràng buộc công suất** trong câu hỏi, nên báo cáo lift và thu hồi theo top 10/20/30%. Không có mục tiêu cứng nào được đặt ra.

## Khuyến nghị

- Với chiến dịch sắp tới, **dùng luật đơn giản** (ưu tiên khách đã có kết quả thành công ở chiến dịch trước) làm baseline. Mô hình hiện tại không đủ để thay thế.
- Trước khi triển khai, thu thập dữ liệu chiến dịch hiện tại và đánh giá lại trên đó. Theo dõi tỷ lệ đăng ký nền theo tháng.
- Nếu cần mô hình, ưu tiên các đặc trưng lịch sử khách (không dùng chỉ số vĩ mô hay tháng làm tín hiệu chính), và kiểm tra lỗi theo nhóm tuổi 60+.

## File kết quả

- `analysis.py`: mô hình chính, chia thời gian, độ nhạy, biểu đồ.
- `diagnostics.py`, `robustness.py`: kiểm tra độ lệch thời gian và độ bền.
- `metrics_test.csv`, `metrics_valid.csv`, `sensitivity.csv`, `split_info.csv`, `permutation_importance.csv`, `logit_coefficients_top20.csv`, `age_group_audit.csv`, `diagnostic_*.csv`, `robustness_time_split.csv`, `results.json`.
- Biểu đồ: `model_comparison.png`, `gains_curve.png`, `feature_importance.png`.

*Dữ liệu quan sát: các kết quả là liên hệ, không phải nhân quả.*
