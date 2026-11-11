# Dự đoán khách hàng đăng ký tiền gửi có kỳ hạn (trước khi gọi)

## Trả lời ngắn
- **Mô hình tốt hơn baseline rõ rệt khi kiểm tra ngẫu nhiên cùng giai đoạn**: Gradient Boosting đạt **AUC 0,81** (KTC 95% 0,80–0,83), so với 0,50 nếu gọi ngẫu nhiên và **0,59** nếu chỉ dùng quy tắc đơn giản "lần chiến dịch trước thành công thì gọi trước". Gọi **20% khách hàng điểm cao nhất** bắt được **66% người đăng ký** (gọi ngẫu nhiên: 20%; quy tắc đơn giản: 34%) – tức gấp 3,3 lần. Nhóm 10% đầu bảng có tỷ lệ đăng ký 53% so với 11,3% trung bình (gấp 4,7 lần).
- **Nhưng khi dự báo theo thời gian (train quá khứ, test giai đoạn sau) lợi thế co lại mạnh**: AUC chỉ khoảng **0,60–0,62**, gần mức quy tắc đơn giản (trung bình 0,56; từng khối 0,48–0,63). Chưa có bằng chứng chắc chắn là mô hình vượt baseline khi áp dụng cho chiến dịch tương lai; lý do chính là bối cảnh kinh tế và cách chọn khách hàng thay đổi mạnh theo thời gian (xem Lưu ý).
- **Yếu tố quan trọng nhất**: (1) thời điểm gọi và bối cảnh kinh tế vĩ mô (số lao động `nr.employed`, `emp.var.rate`, `euribor3m`, `month`); (2) kênh liên lạc (`contact`: di động đăng ký 14,7% so với điện thoại bàn 5,2%); (3) lịch sử liên lạc trước (`poutcome`, `pdays`: khách từng đăng ký ở chiến dịch trước đăng ký lại 65,1%, so với 8,8% nhóm chưa liên lạc). Các đặc điểm nhân khẩu học (nghề, hôn nhân, học vấn, khoản vay) đóng góp rất ít sau khi đã có các yếu tố trên.

## Dữ liệu và thiết lập
- **Phiên bản dùng**: `data/bank-additional/bank-additional-full.csv` – 41.188 dòng, 20 biến đầu vào (có thêm 5 chỉ số kinh tế vĩ mô), sắp theo thời gian từ 5/2008 đến 11/2010. Đây là bản đầy đủ nhất về cả số dòng lẫn biến trong họ dữ liệu này. (Giả định: không dùng `bank-full.csv` – bộ khác, 45.211 dòng, có `balance` nhưng không có chỉ số vĩ mô; không trộn hai bộ.)
- **Mục tiêu**: `y` = yes (11,27% đăng ký). 12 dòng trùng lặp được giữ nguyên (không đáng kể).
- **Chống rò rỉ**: loại `duration` (thời lượng cuộc gọi – chỉ biết sau khi gọi; thêm vào làm AUC tăng giả tạo lên 0,76 trong kiểm tra theo thời gian) và `campaign` (số lần liên lạc trong chiến dịch, không biết ở lần gọi đầu; thêm vào không cải thiện, AUC 0,62 so với 0,61). `pdays=999` được mã hóa thành "chưa từng liên lạc" + cờ riêng.
- **Baseline**: (1) gọi ngẫu nhiên (tỷ lệ chung); (2) quy tắc `poutcome = success` gọi trước.
- **Mô hình**: Logistic Regression và Gradient Boosting (HistGradientBoosting), 3 bộ biến: A = khách hàng + lịch sử; B = A + kênh/tháng/thứ; C = B + 5 chỉ số vĩ mô.
- **Đánh giá**: (a) hold-out ngẫu nhiên 75/25 có phân tầng; (b) CV 5 lần ngẫu nhiên; (c) kiểm tra theo thời gian (chia 70/30 theo thứ tự, và 4 khối kế tiếp huấn luyện trên toàn bộ quá khứ).

## Kết quả (hold-out ngẫu nhiên, tập test 10.297 khách hàng, tỷ lệ đăng ký 11,3%)
| Mô hình | AUC | PR-AUC | Thu hồi top 20% | Lift top 20% |
|---|---|---|---|---|
| Ngẫu nhiên | 0,500 | 0,113 | 20% | 1,0 |
| Quy tắc poutcome=success | 0,592 | 0,244 | 34% | 1,7 |
| Logistic – bộ A | 0,701 | 0,333 | 44% | 2,2 |
| Gradient Boosting – bộ A | 0,709 | 0,350 | 45% | 2,3 |
| Gradient Boosting – bộ B (không vĩ mô) | 0,787 | 0,434 | 61% | 3,0 |
| Logistic – bộ C | 0,806 | 0,467 | 64% | 3,2 |
| **Gradient Boosting – bộ C** | **0,814** | **0,486** | **66%** | **3,3** |

