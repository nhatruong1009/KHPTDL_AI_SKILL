# Trả lời: giống nho, mức giá và rượu vang Pháp so với Bồ Đào Nha

## Ngắn gọn

- **Dữ liệu không trả lời được câu hỏi về giống nho và mức giá.** Bộ dữ liệu (`winequality-red.csv`, `winequality-white.csv`) chỉ có 11 chỉ số hóa lý và 1 điểm chất lượng cảm quan. Mô tả trong `winequality.names` ghi rõ: không có thông tin về giống nho, thương hiệu hay giá bán.
- **Dữ liệu không có rượu vang Pháp.** Toàn bộ mẫu là rượu vang *Vinho Verde* của Bồ Đào Nha (vùng Minho), gồm 1.599 mẫu đỏ và 4.898 mẫu trắng. Vì vậy không thể so sánh rượu Pháp với rượu Bồ Đào Nha.
- **Điều dữ liệu cho phép nói:** trong nhóm Vinho Verde, rượu có nồng độ cồn cao hơn thường được chấm điểm cao hơn. Đây là một mối liên hệ thống kê, không phải bằng chứng nhân quả, và không phải thông tin về giá.

## Những gì dữ liệu cho thấy

Điểm chất lượng nằm trong thang 0–10, do chuyên gia nếm chấm (trung vị của ít nhất 3 lần đánh giá).

| Loại rượu | Số mẫu | Điểm TB | Trung vị | Điểm cao nhất |
|---|---|---|---|---|
| Vang đỏ | 1.599 | 5,64 | 6 | 8 |
| Vang trắng | 4.898 | 5,88 | 6 | 9 |

Điểm trung bình của rượu trắng cao hơn đỏ khoảng 0,24 điểm. Đây là một khác biệt nhỏ.

Quan hệ giữa nồng độ cồn và điểm chất lượng (điểm trung bình theo nhóm cồn):

| Nồng độ cồn | Vang đỏ | Vang trắng |
|---|---|---|
| < 9,5% | 5,23 | 5,50 |
| 9,5–10,5% | 5,40 | 5,61 |
| 10,5–11,5% | 5,80 | 6,00 |
| ≥ 11,5% | 6,35 | 6,48 |

Hệ số tương quan giữa cồn và điểm là 0,48 (đỏ) và 0,44 (trắng).

Các đặc điểm của nhóm rượu được chấm từ 7 điểm trở lên (so với nhóm từ 4 điểm trở xuống):
- Rượu cao điểm có cồn trung bình khoảng 11,4–11,5%, còn rượu thấp điểm khoảng 10,2%.
- Độ axit bay hơi thấp hơn ở nhóm cao điểm, ví dụ 0,41 so với 0,72 g/dm³ ở vang đỏ.

## Lưu ý về cách hiểu câu hỏi

- "Chất lượng cao nhất" trong dữ liệu được hiểu là điểm cảm quan cao nhất. Nhóm rượu đạt 8 điểm (đỏ) và 9 điểm (trắng) đều rất ít mẫu (18 và 5 mẫu).
- Nồng độ cồn được dùng làm chỉ số gần nhất với "mức giá" theo nghĩa chất lượng/cấp độ. Nồng độ cồn không phản ánh giá bán.
- Mẫu vang đỏ và trắng là hai bộ riêng biệt và không cân bằng về số lượng. Phân tích này chỉ mô tả tương quan, không kiểm định nguyên nhân.

## Cần dữ liệu gì để trả lời đầy đủ

- Giống nho (ví dụ Touriga Nacional, Alvarinho, Cabernet Sauvignon) và vùng sản xuất.
- Giá bán hoặc giá bán lẻ.
- Quốc gia xuất xứ để so sánh Pháp với Bồ Đào Nha.

Phân tích được thực hiện bằng `../scripts/analyze.py` (Python chuẩn, không cần thư viện ngoài, chạy với `python3 -I`) trên dữ liệu gốc trong `data/`, không thay đổi dữ liệu.
