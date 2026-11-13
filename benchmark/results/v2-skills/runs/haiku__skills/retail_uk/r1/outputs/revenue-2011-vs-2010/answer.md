# Doanh thu thuần 2011 so với 2010: khách mới, khách cũ và thị trường

## Trả lời ngắn

- **So sánh công bằng (1/1–8/12, cùng kỳ hai năm):** doanh thu bán hàng thuần tăng **+£359k (+4,0%)**, từ £8,86 triệu lên £9,22 triệu. Nếu tính cả các dòng điều chỉnh nội bộ (bù nợ xấu, phí, "Manual") thì tăng **+£176k (+2,0%)**. Kết luận chung: tăng nhẹ, khoảng 2–4%.
- **Phần thay đổi đến từ đâu:** từ khách có mã, khách mới 2011 bù gần hết khách cũ rời đi. Khách mới cộng **+£1,45 triệu**, trong khi khách cũ giảm ròng **−£1,41 triệu** (khách mất −£1,06 triệu, khách còn lại chi tiêu ít hơn −£0,39 triệu, khách quay lại +£0,05 triệu). Phần khách có mã chỉ tăng **+£37k (+0,5%)**. Phần còn lại, **+£322k**, đến từ đơn không có mã khách hàng, nên không phân loại được là khách mới hay cũ.
- **Thị trường:** Anh (+£142k, +1,9%), Úc (+£106k), Pháp (+£68k) kéo tăng nhiều nhất. Ireland (EIRE, −£78k, −23%), Đan Mạch (−£27k, −61%) và Thụy Điển (−£17k, −33%) giảm nhiều nhất. Mức tăng của Úc gần như hoàn toàn do 3 khách hàng; mức giảm của EIRE cũng do 3 khách hàng.
- **Gợi ý cho quyết định:** khách cũ đang rời đi với tỷ lệ 36,6% mỗi năm (1.533/4.184 khách mua 2010 không mua lại trong 2011). Hiện tại tăng trưởng phụ thuộc vào việc liên tục thu hút khách mới để bù. Vì vậy nên **ưu tiên giữ chân khách cũ** và duy trì mức thu hút khách mới hiện tại, không cắt giảm.

## Bằng chứng

### 1. So sánh công bằng (bảng `headline_revenue.csv`, `sensitivity.csv`)

| Phương án | 2010 (£) | 2011 (£) | Thay đổi | % |
|---|---:|---:|---:|---:|
| **Headline:** bán hàng, bỏ điều chỉnh nội bộ | 8.864.344 | 9.223.328 | +358.985 | +4,0% |
| Gồm cả điều chỉnh nội bộ | 8.793.185 | 8.969.296 | +176.111 | +2,0% |
| Chỉ khách có mã (bỏ điều chỉnh) | 7.740.573 | 7.777.132 | +36.559 | +0,5% |

Cùng kỳ là 1/1 đến 8/12 cho cả hai năm. Dữ liệu 2011 kết thúc giữa ngày 9/12/2011, nên không dùng cả năm 2010 làm mốc. So sánh sai (cả năm 2010 £9,29 triệu với 2011 đến 9/12 £9,22 triệu) cho ra −0,7%, và làm mất tăng trưởng thật.

### 2. Phân rã khách mới / cũ (`bridge_new_vs_old.csv`, `customer_stats.csv`, `bridge_waterfall.png`)

| Thành phần | Số khách | Doanh thu (£) |
|---|---:|---:|
| Doanh thu 2010, khách có mã | 4.184 | 7.740.573 |
| Khách mất (mua 2010, không mua 2011) | −1.533 | −1.064.368 |
| Khách giữ lại: thay đổi chi tiêu | 2.651 | −394.832 |
| Khách cũ quay lại (không mua 2010) | 49 | +45.784 |
| Khách mới 2011 (lần đầu mua 2011) | 1.521 | +1.449.975 |
| **Doanh thu 2011, khách có mã** | 4.221 | **7.777.132** |
| Đơn không có mã KH (thay đổi) | — | +322.426 |

- Chi tiêu trung bình khách mới 2011: £953. Khách giữ lại: £2.518 (2010) → £2.369 (2011), giảm 5,9%.
- Khách cũ ròng: −1.064 − 395 + 46 = **−£1.413k**, tương đương 18% doanh thu khách có mã của 2010.
- Để bù £1,41 triệu khách cũ mất đi theo chi tiêu khách mới hiện tại (£953), cần khoảng **1.480 khách mới mỗi năm**. Năm 2011 đã đạt 1.521 khách mới, tức là chỉ vừa đủ để bù phần khách cũ rời đi, không tạo thêm tăng trưởng đáng kể.

