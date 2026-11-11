# Phân tích tiêu thụ điện hộ gia đình và dự báo tháng 12/2010

## Dữ liệu và cách tính

- File: `data/household_power_consumption.txt`, đo theo phút, 2.075.259 dòng.
- Thực tế dữ liệu chạy từ **16/12/2006 17:24 đến 26/11/2010 21:02**, không phải đến hết 11/2010. **Tháng 12/2010 hoàn toàn không có dữ liệu.**
- Đơn vị: `Global_active_power` là công suất trung bình (kW) trong mỗi phút. kWh/ngày = kW trung bình × 24. Ngày nào có dưới 80% số phút đo được (21 ngày) bị loại khỏi thống kê xu hướng, mùa vụ và mô hình.
- Thiếu dữ liệu: 25.979 phút (1,25%), gồm 9 khoảng trống từ 70 phút trở lên (chi tiết ở dưới).

## 1. Xu hướng

- Trung bình kWh/ngày theo năm (chỉ tính ngày đủ dữ liệu): 2007: 26,8; 2008: 25,7; 2009: 25,9; 2010 (đến tháng 11): 25,4.
- Hồi quy tuyến tính trên trung bình tháng cho thấy xu hướng giảm nhẹ khoảng **0,66 kWh/ngày mỗi năm** (khoảng 2–3%/năm). Mức tiêu thụ gần như đi ngang từ 2008 đến 2010; phần lớn mức chênh lệch giữa các năm là do mùa và thời tiết.

## 2. Tính mùa vụ

- **Theo tháng (năm):** cao nhất vào tháng 12 (36,0 kWh/ngày), tháng 1 (35,1) và tháng 11 (31,0); thấp nhất vào tháng 8 (13,7) và tháng 7 (16,8). Mùa đông cao, mùa hè thấp, tháng 8 còn bị kéo xuống bởi giai đoạn vắng nhà năm 2008.
- **Theo thứ (ngày):** cuối tuần cao hơn các ngày trong tuần. Thứ Bảy 30,2 và Chủ nhật 29,3 kWh/ngày, trong khi thứ Năm thấp nhất (23,5).
- **Theo giờ (ngày):** thấp nhất lúc 3–5 giờ sáng (~0,44 kW). Có hai đỉnh: buổi sáng khoảng 7 giờ (~1,50 kW) và buổi tối 20 giờ (~1,90 kW).

## 3. Bất thường

**Khoảng trống dữ liệu (dài ≥ 70 phút):**

| Thời gian | Độ dài |
|---|---|
| 17/8/2010 21:02 – 22/8/2010 21:27 | ~5 ngày |
| 25/9/2010 03:56 – 28/9/2010 19:12 | ~3,6 ngày |
| 28/4/2007 – 30/4/2007 | ~2,6 ngày |
| 13/6/2009 – 15/6/2009 | ~2,2 ngày |
| 12/1/2010 – 14/1/2010 | ~2,2 ngày |
| 20/3/2010 – 21/3/2010 | ~1,4 ngày |
| 13/8/2009 | ~15 giờ |
| 15/7/2007 | ~1,4 giờ |
| 10/12/2008 | ~1,2 giờ |

**Giai đoạn tiêu thụ thấp bất thường (có thể vắng nhà, chưa xác nhận):**
- **25/2 – 3/3/2007:** khoảng 8–9 kWh/ngày, sau đó tăng lên 35–58 kWh/ngày từ 4/3/2007. Đây là một tuần thấp rõ rệt.
- **6 – 30/8/2008:** khoảng 4–6 kWh/ngày, mức thấp nhất trong toàn bộ dữ liệu, tải nền gần như ổn định (~0,19 kW). Ngày 31/8/2008 tiêu thụ trở lại ~25 kWh/ngày.
- **1 – 14/8/2010:** khoảng 9 kWh/ngày, sau đó tăng lên 17–19 kWh/ngày từ 15/8/2010. Các ngày 18–22/8/2010 bị thiếu dữ liệu.

