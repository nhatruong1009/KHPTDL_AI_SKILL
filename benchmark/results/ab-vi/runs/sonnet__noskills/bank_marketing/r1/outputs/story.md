# Câu chuyện dữ liệu: nên gọi cho ai?

1. **Vấn đề:** chỉ 11,3% cuộc gọi dẫn đến đăng ký tiền gửi có kỳ hạn; tổng đài cần xếp hạng khách để gọi người có khả năng cao trước.
2. **Cách làm:** dùng bộ dữ liệu đầy đủ (41.188 khách), bỏ `duration` vì chỉ biết sau cuộc gọi.
3. **Kết quả:** mô hình đạt AUC 0,80; gọi 10% khách đầu bảng cho tỷ lệ thành công 51% (gấp 4,6 lần), bắt được 46% người đăng ký. Quy tắc đơn giản chỉ đạt AUC 0,60.
4. **Yếu tố chính:** bối cảnh kinh tế (lãi suất euribor, việc làm), tháng gọi, kênh di động, kết quả chiến dịch trước, nhóm sinh viên/hưu trí.
5. **Giới hạn:** tỷ lệ đăng ký thay đổi theo thời kỳ; khi kiểm tra theo trục thời gian, AUC giảm còn ~0,66 và không vượt baseline chỉ-euribor. Cần huấn luyện lại thường xuyên và thử nghiệm đối chứng trước khi triển khai rộng.
