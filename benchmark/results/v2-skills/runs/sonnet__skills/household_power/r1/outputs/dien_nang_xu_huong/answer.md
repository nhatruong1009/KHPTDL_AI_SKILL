# Điện năng hộ gia đình 12/2006 – 11/2010: xu hướng, mùa vụ, bất thường và dự báo 12/2010

**Trả lời:** Mức tiêu thụ **gần như không có xu hướng dài hạn** (cùng 11 tháng T1–T11: 8.560 → 8.469 → 8.415 → 8.474 kWh cho 2007–2010, tức −1,1%, −0,6%, +0,7%). Biến động chủ yếu do **mùa vụ năm** (tháng 12–1 cao nhất, tháng 7–8 thấp nhất) và các **tuần vắng nhà**. **Dự báo tổng điện năng tháng 12/2010 ≈ 958 kWh** (khoảng 80%: 856–1.133; khoảng 95%: 795–1.220).

## Bằng chứng
**Xu hướng** ([biểu đồ](01_xu_huong_va_du_bao.png), `xu_huong_nam.csv`, `tong_thang.csv`)
- Tổng 12 tháng liên tiếp: 12/2007–11/2008 = 9.679 kWh; 12/2009–11/2010 = 9.489 kWh; 12 tháng ngay trước đó = 9.363 kWh. Độ dốc chỉ số khử mùa ≈ −0,5 điểm %/năm, nhỏ so với dao động mùa.

**Mùa vụ** (`chi_so_mua_thang.csv`, `mua_vu_thu.csv`, `mua_vu_gio.csv`)
- Năm ([biểu đồ](02_mua_vu_nam.png)): chỉ số tháng (trung vị 2007–2009, 1,0 = trung bình năm) cao nhất tháng 1 (1,38) và 12 (1,29), thấp nhất tháng 7 (0,61) và 8 (0,63). Mùa đông cao gấp khoảng 2 lần mùa hè.
- Tuần ([biểu đồ](03_mua_vu_ngay_tuan.png)): thứ 7 và CN cao hơn ngày thường (trung bình 29,9 và 29,3 kWh/ngày so với 23,5–26,0 kWh các ngày thứ 2–6). Sau khi khử mùa tháng, chỉ số thứ 7/CN ≈ 1,12; khác biệt giữa các thứ có ý nghĩa (Kruskal–Wallis p < 1e-20, nhưng độ lớn ~±10% mới là điều đáng chú ý).
- Ngày: ngày thường có đỉnh sáng (7h ≈ 1,72 kW) và đỉnh tối (20–21h ≈ 1,85 kW), thấp nhất 3–5h (~0,43 kW). Cuối tuần không có đỉnh sáng rõ, dùng nhiều suốt ban ngày (~1,5 kW lúc 11–14h) và đỉnh tối ~2,05 kW.

**Giai đoạn bất thường** ([biểu đồ](04_tuan_bat_thuong.png), `tuan_bat_thuong.csv`, `khoang_trong_du_lieu.csv`)
- *Khoảng trống dữ liệu*: 25.979 phút thiếu (1,25% tổng 2.075.259 phút; không có dòng bị mất, thiếu ở dạng giá trị `?`). Có 9 khoảng ≥ 60 phút; dài nhất: 17–22/8/2010 (5,0 ngày), 25–28/9/2010 (3,6 ngày), 28–30/4/2007 (2,6 ngày), 13–15/6/2009 (2,3 ngày), 12–14/1/2010 (2,2 ngày), 20–21/3/2010 (1,4 ngày). Hai khoảng dài nhất đều trong 2010 → 8/2010 và 9/2010 chỉ có 84% và 88% số phút.
- *Tuần bất thường* (so với trung vị trượt 9 tuần; |z| > 3 theo MAD): rõ nhất là **tháng 8/2008, bốn tuần liên tiếp chỉ 31–60 kWh/tuần (z từ −8 đến −17)**, cả tháng chỉ 206 kWh so với 440–569 kWh của tháng 8 các năm 2007, 2009, 2010 (đã hiệu chỉnh) — mô hình giống cả nhà vắng. Các tuần thấp ngắn hạn khác: đầu tháng 3 và giữa tháng 4/2007, 24/6/2007, 4/11/2007, 2/3/2008, 2/11/2008, 7/3/2010 (~84–116 kWh so với cơ sở ~190–250) và tháng 8 các năm 2009, 2010. Một tuần cao bất thường: tuần kết thúc 30/12/2007 (317 kWh, z = +3,3). Dữ liệu không cho biết nguyên nhân; "vắng nhà/nghỉ lễ" chỉ là giả thuyết hợp lý.
- 7 tuần có <90% số phút (không chấm điểm bất thường): tuần kết thúc 29/4/2007, 14/6/2009, 17/1/2010, 21/3/2010, 22/8/2010, 26/9/2010 và 3/10/2010.

