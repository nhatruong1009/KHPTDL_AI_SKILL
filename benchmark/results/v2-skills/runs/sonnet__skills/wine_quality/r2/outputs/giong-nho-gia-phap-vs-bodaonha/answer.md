# Giống nho, mức giá và Pháp vs Bồ Đào Nha: dữ liệu này không trả lời được

## Kết luận
**Không thể trả lời cả hai câu hỏi từ bộ dữ liệu này.**

| Khái niệm trong câu hỏi | Cột trong dữ liệu | Trạng thái |
|---|---|---|
| Giống nho | không có | [MISSING] |
| Mức giá | không có | [MISSING] |
| Quốc gia / xuất xứ (Pháp) | không có | [MISSING] |
| Chất lượng | `quality` (điểm 0-10, trung vị của ≥3 chuyên gia) | [OK] |

- Tài liệu `winequality.names` nói rõ: "there is no data about grape types, wine brand, wine selling price".
- Toàn bộ 6.497 mẫu (1.599 vang đỏ, 4.898 vang trắng) là vang **Vinho Verde của Bồ Đào Nha**. Không có mẫu nào của Pháp, nên không thể so sánh Pháp với Bồ Đào Nha.
- Tôi không trả lời bằng kiến thức bên ngoài như thể nó đến từ dữ liệu.

## Dữ liệu cần có
Một cột giống nho, giá bán và quốc gia cho từng chai, kèm điểm chấm, trong đó có cả vang Pháp.

## Những gì dữ liệu này trả lời được (phân tích phụ, đã chạy)
Loại vang (đỏ/trắng) **không phải** giống nho. Đây chỉ là phân tích gần nhất có thể làm.

| Loại | Số mẫu | Điểm TB | Trung vị | % điểm ≥ 7 |
|---|---|---|---|---|
| Đỏ | 1.599 | 5,64 | 6 | 13,6% |
| Trắng | 4.898 | 5,88 | 6 | 21,6% |

- Vang trắng được chấm cao hơn vang đỏ. Mann-Whitney có p ≈ 4e-23. Kết quả vẫn giữ nguyên sau khi loại các dòng trùng lặp (đỏ 5,62 vs trắng 5,86; p ≈ 2e-18).
- Hiệu số khoảng 0,24 điểm, là mức nhỏ.
- Trong nhóm điểm ≥ 7, cả đỏ và trắng đều có **độ cồn cao hơn** (đỏ 11,5 so với 10,3; trắng 11,4 so với 10,3). Đây là liên hệ thống kê, không chứng minh nhân quả.
- Với vang đỏ, nhóm điểm cao còn có độ axit bay hơi thấp hơn (0,41 so với 0,55).

## Lưu ý
- 240 dòng trùng ở file đỏ và 937 dòng trùng ở file trắng. Tôi chưa xác định đó là lỗi hay các mẫu lặp hợp lệ, nên đã kiểm tra lại kết quả khi loại chúng.
- Điểm chấm mang tính chủ quan và lệch về giữa thang (hầu hết là 5-6).
- Dữ liệu chỉ cho thấy mối liên hệ, không cho thấy nhân quả.

Mã và bảng kết quả: `analysis.py`, `quality_by_type.csv`, `profile_high_quality.csv`.

## Câu hỏi liên quan mà dữ liệu trả lời được
1. Đặc tính hóa lý nào (độ cồn, độ axit...) gắn với điểm chất lượng cao ở vang đỏ và vang trắng?
2. Vang trắng có được chấm cao hơn vang đỏ không? Câu trả lời là có, ở mức chênh nhỏ.
