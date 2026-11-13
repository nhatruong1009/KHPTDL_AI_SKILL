# Leo núi Everest có an toàn hơn theo thời gian không?

**Trả lời:** Có, theo nghĩa tỉ lệ tử vong trên mỗi người leo đã giảm rõ rệt. Từ 1990 đến nay, tỉ lệ tử vong của thành viên đoàn giảm từ 19,6 xuống 10,4 ca trên 1.000 người (khoảng 0,53 lần); với nhân viên được thuê (hired staff), tỉ lệ giảm từ 20,6 xuống 6,7 ca trên 1.000 (khoảng 0,32 lần). Trước 1990, hai nhóm có tỉ lệ gần như bằng nhau (RR hired/thành viên = 1,05, không có ý nghĩa thống kê); từ 1990, nhân viên được thuê có tỉ lệ thấp hơn thành viên (RR = 0,64; p = 0,003). Tuy vậy, mức an toàn chưa ổn định: năm 2014 và 2015 chiếm 28 trên 40 ca tử vong của nhân viên được thuê trong thập kỷ 2010 (dữ liệu không ghi nguyên nhân cụ thể của hai năm này).

## Bằng chứng

**Tỉ lệ tử vong theo thập kỷ** (ca trên 1.000 người; số ca / số người trong ngoặc)

| Thập kỷ | Thành viên đoàn | Nhân viên được thuê | Nhân viên / thành viên (số người) | Dùng oxy | Lên đỉnh chính |
|---|---|---|---|---|---|
| 1950s | 0,0 (0/107) | 7,2 (1/139) | 1,30 | 44% | 22% |
| 1960s | 21,7 (4/184) | 5,6 (2/359) | 1,95 | 50% | 19% |
| 1970s | 16,3 (10/613) | 24,4 (19/778) | 1,27 | 76% | 52% |
| 1980s | 20,2 (40/1.980) | 19,8 (20/1.012) | 0,51 | 65% | 30% |
| 1990s | 14,4 (43/2.980) | 10,6 (19/1.800) | 0,60 | 70% | 51% |
| 2000s | 9,6 (42/4.360) | 2,7 (9/3.302) | 0,76 | 81% | 68% |
| 2010s | 8,6 (43/4.980) | 7,8 (40/5.109) | 1,03 | 75% | 67% |

Các thập kỷ 1920s–1940s bị loại khỏi biểu đồ vì có dưới 50 thành viên mỗi thập kỷ, khoảng tin cậy quá rộng (ví dụ 1920s: 90,9 trên 1.000, khoảng 19–243).

**Trước và sau 1990** (1921–1989 so với 1990–2019)

| Chỉ số | Trước 1990 | Từ 1990 | Tỉ số (RR) sau/trước | p |
|---|---|---|---|---|
| Thành viên: ca tử vong / 1.000 | 19,6 (58/2.961) | 10,4 (128/12.320) | 0,53 (0,39–0,72) | <0,001 |
| Nhân viên được thuê: ca / 1.000 | 20,6 (52/2.530) | 6,7 (68/10.211) | 0,32 (0,23–0,46) | <0,001 |

**Hai nhóm so với nhau** (RR nhân viên được thuê / thành viên): trước 1990 = 1,05 (0,72–1,52; p = 0,85); từ 1990 = 0,64 (0,48–0,86; p = 0,003).

**Điều gì đã thay đổi trong kỷ nguyên thương mại**
- Số đoàn leo tăng: 204 đoàn (1921–1989) so với 1.945 đoàn (1990–2019).
- Nhân viên được thuê trên mỗi thành viên tăng dần, từ 0,51 (1980s) lên 1,03 (2010s).
- Tỉ lệ đoàn lên đỉnh chính tăng từ 30% (1980s) lên khoảng 67–68% (2000s–2010s).
- Tỉ lệ đoàn dùng oxy tăng từ 65% (1980s) lên 75–81% (2000s–2010s).
- Thành phần tử vong đổi: trong 68 ca nhân viên được thuê tử vong sau 1990, 33 ca (49%) do tuyết lở (avalanche); với thành viên, 10 trên 128 ca (8%) do tuyết lở, còn phổ biến hơn là ngã (31), AMS (24) và kiệt sức (23).

