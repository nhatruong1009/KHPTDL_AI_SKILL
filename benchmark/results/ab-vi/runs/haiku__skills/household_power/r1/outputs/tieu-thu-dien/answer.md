# Tiêu thụ điện năng của hộ gia đình: xu hướng, mùa vụ, bất thường và dự báo tháng 12/2010

## Trả lời ngắn

- **Xu hướng:** Gần như đi ngang. So cùng kỳ tháng 1–10, mức trung bình là 25,14 (2007), 24,52 (2008), 24,69 (2009) và 25,09 (2010) kWh/ngày, chênh lệch dưới 3%. Không thấy tăng hay giảm bền vững.
- **Mùa vụ:** Mạnh theo mùa. Tháng 1 cao hơn trung bình năm 32%, tháng 12 cao hơn 27%. Tháng 7–8 thấp nhất (chỉ số 0,64 và 0,47). Theo tuần, thứ Bảy và Chủ Nhật cao hơn các ngày trong tuần, khoảng 29–30 so với 23–26 kWh/ngày. Theo giờ, đỉnh lúc 20:00 (1,90 kW trung bình) và đáy lúc 04:00 (0,44 kW).
- **Bất thường:** Khoảng trống dữ liệu là 25.979 phút (1,25%), tập trung ở 9 khoảng trống từ 1 giờ trở lên. Khoảng dài nhất là 17–22/08/2010 (120 giờ). Tháng 8/2008 có mức tiêu thụ rất thấp (6,6 kWh/ngày, chỉ bằng 1/4 bình thường) do hộ có thể vắng nhà, và đây là bất thường lớn nhất trong dữ liệu. Các tuần bất thường khác: tuần 17/08/2008 và 24/08/2008 (thấp), tuần kết thúc 31/12/2006 (cao, Tết dương lịch).
- **Dự báo tổng điện năng tháng 12/2010:** khoảng **1.023 kWh** (≈33,0 kWh/ngày). Khoảng 90%: **820–1.247 kWh**.

## Dữ liệu và phạm vi

- File: `data/household_power_consumption.txt`, 2.075.259 dòng, đo theo phút, từ **16/12/2006 17:24** đến **26/11/2010 21:02**. Khác với đề bài, dữ liệu không kéo đến hết tháng 11/2010. Tháng 12/2010 không có dữ liệu nào, nên đây là dự báo ngoài mẫu.
- Chỉ dùng `Global_active_power` (kW). Các giá trị thiếu (`?`) xuất hiện đồng thời ở mọi cột, nên không có khoảng trống một phần.
- Đơn vị: kWh/ngày = 24 × công suất trung bình (kW) trên các phút có dữ liệu. Cách này không bị lệch khi một ngày có thiếu vài phút.
- Ngày có dưới 50% phút dữ liệu bị loại khỏi phân tích ngày/tuần/tháng (20 ngày). Tháng 12/2006 (từ ngày 16) và tháng 11/2010 (đến ngày 26) là tháng bị cắt.

## Phát hiện chi tiết

### 1. Xu hướng
- Trung bình ngày theo tháng trên toàn giai đoạn có xu hướng giảm (OLS −0,048 kWh/ngày mỗi tháng), nhưng kết quả này bị nhiễu bởi mùa vụ và tháng bị cắt nên **không dùng để kết luận**.
- So cùng kỳ tháng 1–10 (loại tháng bị cắt): tỉ lệ so với 2007 là 0,975 (2008), 0,982 (2009) và 0,998 (2010). Mức giảm nhẹ 2008–2009 gắn với tháng 8/2008 bất thường; năm 2010 gần bằng 2007.
- Tháng 12 có giá trị lần lượt 39,0 (2007), 30,6 (2008), 32,7 (2009) kWh/ngày. Năm 2008 thấp hơn 2007 khá nhiều, nhưng dữ liệu không đủ để nói nguyên nhân (thời tiết, hành vi, thiết bị).

### 2. Mùa vụ
- **Theo tháng** (chỉ số, 1 = TB năm): T01 1,32; T02 1,18; T03 1,13; T04 1,00; T05 0,94; T06 0,86; T07 0,64; T08 0,47; T09 0,88; T10 1,03; T11 1,18; T12 1,27. Mùa đông cao, mùa hè thấp. Chỉ số tháng 8 bị kéo xuống bởi giai đoạn vắng nhà năm 2008.
- **Theo thứ** (kWh/ngày, TB): T2 24,0; T3 25,7; T4 26,0; T5 23,5; T6 25,0; **T7 29,9**; **CN 29,3**. Cuối tuần cao hơn ngày thường khoảng 4–5 kWh/ngày.
- **Theo giờ:** Công suất trung bình thấp nhất lúc 04:00 (0,44 kW) và cao nhất lúc 20:00 (1,90 kW). Xem `bieu_do_heatmap_thu_gio.png` để thấy chi tiết theo thứ.

