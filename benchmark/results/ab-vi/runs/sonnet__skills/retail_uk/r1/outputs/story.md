# Giữ chân khách cũ hay tìm khách mới? – Data story cho CEO

**Thông điệp chính:** Doanh thu thuần 2011 gần như đi ngang (**+2,5%**, +£223 nghìn) khi so công bằng. Con số này che giấu một "chiếc thùng thủng": khách cũ làm mất ~£1,5 triệu, khách mới chỉ bù lại ~£1,4 triệu. **Ưu tiên giữ chân khách cũ**, đặc biệt nhóm khách B2B lớn ở Anh và Ireland.

## 1. So sánh công bằng: +2,5%, không phải −1,5%
Dữ liệu 2011 chỉ kéo dài đến 09/12/2011. So cả năm lịch sẽ thấy −1,5% (£9,03 triệu vs £9,17 triệu) – một kết luận sai vì 2011 thiếu ~3 tuần mùa cao điểm. So cùng kỳ **01/01–09/12**:

| | 2010 | 2011 | Thay đổi |
|---|---|---|---|
| Doanh thu thuần (hàng hoá, đã trừ hàng trả lại) | £8,81 triệu | £9,03 triệu | **+£223 nghìn (+2,5%)** |

Tăng trưởng không đều: Q1–T4/2011 giảm (−4% đến −24%), từ tháng 5 phục hồi (+6% đến +20%) – xem `theo_thang.png`.

## 2. Tăng trưởng đến từ đâu: khách mới bù cho khách cũ rời bỏ
![](cau_noi_khach_hang.png)

| Nhóm | Số khách | Thay đổi doanh thu |
|---|---|---|
| Khách cũ giữ lại (mua cả 2010 & 2011) | 2.653 | **−£430 nghìn** (−6%) |
| Khách cũ rời bỏ (chỉ mua 2010) | 1.533 | **−£1.067 nghìn** |
| Khách mới 2011 | 1.532 | **+£1.430 nghìn** |
| Khách cũ quay lại | 47 | +£37 nghìn |
| Không có Customer ID | – | +£253 nghìn |

- Chỉ **63%** khách có mặt năm 2010 còn mua năm 2011; nhóm đó mua ít đi (£2.525 → £2.363/khách).
- Khách cũ trừ đi tổng cộng **~£1,46 triệu**; khách mới cộng **£1,43 triệu**. Tức là công ty phải "chạy" mua khách mới chỉ để đứng yên.
- Nhóm khách đã mua nhiều nhất tăng/giảm trái chiều (khách 14646 +£40 nghìn, 18102 −£74 nghìn, 12415 +£104 nghìn) – doanh thu phụ thuộc vào một số ít khách lớn.

## 3. Thị trường
![](thi_truong.png)

- **Anh (89% doanh thu)** gần như phẳng: +£31 nghìn (+0,4%). Bên trong là cùng câu chuyện: khách cũ giữ lại −£546 nghìn, rời bỏ −£938 nghìn, khách mới +£1.237 nghìn.
- **Kéo tăng:** Úc +£106 nghìn (+354%) – nhưng ~£104 nghìn chỉ từ **một khách (12415)**, nên rất mong manh; Pháp +£62 nghìn (+55%); Hà Lan, Tây Ban Nha, Nhật, Na Uy tăng nhẹ.
- **Kéo giảm:** Ireland (EIRE) −£79 nghìn (−24%), chủ yếu do khách 14156 (−£59 nghìn); Đan Mạch −£28 nghìn (−63%), Thụy Điển −£16 nghìn (−34%).
- Nhóm ngoài Anh lành mạnh hơn: khách cũ giữ lại *tăng* +£116 nghìn.

## 4. Khuyến nghị
1. **Giữ chân là đòn bẩy lớn hơn.** Cứ giảm một nửa số khách rời bỏ (~£0,5 triệu doanh thu 2010 của họ) tương đương gần 40% đóng góp của toàn bộ khách mới – và thường rẻ hơn khi tìm khách mới. *(Đây là ước tính minh hoạ, giả định khách giữ lại mua như năm trước.)*
2. Lập danh sách theo dõi **khách lớn** (top ~20): liên hệ chủ động khi đơn hàng giảm (ví dụ EIRE 14156, UK 18102).
3. Không bỏ tìm khách mới – nó đang giữ doanh thu không giảm – nhưng đừng coi tăng trưởng +2,5% là bằng chứng sức khoẻ tốt.
4. Không đầu tư mạnh vào Úc chỉ dựa trên 1 khách; Pháp là thị trường đáng thử nghiệm.

## Lưu ý
- Doanh thu thuần = số lượng × giá, gồm hàng trả lại (ghi âm); loại phí ship/điều chỉnh/phí ngân hàng và hóa đơn điều chỉnh nợ xấu (A…). Tính cả các dòng này thì kết quả là +1,5%.
- ~20–25% dòng không có Customer ID: không xếp được mới/cũ, tách riêng (+£253 nghìn).
- "Khách mới" = lần mua đầu tiên trong dữ liệu rơi vào 2011; dữ liệu chỉ bắt đầu 12/2009 nên một số "khách mới" có thể là khách rất cũ. "Rời bỏ" = không mua trong 01/01–09/12/2011 (có thể mua lại sau).
- Dữ liệu quan sát: chỉ cho thấy mối liên hệ, không chứng minh nguyên nhân khách rời bỏ.
