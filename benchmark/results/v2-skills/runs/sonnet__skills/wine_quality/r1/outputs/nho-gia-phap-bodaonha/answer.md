# Kết luận: dữ liệu KHÔNG đủ để trả lời câu hỏi này

**Câu hỏi:** (1) Giống nho nào và mức giá nào cho rượu vang chất lượng cao nhất? (2) Rượu vang Pháp có điểm cao hơn rượu vang Bồ Đào Nha không?

## Đối chiếu khái niệm với cột dữ liệu

| Khái niệm | Cột | Trạng thái |
|---|---|---|
| Giống nho | – | [THIẾU] |
| Mức giá | – | [THIẾU] |
| Quốc gia (Pháp / Bồ Đào Nha) | – | [THIẾU] |
| Chất lượng / điểm | `quality` (trung vị điểm của ít nhất 3 chuyên gia, thang 0–10) | [OK] |

Tệp `winequality.names` ghi rõ: "there is no data about grape types, wine brand, wine selling price, etc." Toàn bộ 6.497 mẫu (1.599 vang đỏ, 4.898 vang trắng) đều là vang **Vinho Verde của Bồ Đào Nha**. Không có mẫu nào của Pháp, nên không thể so sánh Pháp với Bồ Đào Nha. Quét tên cột cũng không thấy cột nào về giống nho, giá hay quốc gia.

→ **Quyết định: Không liên quan (Not relevant).** Mình không trả lời từ kiến thức chung như thể nó đến từ dữ liệu này.

## Cần dữ liệu gì
Bảng có mỗi dòng là một chai/mẫu vang, kèm giống nho (variety), giá, quốc gia/vùng và điểm chấm (ví dụ bộ "wine reviews").

## Những câu hỏi dữ liệu này trả lời được
- Vang đỏ hay vang trắng Vinho Verde được chấm cao hơn? (xem bên dưới)
- Đặc tính hoá lý nào (cồn, độ acid bay hơi, …) gắn với điểm cao?

## Phép tính phụ (chỉ để tham khảo, không trả lời câu hỏi gốc)
Điểm `quality` theo loại vang Vinho Verde (`quality_red_vs_white.csv`):

| Loại | n | Trung bình | Trung vị | Độ lệch chuẩn |
|---|---|---|---|---|
| Đỏ | 1.599 | 5,64 | 6 | 0,81 |
| Trắng | 4.898 | 5,88 | 6 | 0,89 |

Kiểm định Mann–Whitney cho p ≈ 4e-23. Chênh lệch trung bình là 0,24 điểm, khá nhỏ.

**Lưu ý:** đây là so sánh đỏ với trắng trong cùng một vùng, không phải Pháp với Bồ Đào Nha. Dữ liệu cũng có trùng lặp (240 dòng ở vang đỏ, 937 dòng ở vang trắng), mình giữ nguyên chúng trong phép tính này. Đây chỉ là mối liên hệ quan sát được, không phải quan hệ nhân quả.
