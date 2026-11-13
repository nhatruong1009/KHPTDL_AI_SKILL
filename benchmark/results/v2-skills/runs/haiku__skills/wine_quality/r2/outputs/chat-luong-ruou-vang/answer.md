# Câu trả lời

**Dữ liệu chỉ trả lời được một phần câu hỏi.** Bộ dữ liệu (`winequality-red.csv`, `winequality-white.csv`) chỉ gồm 1.599 mẫu rượu vang đỏ và 4.898 mẫu rượu vang trắng, đều là rượu *Vinho Verde* của Bồ Đào Nha, kèm các chỉ số hóa lý và điểm chất lượng cảm quan (0-10). Dữ liệu **không có** giống nho, giá bán, cũng như vùng hay quốc gia xuất xứ.

- **Giống nho và mức giá cho rượu chất lượng cao nhất:** không thể trả lời từ dữ liệu này. Không có cột giống nho hay giá nên không xác định được.
- **Rượu Pháp có được chấm điểm cao hơn rượu Bồ Đào Nha không:** không thể trả lời. Toàn bộ mẫu là rượu Bồ Đào Nha, không có rượu Pháp để so sánh.

**Những gì dữ liệu cho thấy:**

1. **Rượu vang trắng được chấm điểm cao hơn rượu vang đỏ.** Điểm trung bình là 5,88 (trắng) so với 5,64 (đỏ), p = 3,6e-23 (Mann-Whitney). Khi loại các mẫu trùng lặp hoàn toàn (kiểm tra độ nhạy), chênh lệch vẫn còn: 5,86 so với 5,62, p = 2e-18. Tỷ lệ mẫu đạt từ 7 điểm trở lên là 21,6% ở rượu trắng và 13,6% ở rượu đỏ. Đây là sự khác biệt về **loại rượu (đỏ/trắng)** chứ không phải giống nho, và chỉ áp dụng cho rượu Vinho Verde.
2. **Nồng độ cồn là yếu tố liên quan mạnh nhất tới điểm cao.** Tương quan Spearman với điểm là 0,48 ở rượu đỏ và 0,44 ở rượu trắng. Điểm trung bình tăng đều theo nhóm cồn: rượu đỏ từ 5,35 (8-9%) lên 6,44 (12%+); rượu trắng từ 5,61 lên 6,59.
3. **Rượu có điểm cao (từ 8 trở lên) rất hiếm:** 198 mẫu, trong đó 180 là rượu trắng (3,7% số rượu trắng) và 18 là rượu đỏ (1,1% số rượu đỏ). Nhóm này thường có nồng độ cồn khoảng 12%, độ axit bay hơi thấp (~0,26-0,37 g/dm³) và sulphates cao hơn ở rượu đỏ (median 0,74).

**Phương pháp:** Đọc hai file với dấu chấm phẩy làm dấu phân cách; gộp hai loại rượu; so sánh bằng Mann-Whitney (điểm là thang thứ bậc); tương quan Spearman trong từng loại; chia nhóm theo nồng độ cồn. Mã nguồn và kết quả nằm trong `outputs/chat-luong-ruou-vang/`.

**Hạn chế:**
- Dữ liệu quan sát, chỉ cho thấy liên quan chứ không phải nhân quả. Nồng độ cồn đi cùng điểm cao không có nghĩa là tăng cồn làm rượu ngon hơn.
- Điểm chất lượng là điểm cảm quan trung vị của ít nhất 3 chuyên gia, nên có tính chủ quan.
- Kết luận chỉ áp dụng cho rượu Vinho Verde, không khái quát được cho rượu Pháp hay rượu Bồ Đào Nha nói chung.
- Có 240 mẫu trùng lặp ở rượu đỏ và 937 ở rượu trắng. Kết quả chính giữ nguyên khi loại trùng lặp.
- Rất ít mẫu có điểm 3 hoặc 9, nên các nhóm điểm cực đoan có độ tin cậy thấp.
