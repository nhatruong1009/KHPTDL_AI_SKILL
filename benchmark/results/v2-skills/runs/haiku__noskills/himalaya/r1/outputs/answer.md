# Everest có an toàn hơn theo thời gian không?

**Trả lời ngắn:** Có. Tỉ lệ tử vong trên Everest giảm mạnh sau năm 1990, nhưng mức giảm khác nhau giữa khách leo và nhân viên được thuê, và nhân viên vẫn chịu rủi ro cao do các sự kiện lớn.

## Kết quả chính

Tỉ lệ tính trên 1.000 người tham gia (dữ liệu expedition-level, Everest, 1921–2019; 2.149 chuyến, 15.281 thành viên đoàn, 12.741 nhân viên được thuê).

| Thập kỷ | Thành viên: tử vong /1.000 | Nhân viên được thuê: tử vong /1.000 | Số thành viên | Số nhân viên |
|---|---|---|---|---|
| 1920s | 90,9 | 109,9 | 33 | 91 |
| 1930s | 23,3 | 0,0 | 43 | 149 |
| 1950s | 0,0 | 7,2 | 107 | 139 |
| 1960s | 21,7 | 5,6 | 184 | 359 |
| 1970s | 16,3 | 24,4 | 613 | 778 |
| 1980s | 20,2 | 19,8 | 1.980 | 1.012 |
| 1990s | 14,4 | 10,6 | 2.980 | 1.800 |
| 2000s | 9,6 | 2,7 | 4.360 | 3.302 |
| 2010s | 8,6 | 7,8 | 4.980 | 5.109 |

Các thập kỷ 1920s–1940s có rất ít chuyến leo (1–5 chuyến mỗi thập kỷ), nên tỉ lệ rất dao động; không nên đọc quá nhiều vào các con số này.

Theo giai đoạn lớn:

| Giai đoạn | Thành viên /1.000 | Nhân viên /1.000 | Tổng /1.000 |
|---|---|---|---|
| Trước 1990 (204 chuyến) | 19,6 (58/2.961) | 20,6 (52/2.530) | 20,0 |
| Từ 1990 (1.945 chuyến) | 10,4 (128/12.320) | 6,7 (68/10.211) | 8,7 |

Ước lượng thô (xấp xỉ chuẩn trên log tỉ số): tỉ lệ tử vong thành viên trước 1990 cao hơn sau 1990 khoảng 1,9 lần (KTC 95% ~1,4–2,6); của nhân viên cao hơn khoảng 3,1 lần (KTC 95% ~2,2–4,4). Ước lượng này không tính đến việc các giai đoạn khác nhau về số chuyến và điều kiện leo.

## Điều gì đã thay đổi trong kỷ nguyên thương mại?

1. **Rủi ro chung giảm.** Tỉ lệ tử vong tổng thể giảm từ khoảng 20 xuống khoảng 9 trên 1.000 người tham gia.
2. **Khách leo được hưởng lợi nhiều nhất về tỉ lệ.** Trước 1990, khách và nhân viên có tỉ lệ tương đương (~20). Sau 1990, tỉ lệ của khách giảm còn ~10, còn của nhân viên còn ~7.
3. **Nhân viên được thuê trong thập kỷ 2000 có tỉ lệ rất thấp (2,7)** nhưng thập kỷ 2010 tăng lên 7,8 do hai năm 2014 (17 người) và 2015 (11 người). Bỏ hai năm này, tỉ lệ 2010s của nhân viên khoảng 2,8/1.000 (12 ca / 4.365 người). Rủi ro của nhân viên vì vậy tập trung vào các sự kiện hiếm nhưng nghiêm trọng (thác băng Khumbu, động đất), không phải đều đặn.
4. **Nguyên nhân tử vong thay đổi.** Trong kỷ nguyên thương mại, thành viên đoàn chết nhiều nhất vì ngã (31), bệnh độ cao AMS (24), kiệt sức (23) và lạnh/cóng (17). Nhân viên được thuê chết chủ yếu vì tuyết lở (33/68 ca sau 1990; 23/52 ca trước 1990) và thác băng (Icefall collapse: 10 ca trước 1990, 3 ca sau 1990) (xem `outputs/nguyen_nhan_tu_vong.csv`). Trước 1990, nhân viên chiếm gần một nửa số ca tử vong (52/110). Thành viên đoàn sau 1990: 78/128 ca do ngã (31), AMS (24) và kiệt sức (23).
5. **Quy mô thay đổi:** số thành viên trung bình mỗi chuyến giảm từ ~14,5 xuống ~6,3, trong khi số chuyến tăng gần 10 lần. Đây là mô tả, chưa phải nguyên nhân.

## Phương pháp

- Lọc `peak_id == "EVER"` từ `expeditions.csv` (2.149 chuyến, 1921–2019).
- Tử vong thành viên = `member_deaths`; tử vong nhân viên = `hired_staff_deaths`; mẫu số = `members` và `hired_staff` (cấp chuyến). Tỉ lệ = tử vong / mẫu số × 1.000.
- Kiểm tra chéo: tổng tử vong trong `members.csv` (306) = `member_deaths` (186) + `hired_staff_deaths` (120). Tử vong nhân viên trong `members.csv` (120) khớp với cấp chuyến.
- Không dùng `members.csv` làm mẫu số cho nhân viên vì nó chỉ chứa 6.730 nhân viên, còn cột `hired_staff` ở cấp chuyến có 12.741.
- Lưu ý: các chuyến năm 1988, 1960, 1975 và một số chuyến khác có `hired_staff = 99` (có thể là giá trị điền tạm). Loại chúng ra làm tỉ lệ nhân viên trước 1990 đổi từ 20,6 sang 23,3; kết luận không đổi.

## Hạn chế

- Dữ liệu dừng ở mùa Xuân 2019 (không có 2020 trở đi).
- Đơn vị là người-chuyến, không phải người-duy nhất; một người tham gia nhiều chuyến được đếm nhiều lần.
- `member_id` không nhất quán giữa các chuyến nên không thể theo dõi từng người.
- Số nhân viên trong dữ liệu chỉ tính những người đi trên trại căn cứ; nhân viên trên trại căn cứ không được tính, nên tỉ lệ nhân viên có thể bị ước lượng quá cao hoặc thấp.
- Tương quan với thời gian không chứng minh nguyên nhân (công nghệ, oxy, lộ trình cố định, quy định, huấn luyện đều thay đổi cùng lúc).

## Tệp đầu ra

- `outputs/story.md`: data story cho công chúng phổ thông.
- `outputs/bieu_do_ti_le_tu_vong.png`: biểu đồ tỉ lệ tử vong theo thập kỷ (đường chia 1990).
- `outputs/theo_thap_ky.csv`, `theo_ky_nguyen.csv`, `theo_giai_doan.csv`, `theo_nam.csv`, `nguyen_nhan_tu_vong.csv`: bảng số liệu.
- `outputs/analysis_log.txt`: nhật ký chạy phân tích.
- `scripts/`: mã phân tích và vẽ biểu đồ.

## Ghi chú về công cụ

Biểu đồ dùng bảng màu hai màu (xanh dương `#2a78d6` và cam `#eb6834`) lấy từ slot 1 và 2 của `references/palette.md` theo kỹ năng dataviz. Lệnh `validate_palette.js` bị từ chối quyền chạy trong phiên này nên chưa kiểm chứng lại bằng script; cặp màu này nằm trong bảng màu đã được xác nhận trong tài liệu.
