# Tăng trưởng doanh thu - sales_data_sample.csv

**Câu hỏi:** Vẽ biểu đồ tăng trưởng doanh thu.

## Trả lời
Doanh thu tăng đều qua các năm: **2003: 3.52M USD -> 2004: 4.72M USD (+34.3%)**. Cùng kỳ tháng 1-5: **0.84M (2003) -> 1.31M (2004, +56.5%) -> 1.79M (2005, +36.4%)**, tức vẫn tăng nhưng chậm hơn năm trước (và chỉ +4.4% nếu chỉ tính đơn đã giao - xem Lưu ý). Doanh thu có tính mùa vụ rất rõ: **tháng 11 là đỉnh** (1,030K năm 2003; 1,089K năm 2004, +5.7%), tháng 10-11 chiếm phần lớn doanh thu cuối năm.

## Biểu đồ
- [monthly_revenue.png](monthly_revenue.png) - doanh thu theo tháng 01/2003 - 05/2005
- [yearly_growth.png](yearly_growth.png) - cả năm và so sánh cùng kỳ tháng 1-5

| Năm | Doanh thu cả năm | Số tháng có dữ liệu | Tháng 1-5 | Tăng trưởng tháng 1-5 |
|---|---|---|---|---|
| 2003 | 3,516,980 | 12 | 839,377 | - |
| 2004 | 4,724,163 (+34.3%) | 12 | 1,313,317 | +56.5% |
| 2005 | 1,791,487 | 5 | 1,791,487 | +36.4% |

## Cách làm
- Doanh thu = tổng cột `SALES` (2,823 dòng đơn hàng, không thiếu giá trị), gộp theo tháng của `ORDERDATE` (01/2003 - 05/2005, đủ 29 tháng, không tháng nào trống).
- `ORDERDATE` khớp hoàn toàn với `YEAR_ID` / `MONTH_ID`; tổng theo tháng = tổng toàn bộ (10,032,629 USD).
- Tăng trưởng năm 2005 chỉ so sánh cùng kỳ tháng 1-5 vì dữ liệu dừng ở 31/05/2005.
- Code: [analysis.py](analysis.py); bảng số: `monthly_revenue.csv`, `yearly_revenue.csv`.

## Lưu ý
- Doanh thu tính trên **mọi trạng thái đơn** (Shipped 92.6%, Cancelled 1.94%, On Hold 1.78%, In Process 1.44%, ...). **Nếu chỉ tính đơn Shipped**, 2004 vẫn tăng +31.6% so với 2003 và cùng kỳ tháng 1-5/2004 tăng +51.1%, nhưng **tháng 1-5/2005 chỉ tăng +4.4%** (1.27M -> 1.32M). Phần lớn đơn chưa giao / bị hủy rơi vào 2005, nên mức +36.4% của 2005 phụ thuộc vào việc các đơn đó có thành doanh thu thật hay không.
- Tăng trưởng theo tháng (MoM) dao động mạnh do mùa vụ, nên so sánh cùng kỳ (YoY) đáng tin hơn.
- Chỉ có 2.4 năm dữ liệu, chưa đủ để kết luận xu hướng dài hạn.
