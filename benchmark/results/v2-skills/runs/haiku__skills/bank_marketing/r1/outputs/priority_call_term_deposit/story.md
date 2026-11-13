# Câu chuyện: Chưa đủ bằng chứng để gọi khách theo mô hình dự đoán

**Thông điệp chính:** Trước khi gọi, các đặc điểm của khách hàng gần như không giúp xếp hạng họ. Điều thực sự có tác dụng là lịch sử chiến dịch trước và thời điểm gọi, và ngay cả chúng cũng không ổn định qua thời gian.

1. **Bối cảnh:** Chiến dịch tiền gửi có kỳ hạn gọi 41.188 khách của một ngân hàng Bồ Đào Nha (2008–2010). Tỷ lệ đăng ký chung là 11%.
2. **Xung đột:** Trên validation, mô hình trông rất tốt (AUC 0,66 so với 0,48 của baseline). Nhưng khi thử trên giai đoạn cuối (test), mô hình kém baseline đơn giản (AUC 0,58 so với 0,62).
3. **Nguyên nhân:** Tỷ lệ đăng ký tăng từ 3% lên 46% qua thời gian. Test rơi vào giai đoạn chưa từng có trong train. Các chỉ số kinh tế trôi theo thời gian và trở thành "đồng hồ" hơn là yếu tố khách hàng.
4. **Hành động gợi ý:** Ưu tiên khách có kết quả thành công ở chiến dịch trước (65% đăng ký) thay vì dùng mô hình. Nếu muốn mô hình, huấn luyện lại trên dữ liệu gần nhất và theo dõi hiệu quả theo tháng.

Biểu đồ đi kèm: [trôi dạt thời gian](bieu_do_5_troi_dat.png) → [đường tích lũy trên test](bieu_do_1_duong_tich_luy.png) → [yếu tố quan trọng](bieu_do_2_yeu_to_quan_trong.png) → [độ nhạy](bieu_do_3_do_nhay.png).
