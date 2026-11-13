# Điện năng hộ gia đình 12/2006–11/2010: xu hướng, mùa vụ, bất thường và dự báo tháng 12/2010

## Trả lời ngắn gọn

- **Xu hướng:** gần như đi ngang. Trung bình ngày theo từng năm điện (12 tháng từ tháng 12) là 26,6 → 26,4 → 25,7 → 26,1 kWh/ngày, tức thay đổi khoảng −2% sau 3 năm. Hồi quy tuyến tính theo tháng cho −1,3%/năm, nhưng con số này yếu và bị lệch bởi mùa vụ, nên chỉ coi là tham khảo.
- **Mùa vụ mạnh nhất là theo mùa trong năm:** tháng 12 trung bình 36,0 kWh/ngày, tháng 7 chỉ 16,8 kWh/ngày, tháng 8 là 13,7 kWh/ngày. Theo tuần, cuối tuần (Thứ Bảy 30,2; Chủ Nhật 29,3) cao hơn ngày thường (23,5–26,0). Theo giờ, đỉnh ở 19–21h (~1,9 kW) và đáy lúc 3–5h sáng (~0,44 kW).
- **Bất thường:** tháng 8/2008 chỉ ~206 kWh (~6,6 kWh/ngày), thấp hơn nhiều so với các tháng 8 khác (440–570 kWh). Nhiều tuần thấp bất thường cũng xuất hiện vào tháng 8/2010 và tháng 3/2007–2008. Có 9 khoảng trống ≥1 giờ, tổng ~17,9 ngày, dài nhất là 17–22/8/2010 (5 ngày).
- **Dự báo tháng 12/2010:** ~**1.039 kWh** (khoảng 33,5 kWh/ngày). Khoảng 90%: **919–1.369 kWh** (dùng toàn bộ 32 tháng backtest). Nếu chỉ dùng các gốc dự báo từ 2009 (20 tháng), khoảng hẹp hơn: **1.010–1.224 kWh**. Tham chiếu: tháng 12/2009 thực tế là 1.015 kWh.

## Dữ liệu và cách tính

- Nguồn: `data/household_power_consumption.txt`, 2.075.259 dòng theo phút, từ 16/12/2006 17:24 đến 26/11/2010 21:02.
- `Global_active_power` là công suất trung bình (kW) trong 1 phút. Năng lượng ngày = kW trung bình × 24 (kWh).
- 98,7% số phút có giá trị; 25.979 phút (1,25%) là `?` (NaN). Không có dòng bị thiếu hoàn toàn và không có trùng lặp thời gian.
- "Ngày đủ dữ liệu" = có ít nhất 80% số phút có giá trị (1.421/1.442 ngày). "Tổng tháng ước tính" = trung bình kWh/ngày của các ngày đủ dữ liệu × số ngày trong tháng. Cách này hiệu chỉnh phần thiếu, nên không phải tổng thô.
- Nguyên tắc chia dữ liệu theo thời gian: các phép dự báo chỉ dùng dữ liệu trước gốc dự báo; không có cột phân nhóm hay kỳ kiểm định sẵn.

## Kết quả chi tiết

**1. Xu hướng.** Khối 12 tháng bắt đầu từ tháng 12 (kWh/ngày): 2006–07: 26,65; 2007–08: 26,45; 2008–09: 25,72; 2009–10 (đến 26/11): 26,08. Biến động nhỏ và không có xu hướng rõ rệt; năm 2008–09 thấp nhất, phần lớn do tháng 8/2008.

**2. Mùa vụ.**
- Theo tháng (kWh/ngày): T1 35,1 · T2 31,2 · T3 29,6 · T4 25,2 · T5 24,7 · T6 21,8 · T7 16,8 · T8 13,7 · T9 23,4 · T10 27,3 · T11 31,0 · T12 36,0. Mô hình là mùa đông cao, mùa hè thấp.
- Theo thứ (kWh/ngày): T2 24,0 · T3 25,6 · T4 26,0 · T5 23,5 · T6 25,0 · T7 30,2 · CN 29,3.
- Theo giờ (kW trung bình): đỉnh sáng 7–8h (~1,5 kW), đỉnh tối 19–21h (~1,7–1,9 kW), đáy 3–5h (~0,44 kW).

