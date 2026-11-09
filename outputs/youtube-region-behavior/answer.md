# Hành vi người dùng theo khu vực - youtube_trending

**Câu hỏi:** Hành vi của người dùng theo khu vực.
**Cách hiểu:** dữ liệu không có từng người dùng, chỉ có các video thịnh hành (trending) ở 10 nước (375,942 dòng, 207,148 video khác nhau, 2017-2018). "Hành vi" được hiểu là **cách khán giả mỗi nước phản ứng với video thịnh hành**: thích, không thích, bình luận, loại nội dung nổi lên.

## Trả lời
1. **Nước dễ tương tác nhất: Nga và Mexico.** Thích/100 lượt xem: RU 4.88, MX 4.47 (cao nhất), FR 3.54; thấp nhất GB 2.08 và IN 2.13. Bình luận/1,000 lượt xem: RU 7.08, MX 5.69, thấp nhất GB 2.11 và IN 2.21. Nga cũng bấm không thích nhiều nhất (0.58/100 lượt xem, gấp 3-5 lần các nước khác).
2. **Nội dung nổi lên khác nhau rõ rệt:**
   - Ấn Độ: Entertainment 46.3%, News & Politics 15.4%.
   - Hàn Quốc: News & Politics 23.5% (cao nhất), People & Blogs 21.2%.
   - Nga: People & Blogs 25.9% là loại số 1; Entertainment chỉ 13.9%.
   - Anh: Music 26.8% (cao nhất, gấp 2-6 lần các nước khác 4.1-12.6%).
   - Các nước còn lại (CA, DE, FR, JP, MX, US): Entertainment dẫn đầu (25-37%).
3. **Nhật tắt bình luận/đánh giá nhiều nhất:** 6.5% video tắt bình luận và 6.95% tắt đánh giá, so với 0.4-2.6% ở phần lớn nước khác (Hàn Quốc tắt đánh giá 4.6%, Ấn Độ tắt bình luận 3.6%).
4. **Quy mô video thịnh hành:** lượt xem trung vị cao nhất ở GB (598K), US (518K), CA (288K); thấp nhất ở JP (49K), MX (47K), FR (54K). Giờ đăng video (UTC) phổ biến nhất: 14-17h ở hầu hết nước; JP 10h, KR 9h, MX 2h.

## Biểu đồ
- [region_engagement.png](region_engagement.png) - thích, bình luận, lượt xem trung vị, độ trễ theo nước
- [category_mix.png](category_mix.png) - cơ cấu thể loại theo nước

## Cách làm
- Gộp 10 file `*videos.csv`, mỗi video lấy một lần (dòng có lượt xem cao nhất). Tỷ lệ = tổng thích (hoặc bình luận) / tổng lượt xem, bỏ video tắt đánh giá hoặc bình luận tương ứng. Tên thể loại lấy từ `*_category_id.json`.
- Code: [analysis.py](analysis.py), log `run_log.txt`; bảng `region_metrics.csv`, `category_mix.csv`.

## Lưu ý
- **Đây là hành vi trên video đã thịnh hành, không phải của mọi người dùng**, và không biết ai xem (độ tuổi, thiết bị). Khác biệt giữa nước có thể do ngôn ngữ, văn hóa, hoặc cách YouTube chọn video thịnh hành mỗi nước, không chắc là "tính cách khán giả".
- **US và GB bất thường**: chỉ 6,351 và 3,272 video khác nhau (so với 12-34K ở nước khác) nhưng số dòng tương đương; video ở đây nằm trong danh sách thịnh hành lâu (US trung vị 6 ngày, GB 10 ngày; còn lại 1-2 ngày) và độ trễ từ đăng đến thịnh hành dài (US 7 ngày, GB 13 ngày; còn lại 1-2 ngày). Nên số liệu của US/GB (và lượt xem trung vị cao) không so sánh trực tiếp được với phần còn lại; cần kiểm tra cách thu thập dữ liệu.
- Tỷ lệ thích/bình luận bị ảnh hưởng bởi thể loại (ví dụ nhạc, tin tức), nên chưa tách được "thói quen khán giả" khỏi "loại nội dung".
- Số liệu dừng ở 2017-2018, chưa kiểm tra tính mùa vụ theo nước.
