# Câu trả lời: Giống nho, mức giá và rượu vang Pháp so với Bồ Đào Nha

**Kết luận: Không thể trả lời câu hỏi này bằng dữ liệu đã cung cấp.** Dữ liệu không có thông tin về giống nho, giá bán, hay xuất xứ quốc gia. Ngoài ra, toàn bộ rượu trong dữ liệu đều là rượu Vinho Verde của Bồ Đào Nha, nên không có mẫu rượu Pháp nào để so sánh.

## Vì sao không trả lời được

| Phần của câu hỏi | Cần cột | Dữ liệu có không? |
|---|---|---|
| Giống nho nào cho chất lượng cao nhất | giống nho (grape variety) | Không. Không có cột nào |
| Mức giá nào cho chất lượng cao nhất | giá bán (price) | Không. Không có cột nào |
| Rượu Pháp có điểm cao hơn Bồ Đào Nha không | quốc gia / xuất xứ, và mẫu rượu Pháp | Không. Không có cột quốc gia, và không có rượu Pháp |

Kiểm tra bằng code (`analysis.py`, file `column_check.csv`) trên 14 từ khóa (grape, variety, price, country, origin, region, france, portugal, brand, producer, winery, ...): không cột nào khớp. Tệp `winequality.names` cũng nói rõ: "there is no data about grape types, wine brand, wine selling price, etc.".

## Dữ liệu thực tế có gì

- Hai tập: `winequality-red.csv` (1.599 mẫu) và `winequality-white.csv` (4.898 mẫu).
- 11 chỉ số lý-hóa (độ axit, đường dư, pH, nồng độ cồn, ...) và 1 điểm chất lượng từ 0 đến 10 do chuyên gia nếm đánh giá.
- Toàn bộ mẫu là Vinho Verde (Bồ Đào Nha). Loại rượu là cột duy nhất có thể tách nhóm.

Điểm chất lượng trung bình theo loại rượu (chỉ để tham khảo, chưa kiểm định thống kê):

| Loại | Số mẫu | Trung bình | Trung vị | Min | Max |
|---|---|---|---|---|---|
| Đỏ | 1.599 | 5,64 | 6 | 3 | 8 |
| Trắng | 4.898 | 5,88 | 6 | 3 | 9 |

## Gợi ý câu hỏi mà dữ liệu có thể trả lời

1. Rượu vang đỏ và trắng khác nhau về điểm chất lượng như thế nào, và sự khác biệt có ý nghĩa thống kê không? (Cần kiểm định, ví dụ Mann-Whitney.)
2. Những chỉ số lý-hóa nào liên quan nhiều nhất đến điểm chất lượng (ví dụ nồng độ cồn, độ axit bay hơi)? Đây là tương quan, không phải quan hệ nhân quả.
3. Có thể dự đoán điểm chất lượng từ các chỉ số lý-hóa không?

Để trả lời câu hỏi gốc về giống nho, giá và xuất xứ, cần một bộ dữ liệu có các cột đó, ví dụ có cột `variety`, `price`, `country` cho mỗi chai rượu.

## Phương pháp

- Đọc cả hai file CSV với dấu phân cách `;`. Đếm dòng và cột.
- So khớp tên cột với 14 từ khóa về giống nho, giá, quốc gia, nhãn hiệu.
- Tính thống kê mô tả điểm chất lượng theo loại rượu.
- Mã nguồn: `analysis.py`. Kết quả: `column_check.csv`, `columns.csv`, `quality_by_type.csv`.

## Hạn chế

- Kết luận dựa trên tên cột và tài liệu đi kèm dữ liệu. Không có thông tin nào khác về nguồn gốc mẫu ngoài tài liệu đó.
- Dữ liệu chỉ có một vùng sản xuất (Vinho Verde), nên không thể khái quát cho rượu vang các nước khác.
