# Câu chuyện dữ liệu: sinh viên nào cần được gọi trước ngày 28?

Hơn 13.000 sinh viên còn theo học đến cuối ngày 28 ở bốn kỳ của hai module BBB và FFF. Gần một nửa (43%) rồi sẽ không hoàn thành khóa học, hoặc bị điểm Fail hoặc rút môn. Câu hỏi là: với những gì biết được trong 28 ngày đầu, có thể nhận ra họ đủ sớm để hỗ trợ không?

**Tín hiệu đã xuất hiện ngay tuần đầu.** Sinh viên hoàn thành (Pass) có trung vị 59 lượt nhấp trong tuần 1, so với 20 ở nhóm Fail và 33 ở nhóm rút môn. Nhóm rút môn nằm giữa, không phải "Fail nhẹ hơn". Khoảng cách còn xuất hiện trước khi khóa học bắt đầu, nên thói quen học từ trước đã khác nhau.

**Sự khác biệt tích lũy.** Số ngày hoạt động lũy kế là chỉ báo tách nhóm rõ nhất theo thời gian: AUC tăng từ 0,63 ở tuần 1 lên 0,67 ở tuần 4. Ở ngày 28, khoảng cách kể từ lần truy cập cuối là tín hiệu mạnh nhất. Việc nộp bài đánh giá đầu tiên (TMA1) cũng rất quan trọng: 9 trên 10 sinh viên chưa nộp bài đến ngày 28 không hoàn thành.

**Dự báo được, nhưng chưa đủ để đạt mục tiêu.** Mô hình chỉ dùng dữ liệu đến ngày 28 đạt AUC 0,69 trên kỳ 2014J (chưa thấy trong quá trình huấn luyện). Với ngưỡng đặt để bắt 70% số sinh viên không hoàn thành trên kỳ kiểm tra, mô hình chỉ bắt được 64%. Để đạt 70%, phải cảnh báo khoảng một nửa lớp học, tức khoảng 1.900 người.

**Nguồn lực là điểm nghẽn.** Mỗi module-kỳ chỉ liên hệ được 200 sinh viên. Danh sách ưu tiên theo điểm rủi ro trúng 287 trên 400 người (72%). Nhưng đơn giản chọn người ít nhấp chuột nhất cũng trúng 289 người, nên mô hình không mang lại thêm lợi ích rõ rệt cho việc chọn danh sách. Quan trọng hơn, 200 suất chỉ bao phủ khoảng 1/5 số sinh viên không hoàn thành của mỗi module. Nhà trường cần cân nhắc: tăng năng lực liên hệ, hay chấp nhận rằng hệ thống chỉ là công cụ ưu tiên chứ không phải lưới an toàn.

**Lời khuyên cho cố vấn.** Với mỗi sinh viên trong danh sách, lý do chính thường là một trong hai điều: chưa nộp TMA1, hoặc đã nộp nhưng điểm thấp. Cuộc gọi đầu tiên nên hỏi về khó khăn cụ thể, không chỉ nhắc nhở chung chung.
