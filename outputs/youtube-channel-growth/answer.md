# Kế hoạch kênh 0 -> 1 triệu sub: dữ liệu youtube_trending trả lời được đến đâu

**Kết luận về độ phù hợp: chỉ phù hợp một phần.** Dữ liệu là các video đã lọt vào mục thịnh hành ở 10 nước (2017-2018). Nó **không có số subscriber, không có tốc độ tăng trưởng kênh theo thời gian, và không có các kênh thất bại**. Vì vậy không thể lập kế hoạch có số liệu để đạt 1 triệu sub, hay nói điều gì khiến kênh tăng sub. Dưới đây chỉ là mô tả những video *đã thịnh hành*.

## Điều dữ liệu cho thấy
(207,148 video khác nhau, 37,917 kênh; đếm theo từng nước)
1. **Thịnh hành thường là của các kênh quen thuộc, nhưng không đóng cửa với kênh nhỏ.** 51-71% kênh trong danh sách chỉ có đúng 1 video thịnh hành ở hầu hết nước (Ấn Độ 24%, ngoại lệ). Nhưng 69-76% video ở CA, DE, FR, MX, RU, KR đến từ kênh có >= 5 video thịnh hành, và Ấn Độ là 91%. Tức nhóm nhỏ kênh lặp lại chiếm phần lớn.
2. **Thể loại:** Entertainment nhiều video nhất (60,572), People & Blogs (35,379), News & Politics (23,353). Lượt xem trung vị cao nhất ở Comedy (~294K), Music (~275K), Sports (~193K) và thấp nhất ở Education (~30K). Music và Gaming có số video trên mỗi kênh thấp nhất (2.6 và 2.5): nhiều kênh khác nhau cùng lọt vào. Xem `category_summary.csv`.
3. **Giờ đăng (UTC):** tập trung 15-17h (khoảng 21.5% video đăng trong 3 giờ này); đăng nhiều nhất vào thứ Sáu (15.8%), ít nhất thứ Bảy (13.1%).

## Điều dữ liệu KHÔNG cho phép kết luận
- **Thiên lệch người sống sót:** chỉ thấy video đã thịnh hành, không thấy hàng triệu video không lọt vào. Không thể suy ra "đăng giờ này / thể loại này thì dễ thịnh hành".
- Video có nhiều thẻ (tags) hơn có lượt xem trung vị cao hơn (0 tag: 35K; 21+ tag: 99K), và tiêu đề <= 30 ký tự có lượt xem trung vị cao hơn (177K so với ~91-107K). Nhưng đây chỉ là mối liên hệ; các kênh lớn có xu hướng làm khác nhau, chưa tách được ảnh hưởng.
- Không có dữ liệu về số sub, chi phí sản xuất, tần suất đăng, hay thị trường Việt Nam (không có trong 10 nước).

## Nên làm gì tiếp
Để lập kế hoạch thật sự có cơ sở, cần dữ liệu có **số sub theo thời gian của nhiều kênh (kể cả kênh không thành công)**, hoặc dữ liệu YouTube Analytics của chính kênh bạn. Nếu bạn muốn, mình có thể phân tích hẹp hơn với dữ liệu này: ví dụ chọn một nước/thể loại và xem kênh nào lọt thịnh hành lặp lại, hoặc video của nó có đặc điểm gì.

## Cách làm
- Mỗi video lấy một lần (dòng có lượt xem cao nhất theo nước). Code: [analysis.py](analysis.py), log `run_log.txt`; bảng `category_summary.csv`, `publish_dow.csv`; biểu đồ [category_concentration.png](category_concentration.png).
