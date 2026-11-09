# Kiểm tra sức khỏe kinh doanh - sales_data_sample.csv

**Câu hỏi:** Có vấn đề gì đang xảy ra trong hoạt động kinh doanh của tôi?

**Cách hiểu:** quét dữ liệu tìm **dấu hiệu cảnh báo**, so sánh giai đoạn gần nhất (tháng 1-5/2005, dữ liệu dừng 31/05/2005) với cùng kỳ năm trước. Dữ liệu chỉ cho thấy **dấu hiệu**, không cho biết nguyên nhân.

## Trả lời
**Có - 3 vấn đề đáng chú ý, và doanh thu "tăng 41%" đang che lấp chúng:**

1. **Đơn hàng bị kẹt (vấn đề cấp bách nhất).**
   - Trước 2005 chỉ 1.9% (2003) và 3.5% (2004) số đơn không ở trạng thái Shipped; năm 2005 là **23.7%**. Riêng Q2-2005: **12/23 đơn chưa giao**.
   - **4 đơn On Hold (179K USD)** - 3 đơn của khách USA trong tháng 4-5/2005, 1 đơn (Volvo Model Replicas, Sweden) bị giữ từ **19/11/2004**, đã hơn 6 tháng.
   - **3 đơn Disputed (72K USD)** trong tháng 4-5/2005 - **lần đầu tiên** có tranh chấp trong dữ liệu; một trong số đó là của **Euro Shopping Channel, khách hàng lớn nhất**.
   - (6 đơn In Process, 145K, đặt ngày 29-31/05 - nhiều khả năng chỉ là đơn vừa đặt, chưa phải vấn đề.)
   - Hệ quả: doanh thu tháng 1-5 tăng **+41.3%** nếu tính mọi đơn không hủy, nhưng chỉ **+12.1%** nếu tính đơn đã giao/giải quyết (+23.5% nếu cộng đơn đang xử lý). 225K USD đang treo ở On Hold + Disputed.

2. **Không có khách hàng mới từ Q4-2004.** Mỗi quý trước đó có 6-26 khách mới; **Q4-2004, Q1-2005, Q2-2005: 0 khách mới**. Toàn bộ tăng trưởng 2005 đến từ khách cũ mua nhiều hơn (1.2 -> 1.5 đơn/khách trong tháng 1-5; giá trị đơn trung bình gần như không đổi ~30K).

3. **Phụ thuộc ngày càng nhiều vào vài khách lớn.** So cùng kỳ tháng 1-5:
   | | Tháng 1-5/2004 | Tháng 1-5/2005 |
   |---|---|---|
   | Khách lớn nhất (Euro Shopping Channel) | 10.6% | **18.2%** |
   | Top 2 | 18.6% | **30.1%** |
   | Top 5 | 37.1% | **44.9%** |
   Khách lớn nhất này cũng đang có đơn tranh chấp.

**Dấu hiệu nhỏ hơn:** Germany, Ireland, Switzerland không có đơn nào trong tháng 1-5/2005 (cùng kỳ 2004: 37K-50K mỗi nước); Japan -43%, Singapore -72% - đều là thị trường nhỏ, ít đơn.

**Không thấy vấn đề:** cả 7 dòng sản phẩm đều tăng (+32% đến +62%); tỷ lệ khách 2004 quay lại mua trong tháng 1-5/2005 (37.3%) cao hơn năm trước (27.9%); không có đơn bị hủy nào trong 2005.

## Biểu đồ
- [order_status_by_quarter.png](order_status_by_quarter.png) - tỷ lệ trạng thái đơn hàng theo quý
- [new_vs_returning_customers.png](new_vs_returning_customers.png) - khách mới và khách cũ theo quý

## Cách làm
- 2,823 dòng / 307 đơn hàng; mỗi đơn chỉ có một trạng thái. So sánh cùng kỳ tháng 1-5 vì 2005 dừng ở 31/05.
- Khách mới = khách có đơn không hủy đầu tiên trong quý đó (tổng các quý = 92 = tổng số khách trong dữ liệu).
- Code: [analysis.py](analysis.py); log: `run_log.txt`; bảng: `customers_per_quarter.csv`, `janmay_change_by_country.csv`, `janmay_change_by_productline.csv`, `janmay_growth_source.csv`.

## Lưu ý
- Đây là **dấu hiệu từ dữ liệu bán hàng**, không phải nguyên nhân. Ví dụ: không có khách mới có thể do ngừng hoạt động tìm khách, do đổi hệ thống ghi nhận, hoặc đơn giản do file chỉ chứa một danh sách khách cố định - cần kiểm tra với nguồn dữ liệu / bộ phận bán hàng.
- Q2-2005 chỉ có 2 tháng; trạng thái các đơn cuối tháng 5 có thể còn thay đổi.
- Không phân tích giá: cột `PRICEEACH` bị chặn ở 100 trên 46% số dòng nên không đáng tin.

## Gợi ý kiểm tra tiếp (không phải kết luận)
1. Xử lý 4 đơn On Hold (đặc biệt đơn từ 11/2004) và 3 đơn Disputed - bắt đầu từ Euro Shopping Channel.
2. Xác minh vì sao không có khách mới từ Q4-2004.
3. Theo dõi tỷ trọng top 2 khách hàng hàng quý.
