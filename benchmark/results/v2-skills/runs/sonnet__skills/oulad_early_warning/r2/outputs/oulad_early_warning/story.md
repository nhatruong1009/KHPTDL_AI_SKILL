# Câu chuyện dữ liệu: bắt tín hiệu bỏ học ngay từ ngày 28

**Thông điệp chính:** Sau 4 tuần, dữ liệu đã đủ để chỉ ra nhóm sinh viên rất dễ không hoàn thành, nhưng chưa đủ để bắt được hầu hết họ. Với 200 chỗ liên hệ mỗi module-kỳ, nhà trường nên coi danh sách là "ca chắc chắn nhất", không phải toàn bộ bức tranh.

1. **Bối cảnh.** 13.020 lượt đăng ký của BBB và FFF còn học đến ngày 28. Nhà trường muốn một danh sách cảnh báo để cố vấn liên hệ.
2. **Dấu hiệu có từ tuần 1.** Trung vị clicks tuần 1 là 59 (Pass), 33 (Withdrawn), 20 (Fail). Giữa hoàn thành và không hoàn thành, khác biệt tuần 1 (hiệu ứng 0,26) gần bằng tuần 4 (0,29). Không cần chờ đến tuần 4 để thấy tín hiệu. Hình: `q1_tuong_tac_theo_nhom.png`, `q2_khac_biet_theo_tuan.png`.
3. **Dự báo được ở mức vừa.** AUC test 0,736, so với 0,50 nếu đoán theo tỷ lệ nền. Ngưỡng chọn để bắt 70% ở validation chỉ bắt được 57,5% trên test, nên **mục tiêu 70% chưa đạt**. Hình: `q3_q4_recall_precision.png`.
4. **Danh sách 200 người/module-kỳ rất chính xác nhưng phủ hẹp.** 83,2% là người không hoàn thành (nền 37,8%), nhưng chỉ phủ 24,2% tổng số. Muốn phủ 70% cần khoảng 860–930 liên hệ mỗi module-kỳ.
5. **Hành động đề xuất (gợi ý, không phải kết quả):**
   - Ưu tiên liên hệ người chưa nộp TMA1 kèm ít tương tác. Đây là lý do hàng đầu của 336/400 người trong danh sách.
   - Hiệu chỉnh lại ngưỡng theo từng kỳ.
   - Dùng kênh nhẹ (nhắn tin tự động) cho nhóm rủi ro vừa nằm ngoài 200 chỗ.
   - Theo dõi chênh lệch recall giữa các nhóm (ví dụ nam so với nữ).

*Mọi số liệu lấy từ `answer.md` và các CSV trong thư mục này. Đây là quan hệ thống kê, không phải nhân quả.*
