# Giống nho, mức giá và rượu Pháp vs Bồ Đào Nha

## Kết luận: dữ liệu KHÔNG trả lời được câu hỏi này
Dữ liệu (`winequality-red.csv` 1.599 mẫu, `winequality-white.csv` 4.898 mẫu) chỉ gồm 11 chỉ số hóa lý và điểm chất lượng (0–10, trung vị của ≥3 chuyên gia). Tệp `winequality.names` nói rõ: *"không có dữ liệu về giống nho, nhãn hiệu, giá bán"*. Toàn bộ mẫu là **Vinho Verde của Bồ Đào Nha**.

- Giống nho nào cho điểm cao nhất: không có cột giống nho → không trả lời được.
- Mức giá nào: không có cột giá → không trả lời được.
- Pháp vs Bồ Đào Nha: không có rượu Pháp, không có cột quốc gia → không so sánh được. Tôi không dùng kiến thức bên ngoài để bịa số.

## Thông tin gần nhất mà dữ liệu cho phép (chỉ là tham khảo, không thay thế câu trả lời)
Mã: `analysis.py`; kết quả: `red_vs_white.csv`, `corr_quality.csv`.

| Loại | n | Điểm TB | Trung vị | % điểm ≥7 |
|---|---|---|---|---|
| Vang đỏ | 1.599 | 5,64 | 6 | 13,6% |
| Vang trắng | 4.898 | 5,88 | 6 | 21,6% |

- Trắng được chấm cao hơn đỏ một chút (Mann-Whitney p ≈ 4e-23). Chênh lệch nhỏ, chỉ khoảng 0,24 điểm. Cả hai đều là Vinho Verde, nên đây không phải so sánh giữa các nước.
- Yếu tố hóa lý tương quan với điểm (gộp đỏ và trắng): cồn +0,44 (mạnh nhất), mật độ −0,31, axit bay hơi −0,27, clorua −0,20. Đây là tương quan, không phải quan hệ nhân quả, và cồn với mật độ có liên quan lẫn nhau.

## Cần dữ liệu gì
Dữ liệu cần có giống nho, giá bán và quốc gia xuất xứ, kèm điểm chấm. Ví dụ: Wine Reviews (Wine Enthusiast) có `variety`, `price`, `country`, `points`. Khi so sánh quốc gia cũng nên kiểm soát giá và giống nho.

## Giới hạn
Điểm chất lượng là chủ quan, nhiều mẫu tập trung ở 5–6. Đây là một vùng sản xuất duy nhất.
