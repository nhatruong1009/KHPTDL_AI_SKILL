# Điện năng tiêu thụ hộ gia đình 12/2006 – 11/2010 và dự báo tháng 12/2010

## Trả lời ngắn
- **Xu hướng:** gần như đi ngang. Trung bình 12 tháng liên tiếp dao động 25,7–26,5 kWh/ngày. Xu hướng sau khi khử mùa vụ là −0,9%/năm (p = 0,35), nên không có ý nghĩa thống kê.
- **Mùa vụ:** mạnh nhất theo năm, rồi theo ngày. Theo tuần thì có nhưng nhẹ.
  - Theo năm: mùa đông cao (T1 = 1,37 lần mức trung bình năm), mùa hè thấp (T8 = 0,63 lần).
  - Theo ngày: đỉnh sáng khoảng 7–8h và đỉnh tối khoảng 20–21h (~1,9 kW).
  - Theo tuần: cuối tuần dùng nhiều hơn ngày thường (29,6 so với 24,8 kWh/ngày, p < 0,001).
- **Giai đoạn bất thường:**
  - Tháng 8/2008 chỉ còn 6,6 kWh/ngày (205,7 kWh cả tháng, khoảng một phần tư mức thường). Đây là bất thường lớn nhất, có thể là cả nhà vắng, nhưng dữ liệu không xác nhận.
  - Có 71 khoảng trống dữ liệu, tổng 25.979 phút (1,25%). Dài nhất là ~5 ngày (17–22/8/2010), rồi ~3,6 ngày (25–28/9/2010) và ~2,6 ngày (28–30/4/2007).
  - Nhiều tuần thấp lẻ tẻ (xem dưới).
- **Dự báo tổng điện năng T12/2010: ≈ 1.052 kWh** (≈ 33,9 kWh/ngày).
  - Khoảng 80%: 916–1.209 kWh.
  - Khoảng 95%: 848–1.306 kWh.

## Bằng chứng
**Xu hướng** (`nam_kwh_ngay.csv`, `cungky_T1_T11.csv`, `xu_huong.csv`)

| Giai đoạn | kWh/ngày |
|---|---|
| 12/2007–11/2008 | 26,46 |
| 12/2008–11/2009 | 25,69 |
| 12/2009–11/2010 | 26,04 |

- Cùng kỳ T1–T11 (bỏ T8/2008): 2007 = 25,68; 2008 = 27,19; 2009 = 25,24; 2010 = 25,43.
- Chênh lệch giữa các năm nhỏ hơn nhiều so với biên độ mùa vụ (T7–T8 ≈ 15 so với T1 ≈ 34).

**Mùa vụ** (`mua_vu.png`, `theo_gio.csv`, `thu_trong_tuan.csv`, `chi_so_mua.csv`)
- Ngày thường đỉnh lúc 7h (1,72 kW) và 21h (1,86 kW). Cuối tuần không có đỉnh sáng sớm mà dùng đều và cao suốt ban ngày (~1,4–1,5 kW từ 11–15h).
- Thứ Bảy (29,9) và Chủ nhật (29,3) cao hơn các ngày còn lại (23,5–25,9 kWh/ngày).
- Chỉ số mùa theo tháng, từ T1 đến T12: 1,37; 1,22; 1,15; 0,98; 0,97; 0,85; 0,65; 0,63; 0,92; 1,07; 1,21; 1,33. Đường mùa vụ của 4 năm gần như chồng lên nhau (biểu đồ dưới của `xu_huong_bat_thuong.png`).

**Tuần bất thường** (`tuan_bat_thuong.csv`)
- Cách làm: so kWh/ngày của từng tuần với trung vị các tuần cùng thời điểm (±2 tuần) của các năm khác. Gắn cờ khi robust z > 3, và chỉ xét tuần có độ phủ dữ liệu ≥ 90%.
- Tuần thấp bất thường:
  - T8/2008, 4 tuần liên tiếp (tuần kết thúc 10/8, 17/8, 24/8 và 31/8/2008), chỉ 4,4–8,6 kWh/ngày so với kỳ vọng 15–20.
  - Tuần đầu tháng 3 (kết thúc 4/3/2007, 2/3/2008, 7/3/2010) ở mức ~13–17 kWh/ngày.
  - Tuần kết thúc 15/4/2007, 24/6/2007, 4/11/2007, 2/11/2008, 22/2/2009 và các tuần tháng 8/2009 và 2010.
  - Dữ liệu không cho biết nguyên nhân, nhiều khả năng là tuần vắng nhà hoặc kỳ nghỉ.
