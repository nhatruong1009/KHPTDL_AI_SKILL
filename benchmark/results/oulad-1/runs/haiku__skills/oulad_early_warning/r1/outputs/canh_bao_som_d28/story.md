# Ai cần hỗ trợ trước ngày 28?

**Thông điệp chính:** Dữ liệu đến ngày 28 đủ để phân biệt nhóm có nguy cơ không hoàn thành ở mức trung bình. Nhưng 200 suất liên hệ mỗi module-kỳ chỉ bắt được khoảng một phần tư số sinh viên cần hỗ trợ, nên cần nâng năng lực hoặc chấp nhận gắn cờ rộng hơn.

## Bối cảnh

Trong 13.020 lượt đăng ký còn học đến ngày 28 (BBB và FFF, 4 kỳ), 43% sẽ không hoàn thành (Fail hoặc Withdrawn). Nhà trường muốn biết ai cần hỗ trợ trước khi quá muộn, và liên hệ được bao nhiêu người.

## Xung đột

Sinh viên không hoàn thành đã hoạt động ít hơn ngay từ tuần 1. Nhưng từng chỉ báo riêng lẻ chỉ phân biệt được yếu (AUC 0,59–0,67). Mô hình tốt nhất đạt AUC 0,67 trên kỳ mới 2014J. Để bắt 70% người không hoàn thành, phải gắn cờ gần một nửa sinh viên.

## Phát hiện

1. **Tương tác có khác biệt từ tuần đầu.** Tổng lượt nhấp 4 tuần (trung vị): Pass 251, Withdrawn 158, Fail 111.
2. **Không nộp TMA1 đến ngày 28 là dấu hiệu rõ nhất.** 97% sinh viên hoàn thành đã nộp, so với 76% sinh viên không hoàn thành. Hoạt động thấp đi kèm, với khác biệt có ý nghĩa từ tuần 1.
3. **Dự báo đạt mức trung bình.** Với ngưỡng đạt 70% recall trên validation, kỳ test chỉ đạt 64% recall và phải gắn cờ 47% sinh viên.
4. **Năng lực hạn chế.** Danh sách 200 mỗi module-kỳ (1.600 người) trúng 1.383 người không hoàn thành (86%), nhưng chỉ bao phủ 25% tổng số người cần hỗ trợ.

## Hành động đề xuất

- Ưu tiên 200 sinh viên có điểm rủi ro cao nhất trong mỗi module-kỳ. Cố vấn bắt đầu bằng việc hỗ trợ nộp TMA1 và kiểm tra nhịp học.
- Nếu muốn bắt 70% người không hoàn thành, cần gắn cờ khoảng 50–57% mỗi cohort. Phương án này cần đánh giá lại năng lực liên hệ.
- Trước khi triển khai, xác nhận `tma1_score` chỉ chứa điểm nộp đến ngày 28 và theo dõi hiệu năng ở kỳ mới.