### 3. Thị trường (`country_change.csv`, `market_concentration.csv`, `country_movers.png`)

| Thị trường | 2010 (£) | 2011 (£) | Thay đổi (£) | Ghi chú |
|---|---:|---:|---:|---|
| United Kingdom | 7.595.942 | 7.737.812 | +141.870 | Khách có mã −188k, đơn không mã +330k |
| Australia | 29.927 | 136.072 | +106.146 | 3 khách hàng chiếm +108k; phần còn lại −2k |
| France | 119.252 | 187.503 | +68.251 | 3 khách chiếm +21k; phần còn lại +48k (rộng) |
| Netherlands | 248.757 | 275.983 | +27.226 | |
| Spain | 28.421 | 55.755 | +27.334 | |
| Denmark | 44.307 | 17.487 | −26.820 | −61% |
| Sweden | 50.978 | 33.909 | −17.069 | −33% |
| EIRE | 333.433 | 255.091 | −78.343 | Khách có mã −68k; 3 khách chiếm toàn bộ |

Thị trường lớn nhất ngoài Anh năm 2010 là EIRE (£333k), tiếp theo là Hà Lan (£249k). Mức giảm 23% của EIRE đáng chú ý vì đây là thị trường lớn thứ hai sau Anh.

## Phương pháp

- **Dữ liệu:** `data/online_retail_II.xlsx`, hai sheet 2009–2010 và 2010–2011. Hai sheet trùng nhau 1–9/12/2010, nên lấy sheet 1 cho trước 1/12/2010 và sheet 2 cho phần còn lại. Đã bỏ 11.812 dòng trùng hoàn toàn.
- **Doanh thu thuần:** `Quantity × Price`, giữ dòng hoàn trả (số lượng âm) để có doanh thu thuần. Bỏ các dòng giá ≤ 0 (điều chỉnh, miễn phí).
- **Điều chỉnh nội bộ** (mã M, B, ADJUST, AMAZONFEE, BANK CHARGES, TEST, CRUK) bị loại khỏi headline vì không phải giao dịch khách hàng; kết quả gồm cả chúng được báo cáo như độ nhạy.
- **Khách mới:** lần mua đầu tiên trong dữ liệu rơi vào 2011. **Khách cũ:** đã mua trước 2011. **Khách mất:** có doanh thu cùng kỳ 2010 nhưng không có trong cùng kỳ 2011.
- Mã script: `analysis.py`. Chạy lại mất khoảng 2 phút (chủ yếu đọc Excel).

## Hạn chế và giả định

1. **Định nghĩa "mất khách" bị đẩy lên cao:** dữ liệu 2011 kết thúc 9/12/2011, nên khách mua trong 9–31/12/2011 bị tính là mất. Tỷ lệ 36,6% có thể cao hơn thực tế; con số chính xác cần dữ liệu đến hết năm 2011.
2. **Đơn không có mã khách:** khoảng 13–16% doanh thu bán hàng không gắn với khách, và đóng góp +£322k vào thay đổi (lớn hơn phần khách có mã). Kết luận "khách mới bù khách cũ" dựa trên phần có mã; phần không mã có thể là khách mới hoặc khách cũ mua vãng lai.
3. **Doanh thu bị ảnh hưởng bởi vài đơn lớn:** Úc và EIRE tập trung vào một số khách; không có dữ liệu chi phí nên không so sánh được hiệu quả đầu tư giữ chân và thu hút khách mới.
4. **Đây là số liệu quan sát:** khách cũ rời đi không có nghĩa là do sản phẩm hay dịch vụ. Cần thử nghiệm (ví dụ nhóm đối chứng) để xác nhận hiệu quả chương trình giữ chân.
5. Tỷ lệ mất khách ~1 điểm phần trăm ≈ 42 khách ≈ £29k doanh thu 2010 (giả định khách giữ lại chi tiêu như khách đã mất, £694 mỗi người). Đây là ước tính minh họa, không phải dự báo.

## Đề xuất

- **Ưu tiên giữ chân khách cũ:** nhắm vào nhóm vừa mua trong 2010 nhưng không quay lại trong 2011; thử nghiệm với nhóm đối chứng và đo tỷ lệ quay lại.
- **Giữ mức thu hút khách mới hiện tại** (≈1.500 khách/năm), vì nếu ngừng, doanh thu sẽ giảm rõ rệt.
- **Theo dõi EIRE và Đan Mạch** để hiểu nguyên nhân giảm; kiểm tra thêm Úc có phụ thuộc vào 3 khách.
- **Bổ sung dữ liệu:** mã khách cho mọi đơn, dữ liệu chi phí thu hút và giữ chân, dữ liệu đến hết năm 2011.