- Tuần cao bất thường: tuần cuối năm 2006 và 2007 (kết thúc 31/12/2006 và 30/12/2007, 45–47 kWh/ngày so với kỳ vọng ~33). Tuần 8/2007 cũng cao hơn kỳ vọng.
- Khoảng trống dữ liệu: các tuần có độ phủ < 90% được tách riêng (cột `co_khoang_trong`) và không bị gắn nhãn bất thường. Chúng gồm tuần đầu (16/12/2006, chỉ có từ 17h24), cuối tháng 4/2007, tháng 6/2009, tháng 1/2010, tháng 3/2010, tháng 8–9/2010 và tuần cuối cùng của dữ liệu.

**Dự báo** (`du_bao_T12_2010.csv`, `backtest_*.csv`, `du_bao_T12_2010.png`)
- Mô hình chọn: trung bình hình học kWh/ngày của T12 các năm trước (2007, 2008, 2009), nhân với 31 ngày. Xu hướng gần như bằng 0 nên không cần điều chỉnh mức.
- Kiểm tra lùi (rolling origin, 32 tháng từ 1/2008, bỏ T8/2008 và tháng thiếu > 10% dữ liệu):

| Mô hình | MAPE | Độ lệch chuẩn log sai số |
|---|---|---|
| Seasonal naive (năm trước) | 9,0% | 0,117 |
| Trung bình các năm (mô hình chọn) | 8,3% | 0,106 |

  Mô hình có hiệu chỉnh mức theo 12 tháng gần nhất có MAPE 9,0% trên 16 tháng, không tốt hơn.
- Khoảng bất định là điểm dự báo × exp(±t·0,106), với t lấy từ phân phối t-student, n−1 = 31 bậc tự do.
- Đối chiếu bằng các cách khác: T12/2009 lặp lại = 1.015; T11/2010 × tỉ lệ T12/T11 trung bình = 964; có hiệu chỉnh mức = 1.139. Cả ba đều nằm trong khoảng 80%.

## Phương pháp
- Quy đổi kWh = Global_active_power (kW, trung bình mỗi phút) / 60, rồi cộng theo phút. Giá trị thiếu ('?') giữ là NaN, không điền bằng 0.
- Tháng và tuần thiếu dữ liệu được quy về kWh/ngày theo số phút có dữ liệu. Tổng tháng "hiệu chỉnh" = kWh/ngày × số ngày của tháng.
- Mã nguồn: `prep.py` rồi `analysis.py` (chỉ dùng pandas, numpy, scipy, matplotlib).

## Giả định và hạn chế
1. Dữ liệu kết thúc lúc 21:02 ngày 26/11/2010, nên T11/2010 chỉ có 25,9 ngày và T12/2010 hoàn toàn là dự báo. T12/2006 cũng chỉ có từ 16/12.
2. Dự báo chỉ dựa trên 3 mùa T12 (39,0; 30,6; 32,7 kWh/ngày). T12/2007 cao rõ rệt so với hai năm sau, nên điểm dự báo (33,9 kWh/ngày) bị kéo lên bởi năm này. Nếu coi T12/2007 là ngoại lệ thì ~1.015 kWh hợp lý hơn.
3. Khoảng bất định đo từ sai số lùi trên 32 tháng, nên chưa phản ánh hết rủi ro nhảy vọt hiếm gặp như T8/2008. Nếu gia đình vắng nhà một phần tháng 12/2010, tổng có thể thấp hơn khoảng 95%. Ngược lại, tuần cuối năm hay cao (xem trên).
4. "Bất thường" chỉ là lệch thống kê so với các năm khác; không rõ nguyên nhân. Dữ liệu chỉ phản ánh mối liên hệ chứ không chứng minh nhân quả.
5. Global_active_power chỉ là điện năng đo tại đồng hồ chính. Phần không thuộc 3 nhánh đo phụ không được phân tách trong phân tích này.
