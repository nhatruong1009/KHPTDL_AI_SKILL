# Uống rượu và điểm cuối kỳ (G3): Toán + Bồ Đào Nha

## Trả lời ngắn gọn

**Có, nhưng chỉ ở mức liên quan thô.** Học sinh uống nhiều rượu hơn có điểm G3 thấp hơn rõ rệt:

- Tương quan Spearman giữa mức uống rượu và G3 khoảng **−0,18** (KTC 95% bootstrap theo học sinh: −0,25 đến −0,11).
- Hồi quy có kiểm soát môn học: mỗi mức Walc (1–5) tương ứng với **−0,42 điểm** G3 (KTC 95%: −0,58 đến −0,25; p < 0,001).
- So sánh nhóm cực đoan (uống nhiều: Walc ≥ 4 so với ít: Walc ≤ 2): TB G3 **10,90 so với 12,35**, chênh lệch **−1,44 điểm**, **Cohen's d = −0,50** (Welch p < 0,001).

**Nhưng mối liên quan này gần như biến mất khi kiểm soát điểm G2 (kỳ giữa).** Khi thêm G2 và số buổi nghỉ học vào mô hình, hệ số Walc chỉ còn **−0,05 điểm/mức** (KTC 95%: −0,11 đến +0,005; p = 0,07). Nói cách khác, phần lớn khác biệt điểm cuối kỳ đã có sẵn ở điểm giữa kỳ của những học sinh uống nhiều. Đây là dữ liệu quan sát cắt ngang, nên không thể kết luận rượu *gây ra* điểm thấp.

## Dữ liệu và cách xử lý

**1. Học sinh xuất hiện ở cả hai file**
- `student-mat.csv` có 395 dòng; `student-por.csv` có 649 dòng.
- File `student-merge.R` ghép trên 13 thuộc tính nền và cho **382 dòng**. Con số này không phải 382 học sinh: vì có nhiều bản ghi trùng khóa (4 trong file Toán, 12 trong file Bồ Đào Nha), phép ghép tạo ra cặp nhân chéo. Kiểm tra cho thấy chỉ có 382 dòng ghép được theo kiểu R, chứ không phải số học sinh duy nhất.
- Tôi ghép **1–1** trên 22 thuộc tính ổn định của học sinh (13 thuộc tính nền + guardian, traveltime, higher, romantic, famrel, goout, health, freetime, studytime). Các thuộc tính như `paid`, `absences`, G1–G3 bị loại vì phụ thuộc môn học. Kết quả: **370 cặp** khớp duy nhất.
- Tổng số học sinh duy nhất là **674** (395 + 649 − 370). Với 370 học sinh có mặt ở cả hai môn, Dalc và Walc khớp nhau 100% giữa hai file.
- Phân tích dùng **bảng dài**: mỗi dòng là một học sinh trong một môn (1.044 dòng). SE được tính **cluster-robust theo học sinh**, nên học sinh trùng không bị đếm hai lần như độc lập. Mức uống rượu của học sinh trùng là trung bình hai lần tự khai (thực tế giống nhau).

**2. Mức uống rượu**
- Dalc (ngày thường, 1–5), Walc (cuối tuần, 1–5), và chỉ số trọng số theo tuần (5·Dalc + 2·Walc)/7. Kết quả cả ba cùng chiều và độ lớn tương tự.

**3. Giá trị G3 đáng ngờ**
- Có **53 dòng G3 = 0** (38 môn Toán, 15 môn Bồ Đào Nha). Cả 53 dòng đều có `absences = 0`, và 33 dòng có G2 > 0. Mẫu này phù hợp với học sinh bỏ học hoặc không được chấm cuối kỳ, không phải điểm thật. **Loại khỏi mẫu chính** (còn 991 dòng, 659 học sinh). Kết quả khi giữ lại các số 0 được báo cáo ở phần độ nhạy.
- Các G3 thấp khác 0 (1–5, khoảng 10 dòng) có G2 tương ứng gần, nên được giữ lại.

## Bảng kết quả chính

| Phân tích (mẫu chính, bỏ G3=0) | Hệ số / effect size | KTC 95% | p |
|---|---|---|---|
| Spearman, Walc vs G3 | ρ = −0,18 | −0,25 đến −0,11 | — |
| Spearman, Dalc vs G3 | ρ = −0,18 | −0,25 đến −0,12 | — |
| Spearman, chỉ số tuần vs G3 | ρ = −0,19 | −0,26 đến −0,12 | — |
| OLS M1: G3 ~ Walc + môn | −0,42 điểm/mức | −0,58 đến −0,25 | < 0,001 |
| OLS M1: G3 ~ Dalc + môn | −0,57 điểm/mức | −0,79 đến −0,36 | < 0,001 |
| OLS M2: M1 + G2 + nghỉ học | −0,05 điểm/mức (Walc) | −0,11 đến +0,005 | 0,07 |
| Nhóm Walc ≥ 4 vs ≤ 2 | Cohen d = −0,50 | — | < 0,001 (Welch) |

**Tách theo môn:** Bồ Đào Nha (Walc, M1) −0,39 (p < 0,001); Toán (Walc, M1) −0,47 (p < 0,001). Khi thêm G2 và nghỉ học, cả hai đều không còn ý nghĩa (p = 0,13 và 0,23).

**Độ nhạy:**
- Giữ G3 = 0: M1 Walc = −0,35 (p = 0,001), d = −0,30; M2 Walc = −0,02 (p = 0,66).
- Chỉ dùng học sinh không trùng (1 dòng/HS): Walc = −0,34 (p = 0,002).

**Trung bình G3 theo Walc (mẫu chính):** 1: 12,43 · 2: 12,20 · 3: 11,82 · 4: 10,85 · 5: 11,00. Xem `outputs/chart_g3_by_walc.png`.

## Kết luận và hạn chế

- Học sinh uống nhiều rượu, đặc biệt cuối tuần, có điểm cuối kỳ thấp hơn đáng kể (khoảng 1,4 điểm ở nhóm cực đoan, d ≈ −0,5). Đây là mối liên quan thật trong dữ liệu.
- Phần lớn khác biệt này đi kèm với điểm giữa kỳ thấp hơn (G2). Khi so sánh học sinh có cùng G2 và số buổi nghỉ, gần như không còn mối liên quan có ý nghĩa.
- Hạn chế: dữ liệu cắt ngang, tự báo cáo; không có thông tin về thời điểm uống rượu so với các kỳ điểm; loại G3 = 0 là giả định hợp lý nhưng không chắc chắn, dù kết quả không đổi về chiều.

## Tệp đầu ra
- `outputs/summary.json`: số lượng học sinh, dòng, cặp ghép.
- `outputs/spearman_results.csv`, `outputs/regression_results.csv`, `outputs/group_comparison.csv`, `outputs/subject_split.csv`, `outputs/descriptive_by_walc.csv`.
- `outputs/long_clean.csv`: bảng dài đã làm sạch.
- `outputs/chart_g3_by_walc.png`: biểu đồ.
- `outputs/scripts/`: mã phân tích (`analysis.py`, `chart.py`).
