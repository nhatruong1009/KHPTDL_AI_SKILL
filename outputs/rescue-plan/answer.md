# Làm gì để cứu tình hình kinh doanh - sales_data_sample.csv

**Câu hỏi:** Tôi có thể làm gì để cứu được tình hình kinh doanh hiện tại?
**Cách hiểu:** dữ liệu dừng ở 31/05/2005. Dựa trên các cảnh báo trong `outputs/business-health-check`, đo xem mỗi "đòn bẩy" đáng bao nhiêu tiền và đáng ưu tiên đến đâu. Dữ liệu cho thấy **quy mô cơ hội**, không chứng minh nguyên nhân.

## Trả lời: 3 việc nên làm, theo thứ tự ưu tiên
1. **Gỡ 251K USD đang bị treo (làm ngay).** 4 đơn On Hold = 179K, 3 đơn Disputed = 72K. Đây là tiền đã bán nhưng chưa thu; bằng ~14% doanh thu 2005 đến nay (1.79M). Bắt đầu từ đơn On Hold của Volvo Model Replicas (từ 11/2004) và đơn tranh chấp của Euro Shopping Channel (khách lớn nhất).
2. **Chuẩn bị mùa cao điểm Q4 - việc có đòn bẩy lớn nhất.** Tháng 9-12 chiếm **60% (2003) và 51% (2004)** doanh thu cả năm, riêng tháng 11 là 24-30%. Nghĩa là kết quả cả năm phần lớn được quyết định trong 4 tháng cuối: cần tồn kho, năng lực giao hàng và chiến dịch bán sẵn sàng trước tháng 9, và không để đơn kẹt như hiện nay lặp lại vào lúc cao điểm.
3. **Chủ động liên hệ khách cũ, ưu tiên khách lớn trước mùa Q4.** 52/83 khách đã mua trong 2004 (tổng 2.62M USD, tức **57% doanh thu 2004**) chưa có đơn nào trong 2005. 15 khách "ngủ" lớn nhất (ngày đặt gần nhất > 180 ngày) có tổng doanh thu lịch sử 1.96M USD; danh sách đầy đủ 49 khách: `winback_candidates.csv`. Vì khách mới đã **0 từ Q4-2004**, nguồn doanh thu thực tế duy nhất là khách cũ.

**Việc thứ tư (nền tảng):** tìm hiểu vì sao không có khách mới và giảm phụ thuộc Euro Shopping Channel (18.2% doanh thu tháng 1-5/2005, từ 10.6%). Khách lớn nhất chiếm 8.8% doanh thu cả giai đoạn, top 5 chiếm 21%, nên rủi ro tập trung chưa cực đoan.

## Biểu đồ
- [rescue_levers.png](rescue_levers.png) - mùa vụ theo tháng và khách theo số ngày từ đơn gần nhất

## Cách làm
- Mốc "hiện tại" = ngày cuối dữ liệu (31/05/2005). Doanh thu = SALES, bỏ đơn Cancelled; đếm theo đơn (307 đơn, 92 khách).
- Code: [analysis.py](analysis.py), log `run_log.txt`; bảng `monthly_share.csv`, `winback_candidates.csv`.

## Lưu ý quan trọng
- **Khách "ngủ" phần lớn là do mùa vụ**: nhiều khách có đơn gần nhất vào tháng 11/2004 (cách 180-210 ngày), tức họ mua theo chu kỳ năm, chưa chắc đã bỏ đi. Vì vậy 57% không phải "mất khách"; đúng thời điểm để liên hệ là trước tháng 9-10, không phải gấp.
- Chỉ có 2 năm đầy đủ (2003, 2004) để suy ra mùa vụ; 2005 mới có 5 tháng nên chưa biết Q4-2005 sẽ ra sao.
- Dữ liệu không có chi phí, biên lợi nhuận, hay thông tin chiến dịch, nên không đánh giá được việc nào sinh lời nhất hay giải pháp nào hiệu quả; con số chỉ là quy mô doanh thu.
- Đơn On Hold/Disputed có thể đã được giải quyết sau ngày 31/05/2005 mà dữ liệu chưa phản ánh.
- Không phân tích giá do `PRICEEACH` bị chặn ở 100.
