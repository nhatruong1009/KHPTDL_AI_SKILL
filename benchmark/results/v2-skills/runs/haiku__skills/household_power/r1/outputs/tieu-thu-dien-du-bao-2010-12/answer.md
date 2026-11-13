# Tiêu thụ điện hộ gia đình (12/2006 – 11/2010) và dự báo tháng 12/2010

**Trả lời:**
- **Xu hướng:** Không có xu hướng tăng hoặc giảm rõ rệt. Mức trung bình gần như đi ngang quanh 25–26 kWh/ngày (ước lượng xu hướng −2,2%/năm, khoảng tin cậy 95% −10,3% đến +5,9%).
- **Mùa vụ:** Tiêu thụ theo **năm** biến động mạnh nhất. Tháng 1 trung bình 35,3 kWh/ngày, tháng 8 chỉ 12,5 kWh/ngày (cao gấp khoảng 2,8 lần). Theo **tuần**, cuối tuần (Thứ 7, Chủ nhật) cao hơn ngày thường khoảng 19%. Theo **ngày**, công suất đỉnh lúc 20h (≈1,90 kW) và đáy lúc 4h (≈0,44 kW).
- **Bất thường:** Có 6 khoảng trống từ 1 ngày trở lên, dài nhất khoảng 5 ngày (17–22/08/2010). Có 22 tuần bất thường, 9 trong số đó rơi vào tháng 8. Tuần thấp nhất là tuần kết thúc 24/08/2008, trung bình 4,4 kWh/ngày so với mức nền 15,3.
- **Dự báo tháng 12/2010:** khoảng **1.025 kWh** (khoảng 95%: **695 – 1.509 kWh**). Đây là dự báo từ mô hình chính. Nếu mức giảm 8% của tháng 11/2010 so với 2009 (chỉ tính 1–26/11) tiếp tục sang tháng 12, kết quả khoảng **935 kWh**. Cả hai đều nằm trong khoảng 95%.

**Bằng chứng:**

| Tháng 12 | Tổng kWh (ước tính) |
|---|---|
| 2007 | 1.210 |
| 2008 | 949 |
| 2009 | 1.015 |
| **2010 (dự báo)** | **1.025** (695 – 1.509) |

Biểu đồ:
- [Xu hướng theo tháng](xu_huong_thang.png)
- [Mùa vụ theo tháng, thứ, giờ](mua_vu.png)
- [Khoảng trống và ngày/tuần bất thường](ngay_tuan_bat_thuong.png)
- [Dự báo tháng 12/2010](du_bao_thang_12_2010.png)

**Cách làm:**
- **Dữ liệu:** 2.075.259 bản ghi theo phút (16/12/2006 – 26/11/2010), không trùng lặp, 1,25% giá trị thiếu. `Global_active_power` là công suất trung bình (kW) trong mỗi phút, nên năng lượng mỗi phút = kW / 60 (kWh).
- **Chuẩn bị:** Chỉ dùng ngày có ≥90% số phút dữ liệu (1.420/1.442 ngày). Với các ngày thiếu dưới 10% phút, tổng được hiệu chỉnh theo tỉ lệ phút có dữ liệu.
- **Bất thường:** Ngày/tuần có sai lệch lớn so với mức nền (trung vị trượt, dùng z-score theo MAD, ngưỡng |z| > 3,5 với ngày và > 3 với tuần). Đây là các điểm cần xem xét, không phải lỗi đã xác nhận.
- **Dự báo:** Mô hình hồi quy trên log(kWh trung bình/ngày) gồm xu hướng tuyến tính và hiệu ứng tháng, huấn luyện trên 39 tháng đủ dữ liệu (loại tháng 12/2006, tháng 8/2010 và tháng 11/2010 vì thiếu ngày). Kết quả nhân với 31 ngày.
- **Kiểm định ngoài mẫu:** Dự báo trước 2 tháng cho 14 tháng (2009–2010). Sai số trung bình tuyệt đối tổng tháng là 8,8%, RMSE (log) 0,10. Khoảng 95% dùng giá trị rộng hơn giữa sai số mô hình (±0,39 log) và sai số backtest (±0,20 log), tức là sai số mô hình.

**Giả định và hạn chế:**
- **Tháng 12/2010 chưa có dữ liệu.** Dữ liệu dừng ở 26/11/2010, nên dự báo là ước lượng, không phải số đo.
- **Khoảng dự báo rất rộng** (±~37%) vì các tháng mùa đông dao động mạnh giữa các năm (949–1.210 kWh). Hai cách tính cho kết quả khác nhau khoảng 9%, nên nên xem khoảng 935–1.025 kWh là vùng hợp lý nhất.
- **Sai số có xu hướng:** Năm 2010 mô hình thường dự báo thấp hơn thực tế (ví dụ tháng 2/2010 thấp hơn 17%). Nếu xu hướng này tiếp tục, con số thực tế có thể cao hơn 1.025 kWh.
- **Không có dữ liệu thời tiết, số người trong nhà, hay thiết bị.** Các nguyên nhân như "tháng 8 thấp vì vắng nhà" chỉ là giả thuyết, chưa kiểm chứng.
- **Đây là quan sát tương quan**, không phải quan hệ nhân quả. Dữ liệu chỉ có một hộ gia đình, không đại diện cho các hộ khác.
- **Khoảng trống dữ liệu** làm thiếu khoảng 25.691 phút trong các đoạn ≥60 phút. Các tháng có khoảng trống không được dùng để huấn luyện mô hình.

**Kiểm tra chất lượng (answer-qa):**

| Kiểm tra | Kết quả | Ghi chú |
|---|---|---|
| Trả lời đúng câu hỏi (xu hướng, mùa vụ, bất thường, dự báo 12/2010) | Đạt | Mỗi ý có con số |
| Con số truy vết được đến output | Đạt | Tất cả từ `so_lieu_chinh.json` và các CSV, chạy lại `analysis.py` cho ra cùng kết quả |
| Mẫu số, đơn vị (kW/60 → kWh), tháng không đầy đủ | Đạt | Tháng đầu/cuối và tháng có khoảng trống bị loại khỏi huấn luyện |
| Kiểm định sai lệch độ nhạy | Đạt | Kết quả 935 kWh được nêu trong phần trả lời, không che giấu |
| Ngôn ngữ nhân quả / khái quát | Đạt | Dùng "tương quan", "giả thuyết" |
| Biểu đồ: tiêu đề nêu kết luận, trục có nhãn, trục cột bắt đầu từ 0 | Đạt | Đã xem biểu đồ dự báo |

**Kết luận: sẵn sàng.**
