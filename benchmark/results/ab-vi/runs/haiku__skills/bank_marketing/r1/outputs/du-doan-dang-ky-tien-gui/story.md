# Gọi đúng người trước: mô hình giúp tổng đài tập trung vào khách dễ đăng ký

**Thông điệp chính:** Với cùng số cuộc gọi, một mô hình dự đoán trước khi gọi giúp tổng đài tiếp cận gần hai phần ba khách đăng ký chỉ bằng cách gọi 20% danh sách, thay vì gọi ngẫu nhiên.

**Bối cảnh.** Tổng đài có nguồn lực gọi hạn chế, và chỉ khoảng 11% khách cuối cùng đăng ký tiền gửi có kỳ hạn. Gọi ngẫu nhiên hoặc theo cảm tính làm lãng phí phần lớn cuộc gọi.

**Xung đột.** Luật đơn giản "ưu tiên khách có kết quả chiến dịch trước là thành công" chỉ đưa được 38% khách đăng ký vào 20% danh sách đầu tiên. Nhiều khách đăng ký lại nằm ngoài nhóm đó.

**Phát hiện.** Gradient boosting, dùng thông tin có sẵn trước khi gọi (không dùng thời lượng cuộc gọi), đưa 66,5% khách đăng ký vào 20% danh sách đầu tiên, tương ứng lift 3,3 lần. Nhóm 10% đầu tiên có tỷ lệ đăng ký 52%, gấp 4,6 lần mức chung. Mô hình đạt ROC AUC 0,81 so với 0,62 của luật đơn giản và 0,50 của việc chọn ngẫu nhiên.

**Yếu tố dẫn dắt.**
1. Bối cảnh kinh tế tại thời điểm gọi (việc làm, lãi suất, chỉ số giá) là yếu tố mạnh nhất. Khi bỏ nhóm này, AUC giảm còn 0,78.
2. Loại liên lạc: khách được gọi di động đăng ký 14,7%, gọi cố định chỉ 5,2%.
3. Tháng liên lạc: tháng 3, 9, 10, 12 có tỷ lệ đăng ký 44–51%, trong khi tháng 5 chỉ 6,4%.
4. Số lần đã gọi: gọi càng nhiều lần, tỷ lệ đăng ký càng giảm, từ 13% (một lần) xuống 3,1% (trên 10 lần).

**Hành động đề xuất.**
- Xếp hạng danh sách bằng mô hình và gọi từ trên xuống, ưu tiên nhóm 10–20% đầu tiên.
- Giới hạn số lần gọi cho một khách, vì tỷ lệ đăng ký giảm rõ rệt sau vài lần.
- Nếu không dự báo được chỉ số kinh tế cho chiến dịch sắp tới, dùng phiên bản không có chúng (AUC 0,78, vẫn gọi 20% đầu tiên thu được 59% khách đăng ký).
- Theo dõi lại mô hình định kỳ, vì dữ liệu thuộc giai đoạn 2008–2010 và mối quan hệ có thể thay đổi.

**Lưu ý.** Đây là tương quan trong dữ liệu lịch sử, không phải bằng chứng nhân quả. Kết quả chưa được kiểm định theo thời gian nên có thể lạc quan hơn thực tế.
