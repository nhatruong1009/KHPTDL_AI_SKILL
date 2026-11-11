# Giống nho, mức giá và rượu vang Pháp so với Bồ Đào Nha

## Trả lời ngắn
**Dữ liệu này không trả lời được cả hai câu hỏi.**
- Không có cột nào về **giống nho** hay **giá bán**. Tài liệu `winequality.names` nói rõ: "there is no data about grape types, wine brand, wine selling price".
- Không có cột **quốc gia**. Toàn bộ 6.497 mẫu (1.599 vang đỏ, 4.898 vang trắng) là vang "Vinho Verde" của Bồ Đào Nha. Không có mẫu vang Pháp nào, nên không thể so Pháp với Bồ Đào Nha.

Tôi không đoán hay suy diễn cho các câu này.

## Phần dữ liệu có thể nói được (chỉ về vang Vinho Verde, Bồ Đào Nha)
Điểm chất lượng là trung vị của ít nhất 3 chuyên gia chấm, trên thang 0–10.

| Loại | Số mẫu | Điểm TB | Tỷ lệ điểm ≥7 |
|---|---|---|---|
| Trắng | 4.898 | 5,88 | 21,6% |
| Đỏ | 1.599 | 5,64 | 13,6% |

- Vang trắng được chấm cao hơn vang đỏ. Kiểm định Mann-Whitney cho p ≈ 4×10⁻²³. Chênh lệch khoảng 0,24 điểm, khá nhỏ.
- Yếu tố hoá lý liên quan nhất đến chất lượng (gộp đỏ và trắng):
  - **Nồng độ cồn** có tương quan dương: r = +0,44.
  - **Mật độ** (r = −0,31), **độ acid bay hơi** (r = −0,27) và **clorua** (r = −0,20) có tương quan âm.
- Ở cả hai loại vang, điểm tăng đều theo nồng độ cồn. Vang trắng có điểm TB 5,49 ở nhóm cồn dưới 9,5% và 6,51 ở nhóm trên 11,5%. Vang đỏ có 5,26 và 6,39 ở hai nhóm tương ứng. Xem `chat_luong_theo_con.png`.

## Cách làm và hạn chế
- Phương pháp: thống kê mô tả, kiểm định Mann-Whitney và tương quan Pearson trên dữ liệu gốc, không loại trùng lặp. Mã trong `analysis.py`.
- Đây là dữ liệu quan sát nên chỉ cho thấy mối liên hệ, không chứng minh nhân quả. Cồn cao đi cùng điểm cao, nhưng chưa chắc làm tăng điểm.
- Điểm số do chuyên gia chấm, mang tính chủ quan.
- Để trả lời câu hỏi gốc, cần một bộ dữ liệu có các cột giống nho (variety), giá (price) và quốc gia (country). Ví dụ là bộ đánh giá rượu vang Wine Enthusiast, tôi chưa dùng và chưa kiểm tra bộ này.
