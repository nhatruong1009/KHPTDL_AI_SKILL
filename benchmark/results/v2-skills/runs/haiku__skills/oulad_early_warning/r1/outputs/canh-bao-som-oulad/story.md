# Cảnh báo sớm: nhìn thấy nguy cơ trong 4 tuần đầu, nhưng 70% chỉ đạt khi cảnh báo hơn một nửa sinh viên

**Thông điệp chính:** Sinh viên không hoàn thành đã khác biệt rõ ngay trong tuần đầu, và mô hình 28 ngày đầu phân biệt được họ ở mức trung bình khá (AUC 0.72). Nhưng để bắt được 70% sinh viên không hoàn thành, nhà trường phải liên hệ với khoảng 54% sinh viên, và hạn mức 200 suất mỗi module-kỳ chỉ bao phủ được khoảng 23% số đó.

## 1. Bối cảnh

Nhà trường muốn biết sớm sinh viên nào cần hỗ trợ, với mốc quyết định là cuối ngày 28 của khóa. Dữ liệu gồm 13,020 lượt đăng ký còn học đến ngày 28 của BBB và FFF qua bốn kỳ.

## 2. Diễn biến: khác biệt đã có từ tuần 1

Sinh viên Pass có trung vị 59 lượt truy cập trong tuần 1; Withdrawn 33; Fail 20. Khoảng cách không thu hẹp về cuối: đến tuần 4, Pass vẫn gấp khoảng hai lần Fail. Chỉ báo mạnh nhất là số ngày hoạt động trong 28 ngày đầu, với khả năng phân tách khoảng 0.67. Sự khác biệt có ý nghĩa thống kê ngay từ tuần 1 và kéo dài đến tuần 4.

Tín hiệu sớm nhất là dấu hiệu: không nộp TMA1 (97% ở nhóm hoàn thành so với 76% ở nhóm không hoàn thành), không có hoạt động trên hệ thống học trực tuyến, và lâu không quay lại hệ thống.

## 3. Cảnh báo: mô hình có ích, nhưng không đủ để đạt 70% với ngưỡng cố định

Mô hình hồi quy logistic dùng 28 ngày đầu có AUC 0.72 trên tập test 2014J, so với 0.65 khi chỉ dùng lượt truy cập tổng. Ngưỡng cố định chốt trên validation chỉ bắt được 64% sinh viên không hoàn thành. Muốn đạt 70%, phải cảnh báo 54% sinh viên, với precision chỉ 51%.

Đây là đánh đổi thực tế. Một hệ thống chỉ đủ nhân lực cho 200 người mỗi module-kỳ không thể đạt 70% recall. Trong 400 sinh viên được ưu tiên ở tập test, 322 (80%) không hoàn thành, nhưng đó chỉ là 23% tổng số không hoàn thành.

## 4. Hành động: ưu tiên và giải thích cho cố vấn

Quy tắc ưu tiên: trong mỗi module-kỳ, xếp sinh viên theo xác suất không hoàn thành ước tính và lấy 200 đầu tiên. Với mỗi sinh viên trong danh sách, hệ thống tạo sẵn đoạn 2–3 câu cho cố vấn, nêu các dấu hiệu chính (thường là lượt truy cập thấp trong 28 ngày đầu, chưa nộp TMA1 đúng hạn, hoạt động ít ở tuần 2 và 4).

Đề xuất:

1. Dùng danh sách 200 mỗi module-kỳ như mốc vận hành đầu tiên, và thông báo rõ là hệ thống chỉ bắt được khoảng một phần ba số không hoàn thành.
2. Nếu nhân lực cho phép, tăng số suất (300 suất bắt được khoảng 32%); đây là đòn bẩy lớn nhất.
3. Trước khi triển khai kỳ mới, đặt lại ngưỡng vì tỷ lệ không hoàn thành khác nhau giữa các kỳ, và kiểm tra recall theo nhóm (một số nhóm thấp hơn đáng kể).

Lưu ý: đây là tương quan trong dữ liệu quan sát. Danh sách giúp cố vấn tìm sinh viên cần trò chuyện, không xác định nguyên nhân hay đảm bảo can thiệp sẽ hiệu quả.
