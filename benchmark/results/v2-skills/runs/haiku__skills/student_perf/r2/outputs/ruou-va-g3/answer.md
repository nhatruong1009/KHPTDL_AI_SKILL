# Uống rượu có liên quan đến điểm cuối kỳ G3 thấp hơn không?

## Trả lời ngắn gọn

**Có, nhưng phần lớn là do điểm các kỳ trước.**

- **Chưa điều chỉnh:** học sinh uống nhiều có G3 thấp hơn rõ rệt. Nhóm uống nhiều (mức 4–5) thấp hơn nhóm uống ít (mức 1–2) khoảng **1,4 điểm** với cuối tuần (Walc) và **1,7 điểm** với ngày thường (Dalc), tương ứng cỡ hiệu ứng Cohen d ≈ **−0,50** và **−0,57** (trung bình). Mỗi bậc uống tăng thêm tương ứng với G3 thấp hơn **0,42 điểm** (Walc) và **0,57 điểm** (Dalc). Cả hai đều có p < 0,001 (kiểm định cụm theo học sinh).
- **Khi điều chỉnh điểm G1 và G2 (kỳ 1 và kỳ 2):** hiệu ứng gần như biến mất. Mỗi bậc uống chỉ tương ứng **−0,05 điểm** (Walc, 95% CI −0,10 đến +0,003, p = 0,06) và **−0,08 điểm** (Dalc, 95% CI −0,19 đến +0,03, p = 0,13). Hệ số chuẩn hóa β ≈ −0,02. Khi đưa cả hai biến rượu vào cùng mô hình, cả hai đều không có ý nghĩa thống kê.

Diễn giải: học sinh uống nhiều thường đã có điểm thấp hơn ngay từ kỳ 1 và kỳ 2. Dữ liệu cho thấy sự khác biệt ở G3 chủ yếu phản ánh khác biệt về học lực có sẵn, không phải tác động riêng của rượu. Đây là dữ liệu quan sát, nên không thể kết luận nhân quả.

## Dữ liệu và xử lý

| Mục | Kết quả |
|---|---|
| Bản ghi | Toán 395, Bồ Đào Nha 649 |
| Khớp học sinh ở cả hai file | 13 khóa định danh (theo `student-merge.R`) cho **382 cặp**. Vì có khóa trùng trong cùng một file (4 ở Toán, 12 ở Bồ Đào Nha), số học sinh duy nhất là **366 người có mặt ở cả hai môn**, tổng **662 học sinh**. |
| Cách gộp | Gộp hai file thành một bảng bản ghi môn học, có biến môn (`is_por`). Các bản ghi cùng khóa định danh dùng chung một mã học sinh để tính sai số chuẩn cụm. Không nhân đôi bản ghi. |
| G3 = 0 | **53 bản ghi**, tất cả đều có vắng mặt = 0. 33 bản ghi có G2 > 0. Đây có khả năng là học sinh bỏ học hoặc không thi, không phải điểm thật. **Mẫu chính loại bỏ 53 bản ghi này** (còn 991). Kết quả khi giữ lại vẫn tương tự (xem bên dưới). |
| G2 = 0 / G1 = 0 | 20 và 1 bản ghi. Được loại khỏi mô hình có điều chỉnh (còn 990). |

## Phương pháp

1. **Mô tả:** G3 trung bình theo từng mức Walc và Dalc, kèm 95% CI.
2. **Kiểm định và cỡ hiệu ứng:** so sánh nhóm cao (4–5) với nhóm thấp (1–2) bằng Mann-Whitney U (kèm rank-biserial) và Cohen d. Tương quan Spearman.
3. **Hồi quy OLS** G3 ~ rượu + biến môn, với sai số chuẩn cụm theo học sinh (647 cụm). Chạy hai phiên bản: không điều chỉnh, và điều chỉnh G1 + G2.

G1 và G2 là điểm các kỳ trước, nên được biết trước G3. Đưa chúng vào mô hình là hợp lý khi hỏi "rượu có liên quan đến G3 sau khi đã tính đến học lực trước đó không?".

## Độ nhạy

| Kiểm tra | Walc (điểm/bậc) | Dalc (điểm/bậc) |
|---|---|---|
| Chính, chưa điều chỉnh | −0,42 (p < 0,001) | −0,57 (p < 0,001) |
| Chính, điều chỉnh G1 + G2 | −0,05 (p = 0,06) | −0,08 (p = 0,13) |
| Giữ cả G3 = 0, chưa điều chỉnh | −0,35 (p = 0,001) | −0,56 (p < 0,001) |
| Giữ cả G3 = 0, điều chỉnh G1 + G2 | +0,02 (p = 0,72) | — |
| Mỗi học sinh một bản ghi, chưa điều chỉnh | −0,40 (p < 0,001) | −0,63 (p < 0,001) |
| Chỉ Toán, chưa điều chỉnh | −0,47 (p < 0,001) | −0,49 (p = 0,003) |
| Chỉ Bồ Đào Nha, chưa điều chỉnh | −0,39 (p < 0,001) | −0,62 (p < 0,001) |

Kết luận không đổi ở mọi kiểm tra: **hiệu ứng thô luôn âm và có ý nghĩa; sau khi điều chỉnh G1 + G2 thì không có bằng chứng về hiệu ứng riêng.** Khi giữ lại các bản ghi G3 = 0, hiệu ứng thô vẫn còn (xem thêm mục giới hạn).

## Giới hạn

- **Dữ liệu quan sát:** chỉ thể hiện mối liên quan, không phải nhân quả. Rượu và học lực có thể cùng bị ảnh hưởng bởi yếu tố khác (động lực, gia đình, thời gian).
- **Dalc và Walc là tự khai báo** theo thang 1–5, được coi là tuyến tính theo bậc.
- **G3 = 0** được coi là không hoàn thành. Nếu thực tế là điểm 0 thật, mẫu chính sẽ bỏ sót những học sinh có thể uống nhiều và điểm thấp nhất, và hiệu ứng thô có thể bị đánh giá thấp. Kết quả khi giữ lại các bản ghi này cho thấy hiệu ứng thô vẫn có, nhưng hiệu ứng điều chỉnh vẫn bằng 0.
- **Nhận dạng học sinh** bằng 13 khóa nhân khẩu học, như cách trong codebook. Có thể có vài trường hợp hai học sinh khác nhau cùng khóa, nên số 366 và 662 là ước tính.
- **Kiểm định Spearman và Mann-Whitney** không tính đến việc các bản ghi cùng học sinh phụ thuộc nhau. Kết luận chính dựa trên OLS cụm.
- **Mức Walc = 5** chỉ có 69 bản ghi (Dalc = 4–5 có 49 bản ghi), nên khoảng tin cậy ở các mức cao rộng.

## File đầu ra

- `analysis.py`: mã chạy toàn bộ phân tích.
- `data_quality.csv`, `descriptives.csv`, `tests_effect_sizes.csv`, `models_ols_cluster.csv`: số liệu.
- `chart_g3_theo_muc_ruou.png`: G3 trung bình theo mức uống rượu.
- `chart_forest_ols.png`: các hệ số ước lượng ở mọi mô hình.
- `run_log.txt`: đầu ra khi chạy.
