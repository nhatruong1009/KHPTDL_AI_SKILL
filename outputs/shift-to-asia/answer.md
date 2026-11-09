# Sẽ thế nào nếu chuyển thị trường sang châu Á? - sales_data_sample.csv

**Câu hỏi:** Sẽ thế nào nếu như tôi chuyển thị trường qua châu Á?

**Phạm vi:** dữ liệu **không thể dự báo** kết quả của việc chuyển thị trường (không có quy mô thị trường châu Á, đối thủ, chi phí, hay dữ liệu về việc đã từng đầu tư vào một thị trường). Phân tích dưới đây trả lời những gì dữ liệu **có thể** cho biết: (1) châu Á đang ra sao, (2) có khác các thị trường hiện tại không, (3) **rủi ro doanh thu** nếu rời bỏ thị trường hiện tại (kịch bản số học).
"Châu Á" = Japan, Singapore, Philippines (Australia thuộc APAC nhưng không phải châu Á, được tách riêng).

## Trả lời
**Dựa trên dữ liệu, chuyển hẳn sang châu Á là rủi ro rất cao; mở rộng thêm châu Á song song với thị trường hiện tại là hợp lý hơn.**

1. **Châu Á hiện rất nhỏ và không tăng.** 235K USD trong 12 tháng gần nhất = **4.6% doanh thu**, giảm nhẹ **-0.7%** so với 12 tháng trước (trong khi châu Âu +42.9%, Bắc Mỹ +21.9%). Chỉ có **5 khách hàng, 18 đơn trong cả 2.4 năm**; Philippines không có đơn nào sau 11/2004, Osaka Souveniers không mua lại sau 04/2004; Q2-2005 châu Á chỉ có 3K.
2. **Khách châu Á mua giống hệt các nơi khác.** Giá trị đơn trung vị 32,060 vs 33,181 USD (Mann-Whitney p = 0.78, n = 18 vs 285 - không khác biệt). Tỷ lệ deal size và cơ cấu sản phẩm tương tự (Classic Cars ~40% ở cả hai); châu Á mua nhiều Trucks and Buses hơn (17.9% vs 11.1%) và ít Vintage Cars hơn (11.6% vs 19.4%). => Không có dấu hiệu khách châu Á "giá trị cao hơn" để bù cho việc rời thị trường cũ.
3. **Cái giá nếu rời thị trường hiện tại (kịch bản):**

| Nếu mất ... doanh thu ngoài châu Á | Doanh thu mất | Châu Á cần đạt / 12 tháng | Gấp bao nhiêu lần hiện tại |
|---|---|---|---|
| 10% | 486,684 | 721,758 | x3.1 |
| 25% | 1,216,710 | 1,451,784 | x6.2 |
| 50% | 2,433,420 | 2,668,494 | x11.4 |
| 100% (chuyển hẳn) | 4,866,839 | 5,101,913 | x21.7 |

   Riêng USA (1.86M) đã bằng **7.9 lần** toàn bộ châu Á. Với tốc độ hiện tại (-0.7%/năm), dữ liệu không cho thấy châu Á có đà để đạt các mức trên.

## Biểu đồ
- [revenue_by_region.png](revenue_by_region.png) - doanh thu theo vùng mỗi quý, phần châu Á (đỏ)
- [scenario_asia_needed.png](scenario_asia_needed.png) - châu Á cần lớn bao nhiêu để bù phần doanh thu mất

## Cách làm
- Doanh thu = `SALES`, bỏ đơn Cancelled (2,763 / 2,823 dòng). Vùng gán theo `COUNTRY`.
- So sánh 12 tháng gần nhất (06/2004-05/2005) với 12 tháng trước; giá trị đơn tính theo tổng mỗi `ORDERNUMBER`; kiểm định Mann-Whitney U.
- Kịch bản: doanh thu châu Á cần có = châu Á hiện tại + phần doanh thu bị mất ở thị trường khác (giả định đơn giản, không có dữ liệu để ước lượng xác suất mất khách).
- Code: [analysis.py](analysis.py); số liệu: `region_summary.csv`, `scenarios.csv`, `productline_mix_asia_vs_rest.csv`, `run_log.txt`.

## Lưu ý
- **Đây không phải dự báo.** Doanh thu thấp ở châu Á có thể do công ty chưa đầu tư ở đó, không nhất thiết do thị trường nhỏ - dữ liệu bán hàng nội bộ không phân biệt được hai khả năng này. Muốn đánh giá đúng cần dữ liệu ngoài: quy mô thị trường, đối thủ, chi phí vào thị trường, hoặc một thử nghiệm nhỏ (ví dụ mở rộng có giới hạn 1-2 quý rồi đo).
- Châu Á chỉ có 18 đơn / 5 khách: mọi so sánh về châu Á có độ tin cậy thấp.
- Nếu tính cả Australia (APAC), tỷ trọng là 11.0% - vẫn nhỏ.
- **Không dùng so sánh giá với MSRP:** cột `PRICEEACH` bị chặn ở 100 trên 46% số dòng (1,304 / 2,823), nên chênh lệch giá theo vùng không đáng tin.
