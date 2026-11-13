# Câu chuyện: mô hình dự đoán đăng ký tiền gửi không vượt được luật đơn giản

**Thông điệp chính:** Với dữ liệu chiến dịch 2008–2010, mô hình dự đoán khách đăng ký trước khi gọi không tốt hơn luật "ưu tiên khách có kết quả chiến dịch trước" khi kiểm tra trên giai đoạn sau. Con số AUC 0,80 đẹp mắt chỉ xuất hiện khi trộn các giai đoạn lại với nhau.

**Bối cảnh.** Ngân hàng muốn biết nên gọi ai trước trong chiến dịch tiền gửi có kỳ hạn. Dữ liệu có 41.188 khách và kết quả đăng ký của họ.

**Căng thẳng.** Tỷ lệ đăng ký tăng từ khoảng 2% lên khoảng 50% khi chiến dịch đi qua các năm. Mô hình học tốt trên giai đoạn đầu nhưng không dự đoán được giai đoạn sau. Trên tập test theo thời gian, AUC của mô hình là 0,577, còn luật đơn giản là 0,625.

**Phát hiện.**
1. Luật đơn giản (khách có kết quả chiến dịch trước thành công) đặt 20% khách đầu có tỷ lệ đăng ký gấp 1,77 lần mức nền.
2. Mô hình tốt nhất đạt 1,23 lần, và không ổn định qua các cách chia.
3. Yếu tố mạnh nhất là chỉ số kinh tế và tháng gọi, tức là dấu hiệu giai đoạn chứ không phải lý do khách đăng ký.

**Hành động.** Dùng luật đơn giản làm chuẩn cho chiến dịch sắp tới. Thu thập dữ liệu hiện tại và đánh giá lại trước khi triển khai mô hình. Kiểm tra cẩn thận nhóm khách trên 60, nơi mô hình xếp hạng kém nhất.

**Đối tượng.** Người quản lý chiến dịch tiếp thị, cần quyết định nên gọi ai và nên tin vào công cụ nào.
