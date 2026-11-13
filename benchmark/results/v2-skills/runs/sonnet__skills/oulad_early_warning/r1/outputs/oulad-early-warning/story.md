# Câu chuyện dữ liệu: cảnh báo sớm ở ngày 28

**Thông điệp chính:** Chỉ sau 4 tuần, hành vi học tập đã tách sinh viên sắp không hoàn thành khỏi những người sẽ qua môn, nhưng tín hiệu chỉ ở mức vừa phải. Với 200 lượt liên hệ mỗi module-kỳ, nhà trường sẽ liên hệ đúng người khoảng 4 trên 5 lần, song chỉ chạm tới khoảng 1 trên 4 sinh viên sẽ không hoàn thành.

1. **Bối cảnh.** 13.020 lượt đăng ký còn học đến ngày 28; 43% cuối cùng không hoàn thành (Fail hoặc Withdrawn). Xem `q1_weekly_by_outcome.png`: nhóm Pass có click trung vị tuần 1 là 59, Withdrawn 33, Fail 20.
2. **Điểm khác biệt.** Khác biệt đã xuất hiện từ tuần 1, thậm chí trước khi khóa bắt đầu. Số ngày vào học và việc nộp TMA1 là hai tín hiệu rõ nhất (`q2_indicator_effects.png`).
3. **Căng thẳng.** Mô hình đạt AUC 0,71 trên kỳ 2014J (chưa từng dùng khi huấn luyện). Đạt 70% recall nghĩa là gắn cờ 53% sinh viên với độ chính xác 50% (`q3_model_performance.png`).
4. **Hành động.** Với giới hạn 200 người/module-kỳ: trúng 80,5% nhưng bao phủ 23,4%; cần 888–1.032 lượt liên hệ để đạt 70%. Quy tắc đơn giản "chưa nộp TMA1, rồi ít click" gần như tốt ngang mô hình (78,8%) và dễ giải thích hơn (`q4_top200_precision.png`).
5. **Gợi ý (không phải kết luận):** bắt đầu bằng quy tắc đơn giản kèm danh sách của mô hình để đối chiếu; kiểm tra hạn TMA1 của FFF; theo dõi sai số theo nhóm (khuyết tật, tuổi 35–55); đo thực tế xem liên hệ có giúp sinh viên ở lại hay không, vì dữ liệu này chỉ cho thấy liên quan, không phải nhân quả.

Mọi con số lấy từ `answer.md` và các file CSV cùng thư mục.
