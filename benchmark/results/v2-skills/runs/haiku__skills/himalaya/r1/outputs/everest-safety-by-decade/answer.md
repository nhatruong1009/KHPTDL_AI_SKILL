# Leo núi Everest có an toàn hơn theo thời gian không?

**Trả lời:** Có, nhưng chủ yếu là *tỉ lệ* trên mỗi người. Từ trước 1990 đến 1990 trở đi, tỉ lệ tử vong giảm rõ rệt ở cả thành viên đoàn thám hiểm (1,96% → 1,04%) và nhân viên được thuê (2,06% → 0,67%, theo định nghĩa trong README). Cả hai mức giảm đều có ý nghĩa thống kê (Fisher p < 0,001). Sau năm 2000, tỉ lệ gần như đi ngang: không có xu hướng giảm có ý nghĩa thống kê trong kỷ nguyên thương mại. Số người tử vong *tuyệt đối* mỗi thập kỷ không giảm: thập kỷ 2010 có 83 ca, cao nhất trong toàn bộ giai đoạn dữ liệu, trong khi số người leo ngày càng đông (tổng số tử vong không đồng nghĩa với tỉ lệ tử vong).

**Bằng chứng:**

| Thập kỷ | Số đoàn | Thành viên | Tử vong TV | Tỉ lệ TV (%) | Nhân viên được thuê | Tử vong NV | Tỉ lệ NV (%) | Tổng tử vong |
|---|---|---|---|---|---|---|---|---|
| 1920 | 3 | 33 | 3 | 9,09 | 91 | 10 | 10,99 | 13 |
| 1930 | 5 | 43 | 1 | 2,33 | 149 | 0 | 0,00 | 1 |
| 1940 | 1 | 1 | 0 | 0,00 | 2 | 0 | 0,00 | 0 |
| 1950 | 9 | 107 | 0 | 0,00 | 139 | 1 | 0,72 | 1 |
| 1960 | 16 | 184 | 4 | 2,17 | 359 | 2 | 0,56 | 6 |
| 1970 | 29 | 613 | 10 | 1,63 | 778 | 19 | 2,44 | 29 |
| 1980 | 141 | 1.980 | 40 | 2,02 | 1.012 | 20 | 1,98 | 60 |
| 1990 | 331 | 2.980 | 43 | 1,44 | 1.800 | 19 | 1,06 | 62 |
| 2000 | 745 | 4.360 | 42 | 0,96 | 3.302 | 9 | 0,27 | 51 |
| 2010 | 869 | 4.980 | 43 | 0,86 | 5.109 | 40 | 0,78 | 83 |

So sánh trước và sau 1990 (đếm theo đoàn, khoảng tin cậy 95% Wilson):

| Nhóm | Trước 1990 | 1990 trở đi | p (Fisher) |
|---|---|---|---|
| Thành viên | 1,96% (1,52–2,52) | 1,04% (0,87–1,23) | 0,0001 |
| Nhân viên được thuê | 2,06% (1,57–2,69) | 0,67% (0,53–0,84) | <0,000001 |

Biểu đồ: [death_rate_by_decade.png](death_rate_by_decade.png)

**Cách làm:**
- Dữ liệu: The Himalayan Database, lọc `peak_id == "EVER"` (Everest): 2.149 đoàn, 1921–2019, từ `expeditions.csv`.
- Tỉ lệ tử vong = số tử vong / tổng số người trong nhóm (thành viên: `members`; nhân viên: `hired_staff`), tổng hợp theo thập kỷ và theo kỷ nguyên. Đây là định nghĩa mẫu số theo README.
- Ranh giới "kỷ nguyên thương mại" = từ năm 1990 (theo yêu cầu). Dữ liệu không có cờ "thương mại" riêng.
- Kiểm định: Fisher exact cho trước/sau 1990; hồi quy tuyến tính tỉ lệ theo năm trong giai đoạn 1990+.
- Mã: `outputs/everest-safety-by-decade/analysis.py`; bảng: `death_rate_by_decade.csv`, `death_rate_by_era.csv`, `era_tests.csv`, `trend_1990plus.csv`.

**Giả định và hạn chế:**
- **Mẫu số của nhân viên được thuê không thống nhất giữa hai file.** `expeditions.csv` ghi 12.741 nhân viên trên Everest, trong khi `members.csv` chỉ có 6.730 người có cờ `hired`. Số ca tử vong khớp nhau (120), nên chỉ khác mẫu số. Với mẫu số theo từng người (`members.csv`), tỉ lệ nhân viên sau 1990 là 1,07% (không phải 0,67%), và trước 1990 là 14,4% (không đáng tin, vì file này thiếu nhiều nhân viên trước 1990). **Kết luận "nhân viên an toàn hơn thành viên sau 1990" không đứng vững:** theo mẫu số từng người, hai nhóm gần như ngang nhau (1,07% so với 1,04%). Kết luận chắc chắn hơn là: *tỉ lệ của cả hai nhóm đều giảm đáng kể sau 1990.*
- Các thập kỷ 1920–1940 chỉ có 1–5 đoàn, nên tỉ lệ rất dao động; không nên đọc chi tiết.
- Số liệu quan sát: đây là tương quan theo thời gian, không chứng minh nguyên nhân. Sự giảm có thể do thiết bị, kinh nghiệm dẫn đường, cung cấp oxy, quy định, hoặc thay đổi về cấu trúc đoàn; dữ liệu không đo được riêng từng yếu tố.
- Tỉ lệ trên mỗi người không bằng rủi ro cho một người leo mới: một người leo nhiều lần sẽ được tính nhiều lần.
- "Nhân viên được thuê" trong `expeditions.csv` chỉ gồm nhân viên đi trên mức trại cơ sở (above basecamp), theo README; nhân viên ở trại cơ sở không được tính.
- Dữ liệu tới năm 2019.
