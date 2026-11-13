# Doanh thu thuần 2011 so với 2010: khách mới hay khách cũ, thị trường nào?

## Trả lời ngắn
- **So sánh công bằng (1/1–8/12 mỗi năm): doanh thu thuần 2011 = £9,002,503 so với £8,759,825 của 2010, tăng +£242,678 (+2.8%).** Khoảng tin cậy bootstrap 95% theo khách hàng: −5.0% đến +10.5% → thực chất là **đi ngang**, không đủ bằng chứng để nói tăng.
- So sánh "ngây thơ" cả năm (2011 chỉ có dữ liệu đến 9/12 so với cả năm 2010) cho −1.5%, và nếu quên loại phần trùng giữa hai sheet thì ra −1.2%: cả hai đều sai dấu.
- **Mới hay cũ?** Khách mới 2011 (lần mua đầu tiên trong dữ liệu nằm ở 2011) đem lại **+£1.43 triệu** (1,533 khách), nhưng khách cũ làm mất **−£1.47 triệu**: 1,532 khách 2010 không mua lại (−£1.06 triệu) và 2,650 khách giữ chân chi ít hơn (−£0.41 triệu; trung bình £2,515 → £2,361/khách, −6%). Khách cũ quay lại +£0.04 triệu; doanh thu không có Customer ID +£0.25 triệu. Cộng lại khách có mã gần như bằng 0 (−£9k); **toàn bộ mức tăng +£243k đến từ nhóm không có Customer ID** (xem hạn chế).
- **Thị trường:** ngoài UK +£197k (+16%), UK +£46k (+0.6%). Kéo tăng nhiều nhất: **Australia +£106k**, **Pháp +£63k**, UK +£46k, Hà Lan +£27k, Tây Ban Nha +£24k. Kéo giảm nhiều nhất: **EIRE (Ireland) −£78k**, Đan Mạch −£27k, Thụy Điển −£16k, Hy Lạp −£9k.

## Bằng chứng
| Nhóm | Khách | DT 2010 | DT 2011 | Thay đổi |
|---|---|---|---|---|
| Cũ – giữ chân (mua cả hai năm) | 2,650 | 6.67 tr | 6.26 tr | −0.41 tr |
| Cũ – rời bỏ (có 2010, không có 2011) | 1,532 | 1.06 tr | 0 | −1.06 tr |
| Cũ – quay lại | 48 | 0 | 0.04 tr | +0.04 tr |
| Mới 2011 | 1,533 | 0 | 1.43 tr | +1.43 tr |
| Không có Customer ID | n/a | 1.03 tr | 1.28 tr | +0.25 tr |
| **Tổng** | | **8.76 tr** | **9.00 tr** | **+0.24 tr** |

- Tỷ lệ giữ chân: 2,650/4,182 = **63.4%** khách hoạt động 2010 còn mua trong cùng kỳ 2011.
- Khách rời bỏ có giá trị thấp (£695/khách năm 2010) so với khách giữ chân (£2,515); khách mới £931/khách (mới mua một phần năm).
- Hai thị trường kéo tăng/giảm lớn rất tập trung vào ít khách: Australia – một khách chiếm 91% doanh thu 2011 (65% năm 2010); EIRE chỉ 3 khách, Đan Mạch 9 khách → biến động quốc gia này dễ do một vài khách lớn, không phải xu hướng thị trường.
- Theo tháng: 2011 thấp hơn 2010 ở T1–T4, cao hơn ở T5–T9, T10–T11 gần bằng nhau (chart3).

Biểu đồ: `chart1_new_vs_existing.png`, `chart2_country.png`, `chart3_monthly.png`. Bảng: `segment_new_vs_existing.csv`, `country_contribution.csv`, `uk_vs_nonuk.csv`, `retention_summary.csv`, `sensitivity.csv`, `headline_numbers.csv`.

## Phương pháp
- Dữ liệu: 2 sheet (2009-12-01→2010-12-09 và 2010-12-01→2011-12-09) **trùng nhau 22,523 dòng (£377k) từ 1–9/12/2010**; giữ một bản.
- Doanh thu thuần = Quantity × Price, đã gồm hoá đơn hoàn/huỷ (Quantity âm). Loại các dòng không phải hàng hoá (POST, DOT, AMAZONFEE, phí ngân hàng, điều chỉnh nợ xấu, M, B, D, ... tổng −£70k).
- Cửa sổ công bằng: **1/1 đến hết 8/12** của mỗi năm (ngày 9/12/2011 mới có nửa ngày).
- Phân loại khách theo Customer ID: "mới" = lần mua đầu tiên trong dữ liệu (từ 12/2009) nằm trong 2011; "giữ chân" = có doanh thu ở cả hai cửa sổ; "rời bỏ" = chỉ có ở 2010; "quay lại" = có ở 2011, đã mua trước 2011 nhưng không có ở cửa sổ 2010.
- Quốc gia lấy theo dòng giao dịch; thay đổi mỗi nước = DT 2011 − DT 2010.

## Kiểm tra độ nhạy (% thay đổi cùng kỳ)
| Biến thể | Kết quả |
|---|---|
| Chuẩn (báo cáo) | +2.8% |
| Giữ cả dòng phí/điều chỉnh | +3.2% |
| Bỏ dòng trùng hoàn toàn | +2.9% |
| Doanh thu gộp (không trừ hàng trả) | +3.4% |
| **Chỉ khách có Customer ID** | **−0.1%** |
| Sai: cộng trùng 1–9/12/2010 | −1.2% |

Kết luận ổn định "đi ngang, ~0 đến +3%"; riêng biến thể chỉ khách có mã cho thấy ~0%, nên headline là **đi ngang (+2.8%, không có ý nghĩa thống kê)**, không phải "tăng trưởng".

## Hạn chế
- **14% doanh thu không có Customer ID** (đa số có thể là khách lẻ/khách vãng lai) → không phân loại mới/cũ được; nhóm này chính là phần tạo ra mức tăng ròng +£252k.
- Dữ liệu bắt đầu 12/2009 nên "khách mới" có thể gồm khách đã mua trước đó (cũ thật nhưng không thấy); "rời bỏ" có thể là khách chỉ ngừng mua tạm thời hoặc đổi mã; khách mới 2011 mới có phần năm để chi tiêu.
- Khoảng tin cậy rộng (−5% đến +10.5%) vì doanh thu tập trung ở ít khách bán buôn lớn.
- Dữ liệu quan sát: mô tả liên hệ, không chứng minh nguyên nhân.
- Không có dữ liệu chi phí/lợi nhuận nên không so sánh chi phí giữ chân với chi phí tìm khách mới.