**Độ nhạy:** Nếu loại 2014 và 2015 (17 + 11 ca nhân viên tử vong), thập kỷ 2010 còn 2,7 ca trên 1.000 nhân viên (12/4.365) và 9,9 trên 1.000 thành viên (40/4.058). Kết luận "nhân viên được thuê giảm mạnh" vẫn đúng, nhưng năm riêng lẻ có thể thay đổi nhiều.

Biểu đồ:
- [Tỉ lệ tử vong theo thập kỷ](chart_death_rate_by_decade.png)
- [Số đoàn leo và nhân viên được thuê trên mỗi thành viên](chart_expeditions_and_hired_ratio.png)
- [Dùng oxy và tỉ lệ lên đỉnh chính](chart_oxygen_success_by_decade.png)

## Cách tính
- Dữ liệu: `data/expeditions.csv` (lọc `peak_id == "EVER"`, 2.149 đoàn, 1921–2019) và `data/members.csv` để xem nguyên nhân tử vong.
- Mẫu số là tổng cấp đoàn: `members` và `hired_staff`. Tổng số ca tử vong cấp đoàn khớp với cấp người trong `members.csv` (186 thành viên, 120 nhân viên).
- Tỉ lệ = số ca tử vong / tổng số người tham gia (đếm mỗi người một lần cho mỗi đoàn). Khoảng tin cậy 95% là Clopper-Pearson; so sánh tỉ lệ dùng RR với khoảng Wald trên thang log và kiểm định Fisher chính xác.
- "Kỷ nguyên thương mại" được lấy theo yêu cầu là năm từ 1990 trở đi. Dữ liệu không có cột đánh dấu thương mại.
- Mã: [analysis.py](analysis.py); bảng kết quả: `mortality_by_decade.csv`, `mortality_by_era.csv`, `rate_ratio_tests.csv`, `pre_post_1990_comparison.csv`, `death_cause_by_era.csv`, `sensitivity_2010s_excl_2014_2015.csv`.

## Giả định và giới hạn
- **Mẫu số là người-đoàn, không phải người duy nhất:** cùng một người có thể được đếm ở nhiều đoàn; dữ liệu không có mã người xuyên đoàn.
- **Nhân viên được thuê có thể bị đếm thiếu:** README ghi rằng `hired_staff` là số nhân viên đi trên trại gốc. Khoảng 19% đoàn (30% trước 1990, 17% sau) ghi số nhân viên bằng 0, có thể là dữ liệu thiếu thay vì không có nhân viên. Ca tử vong của nhân viên có thể bị ghi thiếu hơn so với thành viên.
- **Thành viên trong dữ liệu:** README ghi rằng với các đoàn ở Nepal, `members` thường là số người nước ngoài được ghi trên giấy phép.
- **Mẫu nhỏ:** trước 1970 có ít ca, khoảng tin cậy rất rộng; xem các con số thập kỷ này là định tính.
- **Liên quan không có nghĩa là nguyên nhân:** sự thay đổi có thể do oxy, lộ trình, kinh nghiệm hướng dẫn viên, thời tiết, cách ghi chép hoặc thay đổi về số đoàn. Dữ liệu quan sát không tách được các yếu tố này.
- **Tỉ lệ thấp hơn không đồng nghĩa với rủi ro thấp:** 6,7–8,6 ca trên 1.000 người nghĩa là vẫn có khoảng 1 trên 115–150 người tử vong trong mỗi lần leo (tính theo tỉ lệ 2010s–2000s, 1.000 / 8,6 đến 1.000 / 6,7).