CV 5 lần ngẫu nhiên cho kết quả nhất quán (GB bộ C: AUC 0,801 ± 0,007; quy tắc đơn giản 0,590). Mô hình nhiều khả năng không cần phức tạp: Logistic chỉ kém ~0,01 AUC.

## Kiểm tra theo thời gian (kết quả thực tế hơn khi dùng cho chiến dịch sau)
| Khối test (10 khối theo thứ tự) | Tỷ lệ đăng ký | AUC quy tắc | AUC GB-A | AUC GB-B | AUC GB-C |
|---|---|---|---|---|---|
| 7 | 10,2% | 0,48 | 0,61 | 0,52 | 0,59 |
| 8 | 12,0% | 0,57 | 0,65 | 0,67 | 0,61 |
| 9 | 15,7% | 0,55 | 0,60 | 0,60 | 0,58 |
| 10 | 45,9% | 0,63 | 0,62 | 0,65 | 0,62 |
| Trung bình | | 0,56 | 0,62 | 0,61 | 0,60 |

Mô hình chỉ dùng thông tin khách hàng + lịch sử (bộ A) ổn định nhất (AUC trung bình 0,62, hơn quy tắc đơn giản khoảng 0,06). Thêm biến vĩ mô *không* giúp khi dự báo theo thời gian.

## Yếu tố quan trọng (permutation importance trên tập test, mức giảm AUC)
- Mô hình đầy đủ (C): `nr.employed` 0,051; `emp.var.rate` 0,022; `month` 0,011; `contact` 0,011; `cons.conf.idx` 0,008; `euribor3m` 0,007; `poutcome` 0,004; `pdays` 0,004.
- Nếu bỏ chỉ số vĩ mô (B): `month` 0,086; `contact` 0,064; `pdays` 0,024; `age` 0,016; `default` 0,008.
- Tỷ lệ đăng ký theo nhóm (đơn biến): `poutcome` success 65,1% / failure 14,2% / chưa liên lạc 8,8%; `contact` cellular 14,7% / telephone 5,2%; tháng 3, 9, 10, 12 đạt 44–51% nhưng cỡ mẫu nhỏ (182–718 cuộc), còn tháng 5 chỉ 6,4% (13.769 cuộc).
- Các biến vĩ mô tương quan chặt với nhau và với thời gian, nên không nên diễn giải từng biến riêng lẻ.

## Lưu ý quan trọng
1. **Dữ liệu không dừng (non-stationary)**: tỷ lệ đăng ký tăng từ ~3% (đầu 2008–2009) lên 31% ở 20% cuối, và 46% ở khối cuối cùng; euribor giảm từ ~4,9 xuống ~0,8; tỉ lệ khách có lịch sử liên lạc trước tăng từ 0 lên 51%. Giai đoạn cuối có thể do ngân hàng chọn khác tập khách hoặc do lãi suất thấp. Vì vậy hold-out ngẫu nhiên (trộn các giai đoạn) **lạc quan**: mô hình học được "tháng/vĩ mô nào = giai đoạn nào" chứ chưa hẳn là hành vi khách hàng. Đây là lý do con số 0,81 không nên được kỳ vọng ở chiến dịch mới.
2. Chỉ số vĩ mô của chiến dịch sắp tới chưa biết trước chắc chắn; nếu dùng cần nhập giá trị dự kiến.
3. Dữ liệu quan sát: các yếu tố ở đây là liên quan, không chứng minh nhân quả (ví dụ chọn kênh di động có thể do khách vốn tích cực hơn).
4. Chưa hiệu chỉnh xác suất, chưa tính chi phí mỗi cuộc gọi/giá trị mỗi hợp đồng, nên chưa chọn được ngưỡng gọi tối ưu.

## Đề xuất
- Dùng điểm số để **xếp thứ tự ưu tiên** (ví dụ gọi nhóm top 20% trước), chạy thử nhỏ (A/B với gọi ngẫu nhiên) trong chiến dịch mới để xác nhận lift, rồi huấn luyện lại bằng dữ liệu mới nhất.
- Ưu tiên khách từng đăng ký ở chiến dịch trước, liên hệ qua di động.

## Tệp
`analysis.py`, `ket_qua_holdout_ngau_nhien.csv`, `ket_qua_cv_ngau_nhien.csv`, `ket_qua_mo_hinh.csv` (chia theo thời gian 70/30), `kiem_tra_theo_thoi_gian.csv`, `do_quan_trong_*.csv`, `bang_decile*.csv`, `so_sanh_baseline.png`, `duong_thu_hoi.png`, `do_quan_trong.png`.
