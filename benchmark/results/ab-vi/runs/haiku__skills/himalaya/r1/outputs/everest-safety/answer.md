# Leo núi Everest có an toàn hơn theo thời gian không?

## Trả lời ngắn

**Có, nhưng không đồng đều.** Tỉ lệ tử vong trên Everest giảm rõ rệt ở cả hai nhóm sau 1990:

- **Thành viên đoàn:** 1,96% (trước 1990) → 1,04% (1990–2019). Giảm còn khoảng một nửa.
- **Nhân viên được thuê (hired staff):** 2,06% (trước 1990) → 0,67% (1990–2019). Giảm còn khoảng một phần ba.

Sau 1990, nhân viên được thuê có tỉ lệ tử vong **thấp hơn** thành viên đoàn (0,67% so với 1,04%; p = 0,003). Trước 1990 hai nhóm gần như ngang nhau (1,96% so với 2,06%; p = 0,80).

Tuy vậy, số ca tử vong tuyệt đối không giảm: mỗi thập kỷ từ 1980 đến 2010 có khoảng 40–43 thành viên đoàn tử vong, trong khi số thành viên tăng từ 1.980 (1980s) lên 4.980 (2010s).

## Bằng chứng

**Tỉ lệ tử vong theo thập kỷ** (tử vong / số người; chỉ tính các thập kỷ có dữ liệu đủ lớn):

| Thập kỷ | Thành viên: tử vong / số người | Tỉ lệ thành viên | Nhân viên thuê: tử vong / số người | Tỉ lệ nhân viên |
|---|---|---|---|---|
| 1950s | 0 / 107 | 0,00% | 1 / 139 | 0,72% |
| 1960s | 4 / 184 | 2,17% | 2 / 359 | 0,56% |
| 1970s | 10 / 613 | 1,63% | 19 / 778 | 2,44% |
| 1980s | 40 / 1.980 | 2,02% | 20 / 1.012 | 1,98% |
| 1990s | 43 / 2.980 | 1,44% | 19 / 1.800 | 1,06% |
| 2000s | 42 / 4.360 | 0,96% | 9 / 3.302 | 0,27% |
| 2010s | 43 / 4.980 | 0,86% | 40 / 5.109 | 0,78% |

Các thập kỷ 1920s–1940s có rất ít người (dưới 100 thành viên mỗi thập kỷ), nên tỉ lệ dao động mạnh và không đáng tin. Chúng vẫn có trong bảng CSV nhưng không có trên biểu đồ.

**Trước và sau 1990** (1921–1989 so với 1990–2019):

| Nhóm | Trước 1990 | 1990 trở đi | Tỉ số (sau / trước) | p-value |
|---|---|---|---|---|
| Thành viên đoàn | 1,96% (58 / 2.961) | 1,04% (128 / 12.320) | 0,53 | < 0,001 |
| Nhân viên thuê | 2,06% (52 / 2.530) | 0,67% (68 / 10.211) | 0,32 | < 0,001 |

**Điều gì thay đổi trong kỷ nguyên thương mại?** Dữ liệu không ghi trực tiếp các yếu tố như hướng dẫn viên, thiết bị hay oxy. Một chỉ báo gián tiếp là cột `trekking_agency` (công ty lữ hành): gần như không có ở các chuyến trước 1970 (0%), nhưng xuất hiện ở 92% chuyến trong thập kỷ 1990 và 98% sau đó. Đây là bằng chứng tương quan, không phải nguyên nhân.

**Nguyên nhân tử vong** (từ `members.csv`, toàn bộ giai đoạn 1921–2019):

- Nhân viên thuê (120 ca): tuyết lở (56), sụp đổ thác băng (13), rơi đá/băng (3), nứt băng (7); các nguyên nhân khác ít hơn.
- Thành viên đoàn (186 ca): ngã (54), AMS - bệnh độ cao (27), kiệt sức (25), lạnh cóng (25), tuyết lở (21), mất tích không rõ lý do (9).

