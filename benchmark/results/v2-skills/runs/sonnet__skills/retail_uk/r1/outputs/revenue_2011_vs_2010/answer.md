# Doanh thu thuần 2011 so với 2010

**Trả lời:** So sánh công bằng (cùng kỳ 01/01–08/12 mỗi năm), doanh thu thuần 2011 là **£8,99 triệu so với £8,74 triệu của 2010, tăng +£254 nghìn (+2,9%)**. Nếu so thẳng "2011 (thiếu 3 tuần cuối) với cả năm 2010" sẽ ra −1,3% — đó là so sánh sai.

- **Khách mới hay cũ?** Mức tăng nhỏ này là hiệu số của hai lực lớn ngược chiều: khách mới 2011 đem về **+£1,44M** (1.536 khách), nhưng khách cũ **mất £1,06M** (1.533 khách 2010 không quay lại) và **£0,39M** (khách cũ giữ lại chi ít hơn, 2.501 → 2.344 £/khách). Cộng thêm +£0,25M từ giao dịch không có Customer ID. Tức là tăng trưởng 2011 **hoàn toàn dựa vào khách mới để bù rò rỉ khách cũ**; riêng nhóm khách có ID thì doanh thu gần như đứng yên (+0,04%).
- **Thị trường:** Tăng: **Úc +£106k** (gần hết từ 1 khách: mã 12415, £124k), **Pháp +£63k (+57%)**, UK +£58k (+0,8%), Hà Lan +£27k, Tây Ban Nha +£24k. Giảm: **Ireland (EIRE) −£78k (−23%)**, **Đan Mạch −£27k (−62%)**, Thuỵ Điển −£16k. Ngoài UK tăng +16% (£1,23M → £1,42M) trong khi UK (86% doanh thu) gần như phẳng.

**Evidence:** [chart1_bridge.png](chart1_bridge.png) · [chart2_countries.png](chart2_countries.png) · [chart3_retention.png](chart3_retention.png) · `bridge.csv`, `country_contrib.csv`, `retention_stats.csv`, `sensitivity.csv`

| Kịch bản (cùng kỳ) | 2010 | 2011 | Thay đổi |
|---|---|---|---|
| Chính (bỏ trùng, bỏ mã phi hàng hoá) | 8,74M | 8,99M | +2,9% |
| Không lọc mã phi hàng hoá/giá ≤ 0 | 8,66M | 8,95M | +3,4% |
| Chỉ hoá đơn bán (chưa trừ hoàn/hủy) | 8,96M | 9,28M | +3,5% |
| Chỉ giao dịch có Customer ID | 7,71M | 7,71M | +0,04% |
| Chỉ UK / chỉ ngoài UK | 7,51M / 1,23M | 7,57M / 1,42M | +0,8% / +16,0% |

Giữ chân: 2.658/4.191 khách 2010 có ID quay lại 2011 (**63,4%**). Khách giữ lại chi TB £2.344 (2011) so với khách mới £935 và khách rời bỏ £689.

**How:**
- File gồm 2 sheet chồng nhau 01–09/12/2010 (22.523 dòng giống hệt) → bỏ trùng; bỏ thêm các dòng trùng hoàn toàn khác (còn 1.033.036 dòng).
- Doanh thu thuần = Quantity × Price, **đã trừ hoàn/hủy** (hoá đơn bắt đầu bằng C); loại mã phi hàng hoá (POST, DOT, M, D, S, ADJUST, AMAZONFEE, B, CRUK, PADS, DCGS…) và dòng giá ≤ 0.
- Cửa sổ công bằng 01/01–08/12 vì dữ liệu 2011 dừng giữa ngày 09/12.
- Cầu nối (cộng đúng, sai số 0): khách 2010 chia theo có/không mua lại trong 2011; khách 2011 chia thành cũ (đã mua 2010), quay lại (chỉ mua 12/2009), mới (lần mua đầu trong 2011).

**Assumptions & caveats:**
- **13,7% doanh thu không có Customer ID** (khách vãng lai/không định danh): không phân loại mới/cũ được. Phần này tăng £251k (£1,03M → £1,28M, chủ yếu UK) và là lý do toàn bộ mức tăng 2,9% nằm ngoài nhóm khách định danh. Kết luận mới/cũ chỉ đúng cho khách có ID.
- "Mới" = chưa mua từ 12/2009 đến hết 2010; dữ liệu bắt đầu 12/2009 nên một số "mới" có thể là khách cũ từ trước đó (làm lệch nhẹ về phía khách mới). Không đo được "khách mới 2010" một cách công bằng nên không so sánh được độ mạnh thu hút khách mới giữa hai năm.
- "Không quay lại" tính trong cửa sổ đến 08/12/2011; một số khách mua theo mùa có thể quay lại sau.
- Thị trường nhỏ biến động mạnh do vài khách lớn (Úc: 1 khách; EIRE: 2 khách ≈ 91–94% doanh thu) — đừng đọc % ở nước nhỏ như xu hướng.
- Dữ liệu quan sát: chỉ nêu liên hệ, không kết luận nguyên nhân. Tháng 12/2010 đủ tháng, 12/2011 chỉ 8 ngày (chỉ ảnh hưởng bảng theo tháng `monthly.csv`, không ảnh hưởng so sánh chính).
- Tái chạy: `load_data.py` → `analysis.py` → `charts.py` (`raw.pkl` là cache tạo ra từ file gốc).
