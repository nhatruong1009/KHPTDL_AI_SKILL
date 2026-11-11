# Leo Everest có an toàn hơn theo thời gian không?

## Trả lời ngắn
**Có, nhưng không đồng đều.** Tỉ lệ tử vong trên mỗi lượt tham gia giảm gần một nửa từ trước 1990 đến 1990–2019:

| Nhóm | 1950–1989 | 1990–2019 | Thay đổi |
|---|---|---|---|
| Thành viên đoàn | 18,7 ‰ (54/2.884) | 10,4 ‰ (128/12.320) | −44% (OR 0,55; p<0,001) |
| Nhân viên được thuê | 18,4 ‰ (42/2.288) | 6,7 ‰ (68/10.211) | −64% (OR 0,36; p<0,001) |

(‰ = số ca tử vong trên 1.000 lượt tham gia. Khoảng tin cậy 95% xem trong `MAIN_death_rate_expedition_level.csv`.)

- **Trước 1990 hai nhóm có rủi ro như nhau** (18,7‰ và 18,4‰, p = 1,0). Từ 1990 nhân viên thuê thấp hơn (OR 0,64; p = 0,003).
- **Theo thập kỷ** (biểu đồ `death_rate_by_decade.png`): thành viên 20,2‰ (1980s) → 14,4 → 9,6 → 8,6 (2010s). Nhân viên thuê 19,8‰ (1980s) → 10,6 → **2,7** (2000s) → 7,8 (2010s).
- **Thập niên 2010 là bước lùi cho nhân viên thuê**, gần như do một sự kiện: lở tuyết Khumbu Icefall năm 2014 và động đất 2015. Hai năm này có 28/744 nhân viên thuê tử vong (37,6‰) so với 3/922 thành viên (3,3‰); riêng 2014 là 17/300. Bỏ 2014–2015, tỉ lệ nhân viên thuê 1990–2019 là 4,2‰, còn thành viên là 11,0‰.
- **Thay đổi trong kỷ nguyên thương mại**: số lượt tham gia tăng vọt (từ ~3.000 lượt/thập kỷ vào 1980s lên ~10.000 lượt vào 2010s, `participants_by_decade.png`). Nhân viên thuê từ chỗ ít hơn thành viên ở mỗi đoàn nay đông gần bằng (5.109 so với 4.980 ở 2010s). Họ làm công việc rủi ro khác nhau: từ 1990, 33 trên 68 ca tử vong của họ do lở tuyết, còn thành viên chủ yếu chết do ngã, say độ cao (AMS), kiệt sức, hạ thân nhiệt (`death_causes_since1990.csv`).

## Phương pháp
- Dữ liệu: Himalayan Database (`expeditions.csv`, `members.csv`), đỉnh Everest, 1950–2019 (xuất phát điểm 1950 vì trước đó ít lượt).
- Tỉ lệ = số tử vong / số lượt tham gia (một người đi hai đoàn tính hai lượt), tính theo cột cấp đoàn `members`, `member_deaths`, `hired_staff`, `hired_staff_deaths`. Khoảng tin cậy Wilson 95%; so sánh bằng kiểm định Fisher.
- Mã: `analysis.py` (khám phá + đối chiếu), `analysis_main.py` (kết quả chính, biểu đồ).

## Lưu ý quan trọng
1. **Bảng `members` ghi thiếu nhân viên thuê**: so với tổng `hired_staff` ở bảng `expeditions`, bảng `members` chỉ phủ 7% (1960s–1970s), 14% (1980s), 29% (1990s), 61% (2000s), 75% (2010s) (`hired_coverage_check.csv`). Số ca tử vong của hai bảng khớp nhau (186 và 120), nên nếu dùng bảng `members` làm mẫu số thì tỉ lệ tử vong của nhân viên thuê trước 1990 bị thổi phồng (ví dụ 365‰ ở 1970s, gấp 15 lần), và kết luận "nhân viên thuê nguy hiểm gấp 8 lần" là **sai**. Tôi dùng mẫu số cấp đoàn; kết quả theo bảng `members` lưu ở các file `alt_*` và `death_rate_by_decade_group.csv` chỉ để đối chiếu.
2. Mẫu số cấp đoàn vẫn có thể không chính xác ở các đoàn cũ (nhân viên ghi nhận "đi lên trên trại căn cứ"). Khoảng tin cậy ở 1950s–1960s rất rộng, không nên đọc xu hướng trước 1970.
3. Đây là dữ liệu quan sát: giảm tỉ lệ tử vong có thể do thiết bị, dự báo thời tiết, dây cố định, oxy, đoàn chuyên nghiệp hơn, hoặc thay đổi cách ghi chép; dữ liệu không tách được nguyên nhân.
4. Tỉ lệ tính theo lượt tham gia, không tính theo thời gian ở trên núi hay theo độ cao đạt được. Số lượt leo lên đỉnh tăng (tỉ lệ thành công của thành viên từ ~7% lên ~52%), nên không so sánh được "rủi ro mỗi lần lên đỉnh" ở đây.
5. Dữ liệu dừng ở mùa xuân 2019; không gồm 2020 trở đi.
6. Số ca tử vong ở nhóm nhỏ (thập kỷ trước 1970) quá ít để kết luận.