**3. Bất thường** (`anomalies_daily.csv`, `anomalies_weekly.csv`; ngưỡng |z| > 3 so với trung vị cùng thứ, cửa sổ 9 tuần):
- 90 ngày bất thường, phần lớn là ngày thấp (8–12 kWh) vào tháng 2–3/2007, tháng 10–11/2007, tháng 2–3/2008, tháng 8/2008 và tháng 8/2010, cùng một số ngày cao (~50–80 kWh) vào tháng 12/2006, tháng 2–3/2007 và cuối 2008.
- 25 tuần bất thường. Mạnh nhất: tuần kết thúc 04/03/2007 (13 kWh/ngày so với trung vị 36), 02/03/2008 (14 so với 31), 04/11/2007 (16 so với 29), 07/03/2010 (17 so với 30).
- Khoảng trống (`gaps_ge_1h.csv`): 9 khoảng ≥1 giờ, đều là giá trị thiếu (NaN), không có dòng bị mất. Dài nhất: 17–22/8/2010 (5,0 ngày), 25–28/9/2010 (3,6 ngày), 28–30/4/2007 (2,6 ngày), 13–15/6/2009 (2,3 ngày), 12–14/1/2010 (2,2 ngày).
- Lưu ý: tuần thấp bất thường tháng 8/2010 xảy ra trước khoảng trống 17–22/8/2010. Dữ liệu không đủ để biết nguyên nhân (nhà vắng, thiết bị ngắt, hay lỗi đo).

**4. Dự báo tháng 12/2010.**
- Mô hình: hồi quy tuyến tính theo ngày với xu hướng thời gian, 3 cặp Fourier theo năm và biến giả thứ trong tuần; huấn luyện trên 1.421 ngày đủ dữ liệu đến 26/11/2010.
- Backtest (32 gốc hàng tháng, 2008–10): sai số tuyệt đối trung bình (MAPE) mô hình **14,3%**, so với naive "cùng tháng năm trước" 15,5% và naive "30 ngày gần nhất" 21,1%.
- Độ nhạy: bỏ tháng 8/2008 (ngoại lệ) thì MAPE mô hình 8,6% so với 10,3% naive năm trước. Chỉ dùng gốc từ 2009 (n=20) thì MAPE 6,1%.
- Sai số tháng 12 đã kiểm tra: +19,5% (12/2008) và +4,0% (12/2009), tức mô hình dự báo cao hơn thực tế trong cả hai năm.

## Mức độ tin cậy và hạn chế

- **Tháng 12/2010 nằm ngoài dữ liệu** (dữ liệu dừng ở 26/11/2010), nên đây là dự báo thật, không phải đánh giá trên dữ liệu đã có.
- Chỉ có 3 tháng 12 đầy đủ (2007, 2008, 2009). Khoảng 90% dựa trên 32 tháng backtest, nên không chắc chắn lắm.
- Khoảng hẹp (1.010–1.224) dựa trên dữ liệu gần hơn và có độ chính xác tốt hơn, nhưng chỉ 20 tháng. Khoảng rộng (919–1.369) bao phủ cả giai đoạn 2008 khi mô hình còn ít dữ liệu. **Khuyến nghị dùng khoảng rộng làm mức an toàn, khoảng hẹp làm mức kỳ vọng.**
- Mô hình không có thông tin thời tiết, kỳ nghỉ lễ (Giáng sinh, Tết dương lịch), hay thay đổi hộ gia đình, nên có thể sai nếu có biến động bất thường.
- Đây chỉ là một hộ gia đình, không khái quát được cho các hộ khác.
- Mọi kết quả là **liên quan**, không phải quan hệ nhân quả.

## Tệp đầu ra

- `analysis.py`: toàn bộ mã đã chạy; `run_log.txt`: nhật ký kết quả.
- `summary.json`: các số liệu chính và độ nhạy; `monthly.csv`, `yearly_blocks.csv`, `seasonal_*.csv`, `backtest.csv`, `forecast_dec2010.csv`, `forecast_dec2010_daily.csv`.
- Biểu đồ: `chart1_xu_huong_ngay.png` (xu hướng ngày và bất thường), `chart2_thang.png` (tổng tháng), `chart3_mua_vu.png` (mùa vụ), `chart4_du_bao_thang12_2010.png` (dự báo).
