# Câu chuyện: 28 ngày đầu đã nói lên nhiều điều, nhưng chưa đủ

Chỉ sau bốn tuần, sinh viên sẽ hoàn thành và không hoàn thành đã tách nhau rõ: sinh viên Pass có median 257 click, Withdrawn 161, Fail chỉ 112; sự chênh lệch xuất hiện ngay từ tuần 1 và gần như không rộng thêm sau tuần 2. Dấu hiệu mạnh nhất là số ngày có vào học (12 so với 7) và việc nộp bài TMA1 đúng hạn.

Tuy nhiên mỗi dấu hiệu riêng lẻ chỉ phân biệt ở mức vừa phải. Mô hình tổng hợp đạt AUC 0,69 trên kỳ 2014J chưa từng thấy; với ngưỡng chọn từ kỳ trước, mô hình bắt được 65% sinh viên không hoàn thành, thấp hơn mục tiêu 70% do tỷ lệ bỏ cuộc của kỳ mới thấp hơn. Mô hình tốt ở FFF (recall 75%) nhưng yếu ở BBB (54%).

Về vận hành: với 200 liên hệ mỗi module-kỳ, danh sách ưu tiên theo điểm rủi ro trúng 76% (gấp 2 lần ngẫu nhiên), nhưng chỉ chạm 22% tổng số người sẽ không hoàn thành — trần lý thuyết là 29%. Nhà trường cần chọn: tăng nhân lực (~1.900 liên hệ để đạt 70%) hoặc chấp nhận mục tiêu "giúp đúng người nguy cơ cao nhất". Nên theo dõi công bằng (recall của nữ 57% so với nam 73%) trước khi triển khai.
