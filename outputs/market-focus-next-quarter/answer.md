# Nên tập trung thị trường nào để tăng doanh thu quý tới? - sales_data_sample.csv

**Câu hỏi:** Tôi nên tập trung vào thị trường nào để có thể tăng trưởng doanh thu ở quý tiếp theo?

**Phạm vi đã thu hẹp:** dữ liệu dừng ở 31/05/2005, nên "quý tới" = **Q3-2005 (tháng 7-9)**. Dữ liệu không có chi phí marketing hay thử nghiệm can thiệp, nên không chứng minh được "tập trung vào X sẽ làm doanh thu tăng". Phân tích dưới đây **xếp hạng thị trường theo quy mô, đà tăng, lịch sử Q3 và độ rộng khách hàng** để làm cơ sở quyết định.

## Trả lời
1. **USA - ưu tiên số 1.**
   - Lớn nhất: 1.86M USD trong 12 tháng gần nhất (36.5% tổng), gấp ~3 lần thị trường thứ hai.
   - Đóng góp nhiều nhất vào mức tăng: +307K (+19.7%), bằng 25.5% tổng mức tăng.
   - Q3 là quý mạnh của USA: 343K (Q3-2003) -> 407K (Q3-2004), trong khi Q3 ở France/Spain/Australia chỉ 22K-86K.
   - Khách hàng rộng nhất: 28 khách, 4 khách mới; khách lớn nhất chỉ chiếm 22.6%.
2. **France - ưu tiên số 2.** 552K (+27.8%), 10 khách (7 khách còn mua trong 2005), khách lớn nhất 32.6%. Nhưng tháng 1-5/2005 gần như đi ngang (-1.1% so với cùng kỳ) và Q3 lịch sử yếu (58K-63K).
3. **Spain - chăm sóc khách hàng lớn, không phải mở rộng thị trường.** 585K (+24.4%) nhưng **88.4% doanh thu đến từ một khách (Euro Shopping Channel)**, chỉ 1 khách mua trong 2005, và Q3-2004 chỉ 22K. Tăng trưởng ở đây phụ thuộc vào một khách hàng.
4. **Australia - theo dõi.** 328K (+35.1%), tháng 1-5/2005 tăng mạnh (+192%), nhưng chỉ 10 đơn và Q3-2004 thấp hơn Q3-2003 (-37.8%).
5. **Các thị trường có % tăng rất cao (Belgium +322%, Italy +176%, Austria +176%, Sweden mới xuất hiện)** chỉ có 1-5 đơn trong 12 tháng: con số % không đủ tin cậy để đặt cược.

## Biểu đồ
- [market_priority_map.png](market_priority_map.png) - quy mô (trục ngang) và tăng trưởng (trục dọc) theo quốc gia
- [growth_contribution.png](growth_contribution.png) - mỗi thị trường đóng góp bao nhiêu USD vào mức tăng

| Thị trường | Doanh thu 12T gần nhất | Tăng so với 12T trước | % tổng mức tăng | Q3-2004 | Số đơn 12T | Số khách 12T | Khách lớn nhất |
|---|---|---|---|---|---|---|---|
| USA | 1,863,970 | +19.7% | 25.5% | 407,497 | 57 | 28 | 22.6% |
| Spain | 585,196 | +24.4% | 9.5% | 21,986 | 17 | 4 | 88.4% |
| France | 552,433 | +27.8% | 10.0% | 63,484 | 20 | 10 | 32.6% |
| Australia | 327,851 | +35.1% | 7.1% | 53,632 | 10 | 5 | 37.6% |

Toàn bộ 19 quốc gia: `market_metrics.csv`. Dòng sản phẩm tăng mạnh nhất ở USA là Classic Cars (+102K) và Vintage Cars (+93K) - xem `productline_by_market.csv`.

## Cách làm
- Doanh thu = `SALES`, **bỏ đơn Cancelled** (60 dòng, 194K USD); thị trường = `COUNTRY` (Singapore bị gán 2 territory khác nhau nên không dùng `TERRITORY`).
- So sánh 12 tháng gần nhất (06/2004-05/2005) với 12 tháng trước (06/2003-05/2004); cùng kỳ tháng 1-5; Q3-2004 với Q3-2003.
- Thị trường có < 10 đơn trong 12 tháng được đánh dấu "ít dữ liệu" (màu xám).
- Code: [analysis.py](analysis.py); log chạy: `run_log.txt`.

## Lưu ý
- **Năm 2005 có nhiều đơn chưa hoàn tất** (In Process / On Hold / Disputed). Chỉ tính đơn Shipped/Resolved thì tăng trưởng thấp hơn: USA +9.1%, Spain +10.1%, France +17.7%, Australia +11.1%. Thứ tự ưu tiên không đổi, nhưng mức tăng thực tế phụ thuộc việc các đơn đang chờ có được giao hay không.
- Đây là **xếp hạng dựa trên dữ liệu quá khứ (tương quan)**, không phải bằng chứng rằng đầu tư vào thị trường X sẽ tạo ra tăng trưởng. Dữ liệu không có chi phí, lợi nhuận hay hoạt động marketing.
- Chỉ có 2 lần Q3 trong dữ liệu (2003, 2004), nên mô hình mùa vụ Q3 theo từng thị trường còn mỏng.
- Q3 thường chỉ chiếm 19-24% doanh thu năm (Q4 là đỉnh), nên đừng kỳ vọng Q3 cao như Q4.
