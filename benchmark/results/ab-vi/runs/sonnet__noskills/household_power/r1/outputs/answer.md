# Điện năng tiêu thụ hộ gia đình, 12/2006 – 11/2010

**Kết luận chính:** không có xu hướng tăng/giảm dài hạn; mức tiêu thụ do mùa vụ chi phối (mùa đông gấp ~2,5 lần mùa hè). **Dự báo tổng điện năng tháng 12/2010 ≈ 1.040 kWh (khoảng 80%: 914–1.184; khoảng 95%: 849–1.274).**

## Dữ liệu và cách xử lý
- 2.075.259 phút (16/12/2006 17:24 → 26/11/2010 21:02); **25.979 phút (1,25%) thiếu giá trị** (ký hiệu `?`).
- Điện năng (kWh) = `Global_active_power` (kW) / 60 mỗi phút. Ngày có độ phủ <90% bị loại; tháng thiếu được hiệu chỉnh theo trung bình ngày hợp lệ × số ngày trong tháng.
- Dữ liệu **kết thúc 26/11/2010**, nên tháng 11/2010 chưa đủ và tháng 12/2010 hoàn toàn là dự báo. Tháng 12/2006 chỉ có từ ngày 16 nên không dùng khi học mô hình.

## Xu hướng
- Trung bình/ngày: 2007 = 26,8; 2008 = 25,7; 2009 = 25,9; 2010 = 25,4 kWh/ngày (2006 = 45,1 chỉ là nửa cuối tháng 12, mùa cao điểm).
- Tổng năm hiệu chỉnh: 2007 ≈ 9.771; 2008 ≈ 9.418 (gồm tháng 8 vắng nhà); 2009 ≈ 9.427 kWh. 12 tháng gần nhất (12/2009–11/2010) so với 12 tháng trước: **+1,3%**; 1–11/2010 so với 1–11/2009: **+0,6%**. Tức là đi ngang, thấp hơn 2007 một chút.

## Tính mùa vụ
- **Theo ngày:** thấp nhất 3–5 giờ sáng (~0,44 kW); đỉnh sáng 7–8 giờ (~1,5 kW); đỉnh lớn nhất buổi tối 20–21 giờ (~1,9 kW). Ngày thường có đỉnh sáng rõ (1,72 kW lúc 7 giờ) và trũng buổi chiều; cuối tuần dùng đều hơn ban ngày (~1,4–1,5 kW lúc 11–17 giờ).
- **Theo tuần:** thứ 7 (29,9) và Chủ nhật (29,3 kWh/ngày) cao hơn ngày thường (23,5–26,0) khoảng 15–25%.
- **Theo năm:** rất mạnh, đỉnh tháng 12–1 (~35 kWh/ngày), đáy tháng 7–8 (~14–17). Hình dạng lặp lại ở cả 3 năm đầy đủ.

## Giai đoạn bất thường
**Khoảng trống dữ liệu ≥1 giờ (9 đoạn):**

| Bắt đầu | Thời lượng |
|---|---|
| 28/04/2007 00:21 | 62,1 giờ |
| 15/07/2007 16:49 | 1,4 giờ |
| 10/12/2008 10:48 | 1,2 giờ |
| 13/06/2009 00:30 | 55,1 giờ |
| 13/08/2009 05:00 | 14,9 giờ |
| 12/01/2010 14:53 | 52,2 giờ |
| 20/03/2010 03:52 | 33,8 giờ |
| **17/08/2010 21:02** | **120,4 giờ (dài nhất)** |
| 25/09/2010 03:56 | 87,3 giờ |

62 đoạn còn lại đều <1 giờ. Các khoảng trống dài tập trung ở 2009–2010.

**Tuần bất thường** (lệch >3 độ lệch chuẩn robust so với đường nền trung vị 9 tuần; 23 tuần):
- **Thấp nghiêm trọng nhất – tháng 8/2008:** các tuần kết thúc 10/8, 17/8, 24/8, 31/8/2008 chỉ 30–60 kWh/tuần so với nền ~107 (trung bình tháng 8/2008 chỉ 6,6 kWh/ngày – nhiều khả năng cả nhà đi vắng). Tương tự nhưng nhẹ hơn: đầu tháng 8/2009 và 8/2010.
- Các tuần thấp lẻ tẻ: 4/3/2007, 15/4/2007, 24/6/2007, 4/11/2007, 2/3/2008, 2/11/2008, 22/2/2009, 7/3/2010 (có thể là tuần vắng nhà ngắn).
- **Tuần cao bất thường:** tuần kết thúc 30/12/2007 (317 kWh, dịp lễ cuối năm) và 24/10/2010 (235 kWh).

## Dự báo tháng 12/2010
- **Mô hình:** trung bình log của tháng 12 các năm trước (2007: 1.210; 2008: 949; 2009: 1.015 kWh) cộng độ lệch mức của 12 tháng gần nhất so với mùa vụ (−1,2%) → **1.040 kWh** (≈33,5 kWh/ngày).
- **Khoảng bất định:** hiệu chỉnh từ backtest 26 tháng (10/2008–11/2010, mỗi tháng chỉ dùng dữ liệu trước đó): MAPE 7,3%, độ lệch chuẩn log-sai số 0,096; phân phối t. Kết quả **80%: 914–1.184; 95%: 849–1.274 kWh.**
- **Lưu ý:** (1) chỉ có 3 tháng 12 để học, tháng 12/2007 cao hơn hẳn nên điểm dự báo có thể hơi cao (tháng 12/2008–2009 chỉ ~950–1.015). (2) Rủi ro đuôi như đi vắng (tháng 8/2008) hoặc tuần lễ cuối năm cao (2007) có thể vượt khoảng 95%. (3) Không có dữ liệu thực tháng 12/2010 để đối chiếu.

## Tệp
`chart1_xuhuong_batthuong.png`, `chart2_mua_vu.png`, `chart3_dubao.png`, `monthly.csv`, `weekly.csv`, `daily.csv`, `gaps.csv`; mã: `prep.py`, `analyze.py`, `forecast.py`, `charts.py`.
