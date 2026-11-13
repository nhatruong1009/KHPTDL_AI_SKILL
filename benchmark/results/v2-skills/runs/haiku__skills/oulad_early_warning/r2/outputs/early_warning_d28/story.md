# Câu chuyện: tìm đúng sinh viên trong 28 ngày đầu

**Thông điệp chính:** Dữ liệu 28 ngày đầu cho thấy ai có nguy cơ không hoàn thành, nhưng với 200 suất liên hệ mỗi module-kỳ, nhà trường chỉ bắt được khoảng một phần tư số sinh viên cần hỗ trợ.

## 1. Bối cảnh

Trong 13.020 sinh viên còn học đến cuối ngày 28 (BBB và FFF, 4 kỳ), 43% sẽ trượt hoặc rút học. Nhà trường muốn biết có thể nhận diện họ sớm đến mức nào.

## 2. Sự khác biệt xuất hiện sớm

Sinh viên đạt có trung vị lượt truy cập gấp khoảng 2,5 đến 4 lần sinh viên trượt ở mỗi tuần trong 4 tuần đầu. Sinh viên rút học nằm giữa hai nhóm. Điều này đúng ngay từ tuần 1, không phải chỉ về cuối kỳ.

## 3. Chỉ báo mạnh nhất

Số ngày có truy cập trong 28 ngày đầu là chỉ báo mạnh nhất (trung vị 12 so với 7). Tiếp theo là truy cập trang chủ khóa học, tham gia diễn đàn và việc nộp TMA1 đúng hạn. Số ngày đăng ký trước khai giảng không cho thấy khác biệt.

## 4. Dự báo được, nhưng có giới hạn

Mô hình chỉ dùng dữ liệu đến ngày 28 đạt AUC 0,72 trên kỳ kiểm tra 2014J. Nó bắt được 71,5% sinh viên không hoàn thành, đạt mục tiêu 70% về điểm ước lượng, nhưng phải gắn cờ 53% quần thể. Cận dưới khoảng tin cậy nằm dưới 70%, nên kết quả này là biên.

## 5. Điểm nghẽn: sức chứa

Với 200 suất mỗi module-kỳ, 73% (BBB) và 88% (FFF) người được liên hệ thực sự là không hoàn thành. Tuy nhiên, 400 suất chỉ bắt được 23% tổng số không hoàn thành. Mục tiêu 70% cần khoảng 950 suất mỗi module-kỳ.

## 6. Hành động đề xuất

- Ưu tiên danh sách 200 sinh viên có điểm rủi ro cao nhất, kèm 3 yếu tố chính để cố vấn mở đầu trao đổi.
- Nếu nhà trường có thể liên hệ nhiều hơn, cần tăng sức chứa. Với 200 suất, không thể đạt mục tiêu 70%.
- Theo dõi nhóm sinh viên khuyết tật, vì mô hình bắt được ít hơn ở nhóm này (66% so với 72%).

Các con số trong câu chuyện này lấy từ `answer.md` và các tệp CSV trong `outputs/early_warning_d28/`.
