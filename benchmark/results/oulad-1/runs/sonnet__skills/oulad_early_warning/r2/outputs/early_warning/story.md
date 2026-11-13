# Câu chuyện dữ liệu: Phát hiện sớm sinh viên cần hỗ trợ trước ngày 28

**Thông điệp chính:** Chỉ 4 tuần đầu đã đủ để thấy ai đang tụt lại, nhưng tín hiệu chỉ ở mức vừa phải - hệ thống nên là công cụ *ưu tiên* người cần liên hệ, chưa phải công cụ "bắt hết" (mục tiêu 70% chưa đạt với 200 cuộc liên hệ mỗi module-kỳ).

## Bối cảnh
13.020 sinh viên BBB và FFF còn theo học đến hết ngày 28; 43% cuối cùng không hoàn thành (Fail hoặc Withdrawn). Nhà trường chỉ đủ nhân lực liên hệ 200 người mỗi module-kỳ.

## 1. Khác biệt xuất hiện ngay từ tuần 1
Trong 28 ngày đầu, sinh viên Pass vào học trung vị 12 ngày và 257 lượt click; Withdrawn 9 ngày / 160 lượt; Fail chỉ 7 ngày / 112 lượt. Khoảng cách đã rõ từ tuần 1 và gần như không đổi sau đó. (`q1_weekly_engagement.png`, `q2_effect_by_week.png`)

## 2. Hai tín hiệu dễ nhận nhất
Số ngày vào học và việc nộp bài TMA1. Sinh viên chưa nộp TMA1 trước ngày 28 có 81-93% không hoàn thành ở cả 8 module-kỳ. (`q2_top_indicators.png`)

## 3. Dự báo được, nhưng không hoàn hảo
Trên kỳ test 2014J, mô hình đạt AUC 0,72. Để bắt 70% sinh viên không hoàn thành phải gắn cờ khoảng một nửa số sinh viên, và gần một nửa trong số đó vẫn sẽ hoàn thành. (`q3_model_performance.png`)

## 4. Với 200 người mỗi module-kỳ
Danh sách ưu tiên trúng 72,8% (291/400) so với 37,8% nếu chọn ngẫu nhiên - nhưng chỉ bao phủ 21% tổng số sinh viên không hoàn thành. Quy tắc đơn giản "chưa nộp TMA1, rồi ít ngày hoạt động" trúng 80,5% trên test. (`q4_priority_list.png`)

## 5. Hành động đề xuất
- Liên hệ trước nhóm chưa nộp TMA1 và vào học rất ít ngày; dùng lời nhắn sẵn có theo từng sinh viên (`q5_priority_list_with_reasons.csv`).
- Với nhóm rủi ro vừa còn lại, cân nhắc kênh rẻ hơn (nhắn tin tự động).
- Xác nhận với bộ phận dữ liệu về thang điểm TMA1 bất thường ở BBB 2014J; theo dõi độ chính xác mỗi kỳ và công bằng giữa các nhóm.

*Lưu ý: đây là mối liên hệ, không phải nhân quả; hiệu quả can thiệp (giả định 14%) chưa được kiểm chứng.*
