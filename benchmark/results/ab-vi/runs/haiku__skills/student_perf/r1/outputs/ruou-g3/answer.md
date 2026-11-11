# Uống rượu có liên quan đến điểm cuối kỳ G3 thấp hơn không?

## Trả lời ngắn

**Có, theo chiều thấp hơn, nhưng mối liên hệ nhỏ đến trung bình và phần lớn biến mất khi kiểm soát điểm kỳ trước.**

- Thô (chưa hiệu chỉnh), cả hai môn: học sinh uống nhiều hơn có G3 thấp hơn. Tương quan Spearman ρ ≈ −0.18 cho cả ngày thường (Dalc) và cuối tuần (Walc). So sánh nhóm thấp (1–2) với cao (3–5): chênh lệch khoảng 1.0–1.3 điểm trên thang 0–20, Cohen's d = 0.35 (cuối tuần) đến 0.45 (ngày thường).
- Khi hiệu chỉnh giới tính, tuổi, thời gian học, số lần trượt, số buổi vắng: môn Bồ Đào Nha vẫn có liên hệ có ý nghĩa thống kê, môn Toán chỉ có ý nghĩa ở một số mô hình; gộp cả hai môn thì không đạt mức 5%.
- Khi thêm điểm kỳ 1 (G1) và kỳ 2 (G2) vào mô hình: ước lượng gần 0 và không có ý nghĩa thống kê ở mọi môn (p từ 0.19 đến 0.54). Nghĩa là học sinh uống nhiều thường đã có điểm thấp hơn từ trước; phần lớn khác biệt G3 đi qua kết quả học kỳ trước.

Đây là dữ liệu quan sát, nên chỉ kết luận về **liên hệ**, không kết luận rượu **gây ra** điểm thấp.

## Dữ liệu và xử lý

**Nguồn:** `data/student-mat.csv` (Toán, 395 dòng) và `data/student-por.csv` (Bồ Đào Nha, 649 dòng). Hai file có cùng cấu trúc 33 cột; không có giá trị thiếu, không có dòng trùng lặp hoàn toàn.

**Học sinh xuất hiện ở cả hai file.**
- Khóa gộp 13 cột trong `student-merge.R` cho 382 cặp, nhưng 12 dòng bên Toán và 8 dòng bên Bồ Đào Nha khớp với nhiều hơn một dòng, nên đây là ghép nhiều-nhiều.
- Tôi ghép 1-1 bằng cách chấm điểm trên 14 thuộc tính gần như cố định giữa hai môn (ví dụ `guardian`, `traveltime`, `Dalc`, `Walc`, `higher`, `romantic`, ...). **370 cặp có khớp 14/14** và được ghép. 12 cặp còn lại không chọn được một cặp duy nhất nên giữ như hai học sinh riêng; con số này có thể đếm trùng một ít.
- Kết quả: **674 học sinh duy nhất** (1044 bản ghi học sinh–môn trừ 370 cặp). Trên 382 cặp của khóa R, Dalc/Walc khớp nhau ở 98.7% / 96.9% trường hợp, nên việc dùng chung một mức rượu cho học sinh học hai môn là hợp lý.
- Trong phân tích gộp, mỗi bản ghi học sinh–môn là một dòng, và sai số chuẩn được gom theo học sinh (cluster-robust). Điểm G3 của cùng một học sinh ở hai môn không được coi là độc lập.

**Giá trị G3 = 0 đáng ngờ.**
- Toán có 38 dòng G3 = 0 (25 dòng có G2 > 0), Bồ Đào Nha có 15 dòng (8 dòng có G2 > 0).
- **Mọi** dòng G3 = 0 đều có `absences = 0`. Điều này gợi ý các em đã nghỉ học, bỏ thi, hoặc không có bản ghi cuối kỳ, nên G3 = 0 không phải điểm thật.
- Quyết định: **loại 53 dòng G3 = 0** khỏi phân tích chính (còn 991 dòng: 357 Toán, 634 Bồ Đào Nha). Đưa lại các dòng này không đổi chiều kết luận (xem Độ nhạy).

**Định nghĩa biến.** Dalc và Walc là thang 1–5 (1 = rất ít, 5 = rất nhiều). Để so sánh nhóm, chia thành "thấp" (1–2) và "cao" (3–5). Mô hình hồi quy coi mỗi bậc tăng là một đơn vị.

## Kết quả

### 1. Tương quan Spearman (thô, theo môn)

| Môn | Biến | n | ρ | KTC 95% | p |
|---|---|---|---|---|---|
| Bồ Đào Nha | Ngày thường (Dalc) | 634 | −0.20 | −0.28 đến −0.13 | <0.001 |
| Bồ Đào Nha | Cuối tuần (Walc) | 634 | −0.17 | −0.24 đến −0.09 | <0.001 |
| Toán | Ngày thường (Dalc) | 357 | −0.15 | −0.25 đến −0.05 | 0.004 |
| Toán | Cuối tuần (Walc) | 357 | −0.19 | −0.29 đến −0.09 | <0.001 |
| Gộp (2 môn) | Ngày thường | 991 | −0.18 | −0.24 đến −0.12 | <0.001* |
| Gộp (2 môn) | Cuối tuần | 991 | −0.18 | −0.24 đến −0.12 | <0.001* |

*p-value gộp coi các dòng là độc lập nên bị lạc quan; dùng hồi quy có sai số theo học sinh (mục 3) để kết luận.

