# Leo Everest có an toàn hơn theo thời gian không?

**Trả lời:** Có. Sự chênh lệch rủi ro giữa nhân viên được thuê và thành viên đoàn gần như biến mất trong kỷ nguyên thương mại.

- **Thành viên đoàn:** tử vong giảm từ 1,98% (54/2.721 lượt, 1950–1989) xuống 1,04% (128/12.285 lượt, 1990–2019), tức khoảng một nửa.
- **Nhân viên được thuê:** giảm từ 15,73% (42/267) xuống 1,07% (68/6.368), giảm mạnh hơn nhiều. Trước 1990, nhân viên thuê có nguy cơ tử vong gấp 7,9 lần (KTC 95%: 5,4–11,6) thành viên đoàn; từ 1990 tỉ lệ này là 1,03 lần (0,77–1,37; p = 0,88, không khác biệt có ý nghĩa).

## Bằng chứng
Tỉ lệ tử vong = số người chết / số lượt tham gia (mỗi dòng trong `members.csv` với `peak_id == "EVER"`).

| Thập kỷ | Thành viên: lượt / chết / % | Nhân viên thuê: lượt / chết / % |
|---|---|---|
| 1950s | 64 / 0 / 0,00 | 45 / 1 / 2,22 |
| 1960s | 145 / 4 / 2,76 | 25 / 2 / 8,00 |
| 1970s | 590 / 10 / 1,69 | 52 / 19 / 36,54 |
| 1980s | 1.922 / 40 / 2,08 | 145 / 20 / 13,79 |
| 1990s | 2.980 / 43 / 1,44 | 524 / 19 / 3,63 |
| 2000s | 4.347 / 42 / 0,97 | 2.003 / 9 / 0,45 |
| 2010s | 4.958 / 43 / 0,87 | 3.841 / 40 / 1,04 |

Biểu đồ: [chart1](chart1_ty_le_tu_vong_theo_thap_ky.png), [chart2](chart2_quy_mo_va_co_cau.png). Bảng đầy đủ kèm khoảng tin cậy: `rate_by_decade.csv`.

**Điều gì đã thay đổi từ ~1990:**
1. **Quy mô và cơ cấu:** số lượt tham gia tăng từ 2.067 (1980s) lên 8.799 (2010s), gấp khoảng 4,3 lần. Nhân viên thuê tăng từ 7,0% lên 43,7% số lượt.
2. **Xu hướng giảm vẫn có ý nghĩa thống kê sau 1990:** kiểm định xu hướng Cochran-Armitage từ 1990: nhân viên thuê z = −2,73 (p = 0,006), thành viên z = −2,33 (p = 0,02).
3. **Thành viên đoàn giảm chậm và đều** (1,44% → 0,97% → 0,87%). **Nhân viên thuê giảm vọt** (36,5% ở 1970s → 3,6% ở 1990s → 0,45% ở 2000s).
4. **Tử vong trên mỗi 100 người lên đỉnh** giảm từ 29,6 (thành viên, 1980s) xuống 1,67 (2010s), và từ 44,4 xuống 1,37 (nhân viên thuê). Tỉ lệ dùng oxy tăng từ 19% lên 62% (thành viên) và từ 45% lên 83% (nhân viên thuê). Đây chỉ là mô tả đồng thời, không chứng minh oxy là nguyên nhân.
5. **Rủi ro của nhân viên thuê tập trung vào thảm họa:** năm 2014 có 17 nhân viên thuê chết (116 lượt) và 0 thành viên; năm 2015 có 11 nhân viên thuê và 3 thành viên chết. Từ 1990, tuyết lở liên quan đến 33 ca chết nhân viên thuê (so với 10 ca thành viên). Thành viên chết chủ yếu do ngã (31), AMS (24), kiệt sức (23), lạnh/tê cóng (17).

## Kiểm tra độ nhạy (đã phản ánh ở trên)
- **Bỏ 2014–2015:** tỉ lệ 2010s của nhân viên thuê giảm từ 1,04% xuống 0,36% (12/3.340), thấp hơn thành viên (0,99%, 40/4.036). Vì vậy, việc "hết chênh lệch" ở 2010s phụ thuộc vào các thảm họa này: nhân viên thuê có rủi ro đuôi (một sự kiện làm chết hàng loạt), còn rủi ro thường lệ thấp.
- **Chỉ mùa xuân:** cùng hình dạng (`sensitivity_spring_only.csv`).
- Đối chiếu: số chết trong `members.csv` (186 thành viên + 120 thuê = 306) khớp đúng tổng `member_deaths` + `hired_staff_deaths` trong `expeditions.csv` cho Everest.

## Cách làm
- Dữ liệu: Himalayan Database (tới xuân 2019); Everest = `peak_id == "EVER"`, 21.813 lượt. Nhóm = cột `hired`; thập kỷ = `year`.
- Khoảng tin cậy Wilson 95%; tỉ số nguy cơ (RR) nhân viên thuê / thành viên kèm kiểm định Fisher; xu hướng Cochran-Armitage.
- Mã: `analysis.py`; kết quả: các file CSV cùng thư mục.

## Giả định & hạn chế
- **Mẫu nhỏ, có thể thiếu dữ liệu trước 1990:** chỉ 267 lượt nhân viên thuê trước 1990 (1970s: 52 lượt, 19 chết; KTC 24,8–50,1%). Nhân viên thuê thời đó có thể được ghi nhận chưa đầy đủ hoặc chỉ khi có sự cố (đây là suy đoán, dữ liệu không xác nhận), nên 15,7% có thể bị thổi phồng. Đọc là "cao hơn rất nhiều", không phải con số chính xác.
- **Mẫu số là lượt tham gia, không phải thời gian tiếp xúc rủi ro.** Nhân viên thuê (94% quốc tịch Nepal từ 1990) thường qua thác băng Khumbu nhiều lần mỗi mùa nhưng chỉ được đếm một lần mỗi đoàn, nên rủi ro thực có thể bị đánh giá thấp so với thành viên.
- `hired_staff` chỉ đếm người lên trên trại căn cứ; số "thành viên" có thể gồm người không lên cao.
- Dữ liệu quan sát: chỉ cho thấy mối liên hệ, không kết luận nguyên nhân (oxy, dự báo thời tiết, dây cố định...). Dữ liệu kết thúc xuân 2019.
