# Câu chuyện: phát hiện sớm sinh viên cần hỗ trợ đến ngày 28

**Thông điệp chính:** Dấu hiệu tương tác đã xuất hiện từ tuần đầu và đủ để xếp hạng rủi ro khá tốt. Nhưng với 200 liên hệ mỗi module-kỳ, nhà trường chỉ tiếp cận được một phần nhỏ người cần hỗ trợ. Mục tiêu bắt 70% là không khả thi nếu giữ giới hạn này.

## Bối cảnh

Tại mốc cuối ngày 28, 13.020 sinh viên vẫn đang theo học ở BBB và FFF qua bốn kỳ. Khoảng 43% trong số họ sau đó không hoàn thành (Fail hoặc Withdrawn). Nhà trường muốn biết ai cần hỗ trợ trước, với nguồn lực chỉ đủ 200 liên hệ mỗi module-kỳ.

## Diễn biến

**1. Khác biệt đã thấy ngay tuần 1.** Sinh viên Pass có trung vị 53 lượt truy cập trong tuần đầu. Withdrawn có 33 và Fail có 20. Khác biệt này giữ nguyên đến tuần 4 và đến ngày 28. Hình: `q1_tuong_tac_theo_tuan.png`.

**2. Không cần chờ đến cuối kỳ để thấy tín hiệu.** Trong 34 chỉ báo, 28 chỉ báo khác biệt có ý nghĩa giữa nhóm hoàn thành và không hoàn thành. Nổi bật nhất là việc nộp TMA1 đúng hạn (93,6% so với 66,5%). Hình: `q2_hieu_do_theo_tuan.png`.

**3. Dự báo được, nhưng chưa đủ để đạt 70%.** Mô hình hồi quy logistic dùng dữ liệu đến ngày 28 đạt AUC 0,69 trên kỳ 2014J. Ngưỡng chọn trên kỳ validation bắt được 63% sinh viên không hoàn thành trên test. Đạt 70% đòi hỏi liên hệ khoảng một nửa số sinh viên, tức khoảng 920–960 người mỗi module-kỳ. Hình: `q3_duong_bat_duoc_tren_test.png`.

**4. Giới hạn 200 là điểm nghẽn.** Danh sách 200 người mỗi module-kỳ, xếp theo điểm rủi ro, trúng 71% trên 2014J (284/400). Đây là số người không hoàn thành được tìm thấy. Tuy nhiên, con số này chỉ chiếm 21% tổng số sinh viên không hoàn thành. Ngay cả xếp hạng hoàn hảo cũng chỉ đạt khoảng 28%. Hình: `q4_trung_theo_module_ky.png`.

**5. Lý do rủi ro, bằng lời thường.** Phần lớn sinh viên trong danh sách có lượt truy cập thấp đến ngày 28 (90%), hoặc chưa có điểm TMA1 (57%). Mỗi sinh viên có 2–3 câu giải thích để cố vấn đọc trước khi trò chuyện.

## Hành động đề xuất

- Dùng danh sách xếp hạng theo mô hình, kèm luật đơn giản "ít lượt truy cập đến ngày 28" làm đối chiếu.
- Với nguồn lực hiện có, coi đây là công cụ ưu tiên, không phải bộ lọc đầy đủ. Kỳ vọng bắt khoảng 20–25% người không hoàn thành.
- Nếu cần đạt 70%, phải tăng nhân lực lên khoảng 50% số sinh viên mỗi module-kỳ, hoặc chấp nhận mục tiêu thấp hơn.
- Theo dõi hiệu quả mỗi kỳ, vì AUC đã giảm ở kỳ 2014J.

## Lưu ý khi trình bày

Đây là mối liên hệ trong dữ liệu, không chứng minh nguyên nhân. Liên hệ có thể giúp hay không, cần đo bằng thử nghiệm có đối chứng. Nhóm Withdrawn trong dữ liệu chỉ gồm người rút sau ngày 28.
