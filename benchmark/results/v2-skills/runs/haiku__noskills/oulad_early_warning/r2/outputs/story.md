# Câu chuyện: phát hiện sớm sinh viên cần hỗ trợ trước ngày 28

Trong 8 module-kỳ của BBB và FFF, có 13.020 sinh viên còn theo học đến cuối ngày 28. Gần một nửa (43%) trong số họ sẽ không hoàn thành khóa học: 3.469 người Fail và 2.152 người Withdrawn.

**Dấu hiệu đã xuất hiện từ tuần đầu.** Sinh viên hoàn thành nhấp chuột gần gấp đôi sinh viên Fail trong bốn tuần đầu (trung bình 103 so với 55 lượt nhấp ở tuần 1). Sinh viên Withdrawn nằm giữa hai nhóm. Khác biệt này có ý nghĩa ngay tuần 1, nên nhà trường không cần chờ đến cuối tháng mới biết ai có nguy cơ.

**Hai tín hiệu mạnh nhất.** Một là việc nộp bài đánh giá TMA1 đúng hạn: 94% sinh viên hoàn thành nộp đúng hạn, so với 67% ở nhóm không hoàn thành. Hai là khoảng thời gian kể từ lần truy cập cuối: nhóm không hoàn thành thường đã vắng mặt trên hệ thống lâu hơn (trung vị 3 ngày so với 1 ngày ở nhóm hoàn thành).

**Mô hình chỉ dùng dữ liệu đến ngày 28.** Mô hình dự báo đạt AUC 0,70 trên kỳ 2014J, không dùng nhân khẩu học. Ở ngưỡng được chọn để bắt ít nhất 70% sinh viên không hoàn thành, mô hình bắt được 73%. Cái giá là phải đánh dấu 56% sinh viên, trong đó khoảng một nửa là báo động nhầm. Hiệu năng cũng thấp hơn ở kỳ mới so với kỳ đã học, nên mô hình cần được theo dõi và huấn luyện lại khi có kỳ mới.

**Nhân lực là điểm nghẽn.** Với 200 suất liên hệ mỗi module-kỳ, nhà trường có thể liên hệ 1.600 sinh viên (12%). Danh sách này có precision 86%, nhưng chỉ bắt được khoảng một phần tư (1.376 / 5.621) số sinh viên không hoàn thành. Để đạt 70%, cần khoảng 6.360 suất, tức gần một nửa cohort. Nhà trường cần chọn một trong hai hướng: tăng nhân lực, hoặc chấp nhận mục tiêu thấp hơn và tập trung vào nhóm có rủi ro cao nhất.

**Gợi ý cho cố vấn.** Với mỗi sinh viên trong danh sách, phần lớn yếu tố chính liên quan đến TMA1 (chưa có điểm, nộp trễ hoặc điểm thấp) và đến khoảng thời gian không truy cập gần đây. Cố vấn nên bắt đầu bằng việc hỏi về bài TMA1 và lên kế hoạch nộp bài, rồi tìm hiểu lý do sinh viên ít truy cập hệ thống.

**Lưu ý.** Tỷ lệ chuyển đổi 14% trong tham số giả định chưa được kiểm chứng từ dữ liệu. Sinh viên rút trước ngày 28 không nằm trong bài toán này.
