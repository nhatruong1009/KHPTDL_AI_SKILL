# Trả lời: doanh thu thuần 2011 vs 2010

**Kết quả:** So cùng kỳ 01/01–09/12 (vì dữ liệu 2011 dừng ở 09/12), doanh thu thuần 2011 = £9,03 triệu so với £8,81 triệu của 2010: **+£223 nghìn (+2,5%)**. So cả năm lịch sẽ ra −1,5%, nhưng đó là so sánh không công bằng.

**Mới hay cũ:** Khách cũ giữ lại −£430 nghìn; khách cũ rời bỏ −£1.067 nghìn; khách mới 2011 +£1.430 nghìn; khách quay lại +£37 nghìn; dòng không có Customer ID +£253 nghìn. Chỉ 63% khách 2010 còn mua năm 2011. Tăng trưởng thuần đến từ khách mới bù lại phần khách cũ mất.

**Thị trường:** Anh +£31 nghìn (phẳng). Kéo tăng: Úc +£106 nghìn (gần như toàn bộ từ 1 khách), Pháp +£62 nghìn. Kéo giảm: Ireland −£79 nghìn, Đan Mạch −£28 nghìn, Thụy Điển −£16 nghìn.

**Phương pháp:** gộp 2 sheet, bỏ phần trùng 01–09/12/2010; net revenue = Quantity × Price (gồm hàng trả lại), loại phí ship/điều chỉnh và hóa đơn "A". Mã chạy: `analysis.py`; kết quả: các file CSV và PNG cùng thư mục (file `_*.pkl` là cache đọc từ xlsx).

**Lưu ý:** 20–25% dòng thiếu Customer ID; "khách mới" chỉ dựa trên lịch sử từ 12/2009; dữ liệu quan sát nên không kết luận nguyên nhân; kết quả nhạy với định nghĩa doanh thu (+1,5% nếu tính cả phí ship/điều chỉnh).

Chi tiết và khuyến nghị: xem `story.md`.
