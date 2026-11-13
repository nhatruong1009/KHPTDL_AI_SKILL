# Câu chuyện điện năng của một hộ gia đình, 2006–2010

Trong gần bốn năm, một hộ gia đình ghi lại điện năng mỗi phút. Dữ liệu cho thấy nhịp sống của gia đình: mùa đông tiêu thụ nhiều, mùa hè ít, cuối tuần sôi động hơn, và vài đợt "im lặng" khi cả nhà đi vắng.

## Nhịp năm: mùa đông đốt điện, mùa hè thở nhẹ

Tháng 12 và tháng 1 là đỉnh, trung bình khoảng 35–36 kWh mỗi ngày. Đến tháng 7 và 8, mức này tụt xuống còn 14–17 kWh. Hình dạng này lặp lại đều đặn qua các năm 2007, 2008, 2009 và 2010. Xem `outputs/chart_mua_vu_theo_nam.png`.

## Nhịp tuần: cuối tuần ấm hơn

Thứ Bảy và Chủ nhật trung bình khoảng 30 kWh mỗi ngày, cao hơn các ngày trong tuần (23–26). Thứ Năm là ngày yên nhất. Nhịp này phản ánh một gia đình sinh hoạt tại nhà vào cuối tuần.

## Nhịp ngày: đêm lặng, tối đông

Từ 3 đến 5 giờ sáng, cả nhà ngủ và công suất chỉ khoảng 0,44 kW. Buổi sáng lúc 7 giờ có một đỉnh nhỏ. Đỉnh lớn nhất đến lúc 20 giờ, khoảng 1,9 kW, khi cả nhà ở nhà và dùng điện nhiều nhất trong ngày. Xem `outputs/chart_tuan_gio.png`.

## Xu hướng: nhẹ nhàng đi xuống

Mức tiêu thụ trung bình hàng năm gần như đi ngang: 26,8 kWh/ngày năm 2007, khoảng 25–26 kWh/ngày trong 2008–2010. Nếu tính trên tháng, xu hướng giảm khoảng 0,66 kWh/ngày mỗi năm, tức khoảng 2–3% mỗi năm. Đó là mức giảm vừa phải, chưa phải thay đổi lớn về thói quen.

## Những "khoảnh khắc lạ" trong dữ liệu

- **Tuần đầu tháng 3/2007:** nhà gần như im ắng, khoảng 8–9 kWh mỗi ngày trong một tuần. Từ 4/3, điện tăng vọt lên 35–58 kWh mỗi ngày. Có thể là một chuyến đi xa rồi trở về, nhưng đây là suy đoán.
- **Tháng 8/2008:** giai đoạn im lặng dài nhất, kéo dài gần ba tuần với khoảng 4–6 kWh mỗi ngày. Chỉ còn tủ lạnh và vài thiết bị chạy nền. Ngày 31/8, nhà lại sáng đèn với khoảng 25 kWh. Giai đoạn này khớp với một kỳ nghỉ dài, nhưng chưa được xác nhận.
- **Tháng 8/2010:** nửa đầu tháng thấp, sau đó tăng lên từ ngày 15. Từ 17 đến 22/8 có một khoảng mất dữ liệu gần năm ngày.
- **Các khoảng trống dữ liệu:** 9 khoảng dài hơn một giờ, dài nhất gần năm ngày (17–22/8/2010). Đây là sự cố ghi nhận, không phải hành vi của gia đình, nên cần tách riêng khi đọc dữ liệu. Xem `outputs/chart_xu_huong_ngay.png`.

## Nhìn về tháng 12/2010

Dữ liệu dừng ở 26/11/2010, nên tháng 12/2010 chưa có số liệu. Dựa trên mùa đông các năm trước và xu hướng nhẹ, dự báo tổng điện tháng 12/2010 là **khoảng 1.030 kWh** (khoảng 33 kWh mỗi ngày). Khoảng 80% là 910–1.170 kWh. Kiểm định ngược cho thấy mô hình sai lệch đáng kể ở năm 2008 (33%) nên khoảng thực tế rộng hơn, khoảng 800–1.300 kWh. Xem `outputs/chart_du_bao_12_2010.png`.

## Điều rút ra

Điện của gia đình này chủ yếu do mùa và lịch sinh hoạt quyết định. Các giai đoạn vắng nhà thể hiện rất rõ, và có thể phát hiện chúng ngay từ dữ liệu. Muốn dự báo chính xác hơn cần thêm dữ liệu nhiệt độ và thêm thông tin về những lần vắng nhà.