**Ngày và tuần đột biến cao:** các ngày cao nhất (>50 kWh) tập trung vào tháng 12 và đầu tháng 1 (ví dụ 16/12/2006 với 73 kWh, 23/12/2006 với 80 kWh, 24/12/2009 với 48 kWh), phù hợp với mùa lễ và thời tiết lạnh.

**Tuần bất thường (|z| ≥ 2,5 so với mức nền trượt 9 tuần):** 33 tuần, trong đó phần lớn là tuần thấp (chỉ 9 tuần cao). Các tuần thấp nhất nằm trong giai đoạn 8/2008 (4 tuần liên tiếp) và tuần 4/3/2007. Danh sách đầy đủ ở `outputs/weekly_kwh.csv`.

## 4. Dự báo tháng 12/2010

Phương pháp: hồi quy tuyến tính trên log(trung bình kWh/ngày theo tháng), gồm xu hướng theo thời gian và hiệu ứng từng tháng, huấn luyện trên các tháng đủ dữ liệu từ 01/2007 đến 11/2010, bỏ tháng 8/2008. Tổng tháng = trung bình kWh/ngày × 31.

| Chỉ tiêu | Giá trị |
|---|---|
| Dự báo trung vị tổng điện tháng 12/2010 | **≈ 1.033 kWh** (≈ 33 kWh/ngày) |
| Khoảng 80% | 912 – 1.170 kWh |
| Khoảng 95% (mô hình) | 851 – 1.255 kWh |
| Độ nhạy (bỏ thêm tháng 2–3/2007) | 1.043 kWh |

So với tháng 12/2009 (1.015 kWh), dự báo cao hơn khoảng 2%.

**Kiểm định ngược (backtest):**
- Dự báo tháng 12/2009 (huấn luyện đến 11/2009): 1.051 kWh so với thực tế 1.015 kWh, sai số +3,5%, nằm trong khoảng 95%.
- Dự báo tháng 12/2008 (chỉ huấn luyện trên dữ liệu 2007): 1.266 kWh so với thực tế 949 kWh, sai số +33%. Mô hình chỉ có một năm dữ liệu để học xu hướng nên không đáng tin ở giai đoạn này.
- Sai số tuyệt đối trung bình: mô hình 18,5%, so với phương pháp "lấy tháng 12 năm trước" 17,0%. Chỉ có 2 điểm kiểm định nên không đủ để kết luận.

**Khuyến nghị về độ bất định:** khoảng 95% của mô hình (851–1.255 kWh) có thể hẹp hơn thực tế, vì sai số kiểm định lên tới 33%. Nên dùng khoảng thực tế rộng hơn, khoảng **800 – 1.300 kWh**, và xem 1.033 kWh là giá trị trung tâm. Dự báo giả định thời tiết tháng 12/2010 tương tự các năm trước và không có giai đoạn vắng nhà.

## Biểu đồ

- `outputs/chart_xu_huong_ngay.png`: kWh hàng ngày, trung bình trượt 30 ngày, các khoảng trống dữ liệu, giai đoạn 8/2008.
- `outputs/chart_mua_vu_theo_nam.png`: mùa vụ theo tháng, từng năm.
- `outputs/chart_tuan_gio.png`: theo thứ trong tuần và theo giờ.
- `outputs/chart_du_bao_12_2010.png`: tổng kWh theo tháng và dự báo tháng 12/2010.

## Tệp đầu ra

- `outputs/daily_kwh.csv`, `outputs/weekly_kwh.csv`, `outputs/monthly_mean_daily_kwh.csv`, `outputs/monthly_fit_data.csv`, `outputs/forecast_dec2010.csv`, `outputs/backtest_december.csv`.
- Mã phân tích: `scripts/` (`analyze.py`, `forecast.py`, `charts.py`).

## Giới hạn

- Không có dữ liệu thời tiết hay nhiệt độ, nên không tách được ảnh hưởng của thời tiết.
- Các giai đoạn "vắng nhà" (2/2007, 8/2008, 8/2010) là suy đoán từ hình dạng tiêu thụ, chưa được xác nhận.
- Dự báo dựa trên 3 năm và 1 tháng 12 đầy đủ (2007–2009), nên độ tin cậy hạn chế.
