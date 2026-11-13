# Uống rượu và điểm cuối kỳ G3 (Toán + Bồ Đào Nha)

## Kết luận
**Có.** Học sinh uống nhiều có G3 thấp hơn. Mối liên quan ngược chiều, có ý nghĩa thống kê, nhưng **nhỏ đến vừa** (|r| ≈ 0,2), và đây chỉ là tương quan, chưa chứng minh nhân quả.

## Cách xử lý dữ liệu
- **Học sinh trùng hai file:** file Toán có 395 dòng, file Bồ Đào Nha có 649 dòng. Tôi ghép bằng 25 thuộc tính nền (13 thuộc tính của `student-merge.R` cộng guardian, traveltime, studytime, schoolsup, famsup, activities, higher, romantic, famrel, freetime, goout, health). Kết quả: 370 học sinh có mặt ở cả hai file, tổng **672 học sinh duy nhất** (1044 dòng). Dalc/Walc khớp 100% ở các cặp này, nên cách ghép đáng tin. Mỗi học sinh được tính **một lần**, với G3 là trung bình hai môn nếu học cả hai. Nếu cộng gộp 1044 dòng như hai mẫu độc lập thì p-value bị phóng đại.
- **G3 đáng ngờ:** 53 dòng có G3 = 0 (38 Toán, 15 Bồ Đào Nha). Các dòng này đều có `absences` = 0, và nhiều dòng có G2 > 0 (đạt điểm kỳ trước rồi về 0). Đây giống bỏ thi hoặc thôi học hơn là điểm 0 thật. **Phân tích chính coi G3 = 0 là thiếu dữ liệu** (15 học sinh chỉ có G3 = 0 bị loại, còn **657 học sinh**). Tôi chạy thêm bản giữ các điểm 0 để so sánh.
- **Mức uống:** Dalc (ngày thường), Walc (cuối tuần) và chỉ số gộp `alc = (5·Dalc + 2·Walc)/7`.

## Kết quả chính (657 học sinh, G3≠0)
| Biến | Spearman ρ (95% CI) | Pearson r | Cohen's d (uống ≥3 so với <3) | Chênh G3 | p (Welch) | Hệ số hồi quy hiệu chỉnh* |
|---|---|---|---|---|---|---|
| Dalc | −0,19 (−0,26; −0,12) | −0,20 | **−0,50** (−0,71; −0,28), n_cao = 79 | −1,30 điểm | <0,0001 | −0,32 điểm/bậc, p = 0,004 |
| Walc | −0,18 (−0,26; −0,11) | −0,20 | **−0,37** (−0,52; −0,22), n_cao = 254 | −0,98 điểm | <0,0001 | −0,24 điểm/bậc, p = 0,004 |
| alc | −0,20 (−0,27; −0,12) | −0,22 | **−0,54** (−0,75; −0,35), n_cao = 77 | −1,41 điểm | <0,0001 | −0,37 điểm/bậc, p = 0,001 |

\*OLS với sai số chuẩn HC3, kiểm soát giới, tuổi, thời gian học, số lần rớt, ý định học cao hơn, trường, học vấn bố mẹ, goout. Hệ số chuẩn hoá còn khoảng −0,09 đến −0,14 SD mỗi bậc.

G3 trung bình giảm đều theo bậc Dalc: 12,1 → 11,4 → 10,9 → 10,5 → 10,1 (bậc 1 → 5). Với Walc: 12,3 → 12,1 → 11,7 → 10,8 → 10,9.

Sau khi kiểm soát, hệ số giảm khoảng 35–40% nhưng vẫn có ý nghĩa. Một phần mối liên quan thô là do các yếu tố đi kèm (giới, số lần rớt, đi chơi).

## Kiểm tra độ vững
- **Theo môn (bỏ G3=0):** Bồ Đào Nha ρ ≈ −0,20 (Dalc), −0,17 (Walc), p < 0,0001. Toán ρ ≈ −0,15 (Dalc), −0,19 (Walc), p < 0,01, nhưng sau hiệu chỉnh chỉ còn p ≈ 0,06–0,12.
- **Giữ G3=0:** Spearman vẫn âm, có ý nghĩa (ρ ≈ −0,17 Dalc, −0,13 Walc; d ≈ −0,29 và −0,25). Tuy nhiên sau hiệu chỉnh không còn ý nghĩa (p = 0,08 và 0,16). Riêng môn Toán, trung bình G3 hầu như không khác nhau (d ≈ 0). Nguyên nhân: các điểm 0 không tập trung ở người uống nhiều (tỉ lệ có G3=0: 5% ở nhóm Dalc ≥3 so với 8% ở nhóm còn lại; Fisher p = 0,50), nên chúng làm nhiễu chứ không giải thích hiệu ứng.
- Cách xử lý G3=0 ảnh hưởng đáng kể tới độ lớn hiệu ứng. Kết luận về chiều âm thì bền, còn độ lớn thì không chắc chắn.

## Lưu ý
- Dữ liệu cắt ngang, hai biến tự khai, mẫu uống nhiều (Dalc ≥4) chỉ khoảng 34 học sinh.
- Ngưỡng "uống nhiều" (≥3) do tôi chọn. Dùng ρ và hồi quy thì không phụ thuộc ngưỡng này.
- Các p-value ở bảng chưa hiệu chỉnh cho việc kiểm định nhiều lần (3 biến), nhưng đều đủ nhỏ để không đổi kết luận.

File: `analysis.py` (mã), `results.csv` (toàn bộ số liệu), `group_means.csv`, `g3_theo_muc_uong.png`.