### 2. Thấp (1–2) so với cao (3–5)

| Phân tích | Biến | n thấp / cao | G3 TB thấp → cao | Hiệu | Cohen's d | p (Mann–Whitney) |
|---|---|---|---|---|---|---|
| Bồ Đào Nha | Ngày thường | 560 / 74 | 12.4 → 10.9 | 1.5 | 0.56 | <0.001 |
| Bồ Đào Nha | Cuối tuần | 391 / 243 | 12.5 → 11.7 | 0.8 | 0.32 | 0.0002 |
| Toán | Ngày thường | 314 / 43 | 11.6 → 10.7 | 1.0 | 0.31 | 0.058 |
| Toán | Cuối tuần | 206 / 151 | 12.0 → 10.8 | 1.2 | 0.38 | 0.0004 |
| Gộp | Ngày thường | 874 / 117 | 12.1 → 10.8 | 1.3 | 0.45 | <0.001 |
| Gộp | Cuối tuần | 597 / 394 | 12.3 → 11.3 | 1.0 | 0.35 | <0.001 |

Nhóm "cao" ngày thường ở Toán chỉ có 43 học sinh, nên ước lượng môn này kém chắc hơn.

### 3. Hồi quy: G3 thay đổi bao nhiêu điểm mỗi bậc tăng (sai số theo học sinh)

| Mô hình | Gộp, Dalc | Gộp, Walc | Bồ Đào Nha, Dalc | Bồ Đào Nha, Walc | Toán, Dalc | Toán, Walc |
|---|---|---|---|---|---|---|
| A: thô (có biến môn) | −0.34* | −0.27* | −0.62*** | −0.39*** | −0.49** | −0.47*** |
| B: + giới, tuổi, học tập, trượt, vắng | −0.23 | −0.18 | −0.40** | −0.22** | −0.35* | −0.37** |
| C: + G1, G2 | −0.06 | −0.02 | −0.10 | −0.05 | −0.05 | −0.04 |

\* p<0.05, \*\* p<0.01, \*\*\* p<0.001. Các ô môn đơn không có biến môn. Đầy đủ KTC và p trong `hoi_quy_he_so.csv`.

Đọc bảng: với mô hình B, học sinh Bồ Đào Nha uống nhiều hơn một bậc (ngày thường) có G3 thấp hơn khoảng 0.4 điểm, và mô hình C cho thấy hầu hết chênh lệch này đi qua G1, G2.

### 4. Độ nhạy

| Kịch bản | Dalc (ρ) | Walc (ρ) |
|---|---|---|
| Chính (bỏ G3 = 0, 991 dòng) | −0.18 | −0.18 |
| Giữ G3 = 0 (Bồ Đào Nha) | −0.21 | −0.17 |
| Giữ G3 = 0 (Toán) | −0.12 | −0.10 |
| Mỗi học sinh 1 dòng, lấy TB 2 môn (659 HS) | −0.19 | −0.18 |
| Chỉ học sinh không trùng, 1 môn (291) | −0.15 | −0.15 |

Mọi kịch bản đều cùng chiều âm. Độ lớn thay đổi nhẹ.

## Phương pháp

1. Đọc hai file, kiểm tra kiểu dữ liệu, giá trị ngoài miền, G3 = 0.
2. Ghép học sinh hai môn bằng khóa gộp, chọn cặp 1-1 theo độ khớp 14 thuộc tính (`ghep_hoc_sinh_2_mon.csv`).
3. Tương quan Spearman và so sánh nhóm (Mann–Whitney, Cohen's d, rank-biserial) cho từng môn.
4. OLS với 3 mô hình (A, B, C), sai số chuẩn cluster-robust theo học sinh, phân bố t với G−1 bậc tự do.
5. Độ nhạy: đưa G3 = 0 trở lại; gộp mỗi học sinh một dòng; chỉ dùng học sinh không trùng.

Mã nguồn: `analysis.py`. Kết quả: `tuong_quan_spearman.csv`, `so_sanh_nhom_thap_cao.csv`, `hoi_quy_he_so.csv`, `do_nhay.csv`, `kiem_tra_G3_0.csv`, `tom_tat_du_lieu.csv`. Biểu đồ: `bieu_do_hop_G3_theo_ruou.png`, `bieu_do_forest_he_so.png`.

## Hạn chế

- **Quan sát, không phải thí nghiệm.** Học sinh uống nhiều có thể khác biệt về nhiều yếu tố chưa đo (động lực, gia đình, bạn bè). Mô hình C giải thích phần lớn liên hệ bằng điểm trước đó, nhưng vẫn có thể có yếu tố chưa đo.
- **Mức rượu tự báo cáo** trên thang 1–5, không đo lượng cồn thực tế.
- **G3 = 0 được coi là thiếu dữ liệu** là một giả định. Nếu đây là điểm thật (ví dụ bị đánh rớt), kết luận có thể thay đổi nhẹ, dù độ nhạy cho thấy chiều vẫn âm.
- **Cặp học sinh 1-1** dựa trên độ khớp thuộc tính, không phải mã định danh; 12 cặp mơ hồ không được ghép.
- **Nhiều kiểm định** (2 biến × 2 môn × 3 mô hình); các p-value gần ngưỡng 0.05 nên đọc thận trọng.
- Dữ liệu là học sinh trung học ở hai trường Bồ Đào Nha, kết quả không nhất thiết áp dụng cho nơi khác.