Nói cách khác, nhân viên thuê chịu rủi ro chủ yếu từ các mối nguy khách quan trên đường đi (băng, tuyết lở), còn thành viên đoàn chủ yếu gặp rủi ro do ngã và thể trạng ở độ cao.

## Phương pháp

- **Dữ liệu:** The Himalayan Database, phiên bản đã làm sạch (TidyTuesday 2020-09-22), lọc `peak_id == "EVER"`. Gồm 2.149 chuyến thám hiểm, 1921–2019.
- **Mẫu số:** Tổng số thành viên (`members`) và tổng số nhân viên thuê (`hired_staff`) lấy từ `expeditions.csv` theo từng chuyến. Tử vong lấy từ `member_deaths` và `hired_staff_deaths` cùng bảng.
- **Đối chiếu:** Tổng tử vong từ `expeditions.csv` khớp hoàn toàn với `members.csv`: 186 thành viên và 120 nhân viên.
- **Khoảng tin cậy 95%:** Wilson score.
- **Kiểm định:** Chi-square hai tỉ lệ, không hiệu chỉnh Yates.
- **Mã:** `analysis.py` trong thư mục này. Mọi số trong bài đều được tính từ mã này trên dữ liệu gốc.

## Hạn chế

1. **Quan sát, không phải thí nghiệm.** Dữ liệu cho thấy liên quan giữa thời gian và tỉ lệ tử vong, không chứng minh nguyên nhân.
2. **Mẫu số là người tham gia theo chuyến, không phải thời gian tiếp xúc độ cao.** Một người leo nhiều lần được đếm nhiều lần. Nhân viên thuê thường đi nhiều mùa hơn, nên cách đếm này có thể làm lệch so sánh giữa hai nhóm.
3. **Sự kiện tập trung.** Riêng năm 2014 (sập thác băng Khumbu) và 2015 (lở tuyết do động đất) chiếm 28 trên 68 ca nhân viên thuê tử vong sau 1990. Khi bỏ hai năm này, tỉ lệ nhân viên thuê sau 1990 là 0,42% (so với 1,10% thành viên đoàn), và kết luận không đổi.
4. **Giá trị 99 đáng ngờ.** Có 3 chuyến ghi `hired_staff = 99` (có thể là mã thiếu dữ liệu). Khi bỏ các dòng này, tỉ lệ nhân viên trước 1990 tăng từ 2,06% lên 2,33%. Kết luận so sánh trước/sau 1990 không đổi.
5. **Phạm vi thời gian.** Dữ liệu dừng ở mùa xuân 2019. Không có số liệu 2020 trở đi.
6. **Chỉ có một đỉnh.** Kết quả chỉ áp dụng cho Everest, không tổng quát hóa sang các đỉnh khác trong dữ liệu.
7. **Phân loại nhóm.** `hired` trong `members.csv` và `hired_staff` trong `expeditions.csv` không tương ứng hoàn toàn về số người (bảng thành viên có 6.730 nhân viên thuê, trong khi tổng `hired_staff` theo chuyến là 12.741). Vì vậy bài này dùng `expeditions.csv` làm mẫu số, và chỉ dùng `members.csv` để đối chiếu số ca tử vong.

## Tệp đầu ra

- `chart_ti_le_theo_thap_ky.png`: tỉ lệ tử vong theo thập kỷ từ 1950s, có khoảng tin cậy 95%.
- `chart_truoc_sau_1990.png`: so sánh trước và sau 1990.
- `chart_so_chuyen_theo_thap_ky.png`: số chuyến thám hiểm theo thập kỷ.
- `ti_le_tu_vong_theo_thap_ky.csv`, `ti_le_tu_vong_theo_ky_nguyen.csv`, `kiem_dinh_so_sanh.csv`, `nguyen_nhan_tu_vong.csv`, `tu_vong_theo_nam.csv`, `kiem_tra_doi_chieu.csv`: số liệu.
- `run_log.txt`: đầu ra của `analysis.py`.