### 3. Bất thường
- **Khoảng trống dữ liệu** (phút thiếu liên tục, đã kiểm tra trong `khoang_trong_du_lieu.csv`):

  | Từ | Đến | Số giờ |
  |---|---|---|
  | 17/08/2010 21:02 | 22/08/2010 21:27 | 120 |
  | 25/09/2010 03:56 | 28/09/2010 19:12 | 87 |
  | 28/04/2007 00:21 | 30/04/2007 14:23 | 62 |
  | 13/06/2009 00:30 | 15/06/2009 07:34 | 55 |
  | 12/01/2010 14:53 | 14/01/2010 19:01 | 52 |
  | 20/03/2010 03:52 | 21/03/2010 13:38 | 34 |

  Các khoảng này tập trung vào 2010, nên các tháng 8, 9/2010 có ít ngày hơn bình thường.
- **Giai đoạn thấp bất thường (08/2008):** Từ 06 đến 30/08/2008, công suất nền ổn định quanh 0,19 kW, công tơ 1 và 2 (bếp, máy giặt) gần như bằng 0. Đây là dấu hiệu hộ vắng nhà thay vì lỗi cảm biến. Từ 31/08/2008 mức tiêu thụ tăng trở lại.
- **Tuần bất thường** (|z| > 2,5, z dựa trên trung vị và MAD): 17/08/2008 (z = −2,7), 24/08/2008 (z = −2,7) và tuần kết thúc 31/12/2006 (z = +2,6).
- **Ngày cao bất thường** (|z| > 3 trong cùng thứ, 12 ngày): chủ yếu tập trung vào mùa đông 12/2006–02/2007 (đỉnh 79,6 kWh vào 23/12/2006) và 11/2008. Các ngày này nằm trong mùa cao, nhưng cụm này chưa đủ để kết luận về nguyên nhân.

### 4. Dự báo tháng 12/2010
- **Phương pháp:** kWh/ngày tháng 12/2010 = TB kWh/ngày tháng 12/2009 × tỉ lệ YoY. Tỉ lệ YoY = tổng TB ngày tháng 1–11/2010 chia cho cùng kỳ 2009 (= 1,008). Tháng 12/2009 = 32,75 kWh/ngày → dự báo 32,99 kWh/ngày × 31 ngày = **1.023 kWh**.
- **Kiểm thử ngược:** Áp dụng đúng phương pháp này cho 24 tháng trong 2008–2010 (bỏ tháng 8/2008 và 8/2009). MAPE = 10,7%. Phân phối sai số log: 5% = −0,222, 95% = +0,198.
- **Khoảng 90%:** 1.023 × exp(−0,222) đến 1.023 × exp(+0,198) = **820–1.247 kWh**. Khoảng chuẩn lognormal cho kết quả gần như tương tự (816–1.283).
- **Độ nhạy theo mùa đông:** Chỉ dùng 8 tháng 10–2 trong kiểm thử, khoảng 90% là 834–1.113 kWh (sai số nhỏ hơn, nhưng mẫu chỉ có 8 tháng nên chưa chắc chắn).

## Phương pháp

1. Gộp hai cột ngày và giờ thành dấu thời gian; kiểm tra trùng lặp (không có) và thứ tự (đã sắp xếp).
2. Tính kWh/ngày bằng 24 × TB kW; loại ngày phủ dưới 50%.
3. Tổng hợp theo tháng, tuần, thứ và giờ.
4. Xu hướng bằng so sánh cùng kỳ tháng 1–10 giữa các năm.
5. Phát hiện bất thường bằng z robust (trung vị và MAD) theo tuần và theo thứ trong tuần.
6. Dự báo bằng YoY ratio; sai số và khoảng bất định lấy từ kiểm thử ngược.

Mã nguồn: `outputs/tieu-thu-dien/analysis.py`. Các CSV và PNG nằm trong cùng thư mục.

## Hạn chế

- **Quan sát, không phải nhân quả.** Mùa vụ và mức giảm 2008 cho thấy tương quan, không chứng minh nguyên nhân.
- **Một hộ gia đình.** Kết quả không đại diện cho các hộ khác.
- **Không có dữ liệu thời tiết.** Tháng 12 phụ thuộc mạnh vào nhiệt độ; dự báo không tính đến điều này. Nếu năm 2010 có mùa đông lạnh bất thường, sai số có thể vượt khoảng dự báo.
- **Mẫu kiểm thử nhỏ.** 24 tháng (và 8 tháng mùa đông) cho ước lượng sai số thô. Khoảng 90% nên xem là ước lượng gần đúng.
- **Đầu ra của tháng 12/2010 là ước tính, không phải số đo.** Dữ liệu dừng ở 26/11/2010.
