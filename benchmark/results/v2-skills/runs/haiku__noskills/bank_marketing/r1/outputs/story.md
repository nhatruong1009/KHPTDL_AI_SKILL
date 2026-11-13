# Chọn khách hàng để gọi: câu chuyện từ dữ liệu chiến dịch tiền gửi

Một ngân hàng Bồ Đào Nha gọi điện cho hàng chục nghìn khách hàng để mời mở tiền gửi có kỳ hạn. Chỉ khoảng 1 trên 9 cuộc gọi dẫn đến đăng ký (11,7%). Mỗi cuộc gọi tốn thời gian của tổng đài, nên câu hỏi đặt ra rất thực tế: trước khi gọi, làm sao biết ai nên gọi trước?

## Điều gì đã biết trước khi gọi

Phần lớn thông tin về khách hàng có sẵn trước cuộc gọi: tuổi, nghề nghiệp, số dư, khoản vay hiện có, và lịch sử với chiến dịch trước. Thời lượng cuộc gọi thì không. Nếu đưa vào mô hình, nó sẽ cho AUC 0,94, nhưng chỉ vì người đã nghe xong và đồng ý mới nói chuyện lâu. Đó là kết quả nhìn lại, không phải dự đoán. Vì vậy mô hình chỉ dùng những gì biết trước.

## Baseline đơn giản đã làm được gì

Nếu gọi ngẫu nhiên, 20% khách hàng đầu tiên chứa đúng 11,5% người đăng ký, tức là không có gì khác so với gọi bừa.

Quy tắc đơn giản nhất là nhìn vào kết quả của chiến dịch trước. Khách đã đăng ký lần trước có tỷ lệ 64,7%. Chỉ với quy tắc này, nhóm 20% đầu tiên đã có 21,5% đăng ký, gấp 1,8 lần ngẫu nhiên. Đây là một bước tiến rõ ràng, và nhiều đội vận hành sẽ dừng ở đây.

## Mô hình thêm được gì

Hồi quy logistic dùng toàn bộ thông tin đã biết nâng AUC lên 0,76. Gradient boosting đưa AUC lên 0,80. Nhóm 20% khách được xếp hạng cao nhất của gradient boosting chứa 62% toàn bộ người đăng ký, và khoảng 36% số người trong nhóm đó đăng ký. Với một danh sách gọi, điều này có nghĩa là cùng số cuộc gọi, số hợp đồng tăng khoảng 1,7 lần so với quy tắc poutcome.

Nhưng con số này đến từ kiểm tra chéo ngẫu nhiên. Khi kiểm tra theo thời gian, nghĩa là huấn luyện trên giai đoạn cũ và thử trên giai đoạn mới, bức tranh thay đổi. Tỷ lệ đăng ký của giai đoạn sau cao hơn hẳn (31,6% so với 6,7%), và gradient boosting chỉ hơn quy tắc poutcome khoảng 0,04 AUC. Nó còn kém hồi quy logistic một chút ở nhóm top 20%. Đây là bài học quan trọng: dữ liệu thay đổi theo thời gian, và mô hình phức tạp không tự động giữ được lợi thế.

## Yếu tố nào thật sự quan trọng

Kết quả chiến dịch trước là yếu tố mạnh nhất. Tháng liên hệ đứng thứ hai, nhưng tôi không coi đây là nguyên nhân: các tháng khác nhau thường thuộc các giai đoạn chiến dịch khác nhau. Tuổi cũng có tín hiệu, đặc biệt ở nhóm trên 60 tuổi với tỷ lệ 42%. Số dư bình quân và ngày trong tháng có tác động nhỏ. Nghề nghiệp, học vấn, và các khoản vay gần như không thêm thông tin sau khi đã biết những yếu tố trên.

Một chi tiết đáng chú ý: 82% khách hàng không có kết quả chiến dịch trước (`unknown`) và chỉ 9% trong số họ đăng ký. Nhóm này có thể là khách mới, và việc chọn ai trong nhóm này là phần khó nhất của bài toán.

## Đề xuất cho tổng đài

Nên dùng hồi quy logistic làm mô hình chính. Nó gần như ngang bằng gradient boosting, ổn định hơn qua thời gian, và có thể giải thích cho người vận hành. Gradient boosting có thể dùng nếu được huấn luyện lại định kỳ và kiểm tra trên dữ liệu gần nhất.

Điểm số nên dùng để xếp hạng, không dùng như xác suất tuyệt đối, vì mức nền đã thay đổi theo thời gian. Ưu tiên khách có kết quả chiến dịch trước là thành công và khách lớn tuổi. Với khách không rõ kênh liên lạc, cần thu thập thêm thông tin trước khi gọi, vì họ đăng ký rất thấp (4%).

Cuối cùng, cần nhớ rằng dữ liệu này đến từ 2008–2010. Trước khi triển khai, nên thử mô hình trên một đợt gọi nhỏ và so sánh với cách gọi hiện tại.