**Dự báo 12/2010** (`du_bao_thang12_2010.csv`, `du_bao_khoang.csv`, `backtest*.csv`, [biểu đồ kiểm tra lùi](05_backtest.png))

| Phương pháp | Dự báo 12/2010 (kWh) | MAPE kiểm tra lùi 2009–2010 (n=19) |
|---|---|---|
| ratio_2m (tỷ lệ tháng/2 tháng trước ở các năm trước × TB 10–11/2010) | **958** | **6,8%** |
| yoy_scaled (12/2009 × tỷ lệ 12 tháng) | 928 | 9,3% |
| seasonal_naive (= 12/2009) | 1.015 | 9,8% |

- Chọn ratio_2m vì sai số kiểm tra lùi nhỏ nhất (theo thời gian, mỗi tháng chỉ dùng dữ liệu trước đó). Khoảng bất định lấy từ sai số log của kiểm tra lùi (độ lệch chuẩn 0,109, lệch +0,028): 80% = 856–1.133, 95% = 795–1.220 kWh. Ba phương pháp (928–1.015) và 3 tháng 12 trước (1.210; 949; 1.015) đều nằm trong khoảng 95%.

## Cách làm
- kWh mỗi phút = `Global_active_power` (kW)/60; cộng theo kỳ. Tháng/tuần thiếu dữ liệu được **hiệu chỉnh**: trung bình kWh/phút quan sát × số phút của kỳ (giả định phút thiếu giống phút có dữ liệu). 12/2006 (chỉ từ 16/12) bị loại khỏi bảng tháng; 11/2010 (đến 26/11 21:02, 100% phút có dữ liệu) được quy ra cả tháng = 861,7 kWh (thực đo 743,3).
- Mùa vụ: tỷ lệ so với trung bình năm (2007–2009, đủ 3 năm), chỉ số thứ trong tuần chỉ trên các ngày phủ ≥95%; mùa giờ theo kW trung bình. Không dùng được `statsmodels` (không cài được trong môi trường) nên không chạy STL/Holt-Winters; thay bằng chỉ số tỷ lệ và dự báo tự cài đặt.

## Giả định & hạn chế
- Chỉ ~4 chu kỳ năm → mùa vụ năm và dự báo dựa trên 3 tháng 12 (rất khác nhau: 1.210 / 949 / 1.015). Khoảng bất định có thể còn hẹp; backtest chỉ 19 điểm và phương pháp được chọn trên chính các điểm đó (hơi lạc quan).
- Dự báo giả định tháng 12/2010 không có kỳ vắng nhà bất thường như 8/2008. Nếu có, tổng sẽ thấp hơn khoảng 95% (rủi ro lệch dưới), vì đáy thấp bất thường chỉ xảy ra một phía.
- Điểm gốc 11/2010 là ngoại suy từ 26 ngày; đã dùng trung bình 10–11/2010 (~864 kWh/tháng).
- Số liệu của một hộ, quan sát — không suy ra nguyên nhân (thời tiết, người ở, thiết bị). `Global_active_power` đo tổng, không tách thiết bị.
