# Leo Everest có an toàn hơn theo thời gian không?

**Trả lời:** Có — nhưng chủ yếu là "an toàn hơn so với thập niên 1970-80", và mức cải thiện đã chững lại từ 2000. Trên Everest, tỉ lệ tử vong của thành viên đoàn giảm từ **1,9%** (1970-89) xuống **0,9%** (2010-19); của nhân viên được thuê (hired staff) giảm từ **2,2%** xuống **0,8%**, với đáy là **0,3%** ở 2000-09. Từ 1990, hai nhóm không còn khác nhau rõ rệt, trừ thập niên 2000, khi nhân viên thuê có tỉ lệ tử vong thấp hơn hẳn.

## Bằng chứng

Tỉ lệ tử vong = số người chết / số người đi lên trên base camp (ghi trong `expeditions.csv`, Everest). Nguồn: `headline_expedition_by_period.csv`.

| Giai đoạn | Số chuyến | Thành viên: chết/tổng | Tỉ lệ | Nhân viên thuê: chết/tổng | Tỉ lệ |
|---|---|---|---|---|---|
| 1921-69 | 34 | 8/368 | 2,2% | 13/740 | 1,8% |
| 1970-89 | 170 | 50/2.593 | 1,9% | 39/1.790 | 2,2% |
| 1990-99 | 331 | 43/2.980 | 1,4% | 19/1.800 | 1,1% |
| 2000-09 | 745 | 42/4.360 | 1,0% | 9/3.302 | 0,3% |
| 2010-19 | 869 | 43/4.980 | 0,9% | 40/5.109 | 0,8% |

- Gộp 1970-89 so với 1990-2019: thành viên 1,93% → 1,04% (50/2.593 so với 128/12.320, Fisher p = 0,0004); nhân viên thuê 2,18% → 0,67% (39/1.790 so với 68/10.211, p < 0,001).
- Hired so với thành viên trong từng giai đoạn: chỉ 2000-09 khác biệt có ý nghĩa (OR = 0,28; p = 0,0002). Các giai đoạn khác p > 0,29.
- Từ thập niên 1990 sang 2010: thành viên vẫn giảm (1,44% → 0,86%, p = 0,018), nhân viên thuê **không** giảm có ý nghĩa (1,06% → 0,78%, p = 0,30) và tăng lại so với 2000-09 (0,27% → 0,78%).
- **Kiểm tra độ bền:** 28/40 ca chết của nhân viên thuê trong 2010-19 xảy ra ở hai năm 2014 (17) và 2015 (11). Bỏ hai năm này, tỉ lệ 2010-19 là **0,27%** (12/4.365) cho nhân viên thuê và **0,99%** (40/4.058) cho thành viên. Vì vậy con số 0,8% của nhân viên thuê phụ thuộc rất nhiều vào hai biến cố đơn lẻ; thành viên thì ổn định quanh 1%.
- Tỉ lệ chuyến đi có ít nhất 1 người chết: 29% (1970-89) → 14% (1990-99) → 6% (2000-09) → 7% (2010-19) (`expedition_fatality_incidence.csv`).
- Kỷ nguyên thương mại: số chuyến mỗi thập niên tăng từ 141 (1980s) lên 331 (1990s), 745 (2000s), 869 (2010s). Số nhân viên thuê trên mỗi thành viên tăng từ 0,69 (1970-89) lên 1,03 (2010-19). Tỉ lệ người lên đến đỉnh (mọi hàng trong `members.csv`) tăng từ 9% (1980s) lên 62% (2010s), dùng oxy từ 21% lên 71% (`context_by_decade.csv`).
- Nguyên nhân tử vong từ 1990 (`members.csv`): trong 68 ca của nhân viên thuê, 63% do tuyết lở/sập băng/đá rơi/khe nứt (riêng tuyết lở 33 ca); trong 128 ca của thành viên chỉ 9%, phần còn lại chủ yếu là ngã (31), say độ cao AMS (24), kiệt sức (23), tê cóng (17).

Biểu đồ: [chart1](chart1_tu_vong_theo_giai_doan.png) · [chart2](chart2_tu_vong_theo_nam.png) · [chart3](chart3_chuyen_di_co_nguoi_chet.png)

## Cách làm
- Dữ liệu: Himalayan Database (`expeditions.csv`, `members.csv`), lọc `peak_name == "Everest"`, 2.149 chuyến, 1921-2019.
- Tỉ lệ cho từng nhóm = `member_deaths / members` và `hired_staff_deaths / hired_staff`, cộng dồn theo giai đoạn; khoảng tin cậy Wilson 95%; so sánh bằng Fisher exact.
- Code: `analysis.py` (bảng, kiểm định), `analysis2.py` (số liệu chính, độ bền), `charts.py`.

## Giả định & hạn chế
- **Mẫu số của nhân viên thuê:** `members.csv` thiếu nhiều dòng nhân viên thuê trước 2000 (vd. thập niên 1980 chỉ có 145 dòng "hired", trong khi `expeditions.csv` ghi 1.012 người). Dùng bảng thành viên sẽ cho tỉ lệ hired phóng đại (1970s: 36,5%; 1980s: 13,8%; `rates_by_decade_members_table.csv`). Số ca chết của hired thì khớp giữa hai bảng (120), nên tôi dùng mẫu số từ `expeditions.csv` làm kết quả chính. Với mẫu số bảng thành viên, xu hướng giảm vẫn đúng chiều nhưng mức giảm bị thổi phồng.
- **Đo theo người trên mỗi chuyến, không theo mức phơi nhiễm:** nhân viên thuê có thể phải đi lại nhiều lần hơn trên tuyến (dữ liệu không đo số lần hay số ngày phơi nhiễm), nên tỉ lệ thấp không đồng nghĩa công việc của họ ít rủi ro hơn.
- **Thập niên trước 1970** rất ít chuyến (34 chuyến trước 1970) → khoảng tin cậy rộng; các thập niên 1920-50 không dùng để kết luận.
- 2 chuyến có số chết lớn hơn số người ghi nhận (dữ liệu nhập lỗi); ảnh hưởng không đáng kể.
- Đây là dữ liệu quan sát: các thay đổi (đoàn thương mại, nhiều hỗ trợ hơn, dùng oxy nhiều hơn) **đi cùng** mức tử vong thấp hơn, nhưng dữ liệu không chứng minh chúng là nguyên nhân.
- Mẫu số của nhân viên thuê là số người "went above basecamp" (theo readme), còn ca chết có thể xảy ra ở bất kỳ độ cao nào; dữ liệu không cho biết có ca nào xảy ra ở base camp hay không nên tỉ lệ có thể lệch nhẹ.
