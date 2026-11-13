# Uống rượu có liên quan đến điểm cuối kỳ G3 thấp hơn không?

## Trả lời ngắn

- **Có liên quan thô, và có ý nghĩa thống kê.** Học sinh uống nhiều rượu có G3 trung bình thấp hơn: hiệu ứng nhỏ đến trung bình (Cohen's d ≈ −0,5 đến −0,6 giữa nhóm mức 1 và nhóm mức 4–5; Cliff's δ ≈ −0,3; Spearman ρ ≈ −0,18).
- **Nhưng liên quan này gần như biến mất khi tính đến điểm G1 và G2.** Sau khi điều chỉnh, hệ số cho mỗi mức uống rượu gần 0 và khoảng tin cậy 95% đều chứa 0 (Dalc: −0,08 điểm/mức [−0,19; +0,04], p = 0,19; Walc: −0,05 điểm/mức [−0,10; +0,01], p = 0,12). Hiệu ứng này không ổn định qua các kịch bản kiểm tra.
- **Kết luận:** dữ liệu cho thấy học sinh uống nhiều rượu có điểm cuối kỳ thấp hơn, nhưng phần lớn chênh lệch đi cùng với điểm các kỳ trước thấp hơn. Dữ liệu quan sát không cho thấy rượu làm giảm G3.

## Số liệu chính (mẫu chính: 990 bản ghi học sinh × môn, 660 học sinh)

**Điểm G3 trung bình theo mức (chỉ số tự báo cáo, 1 = thấp nhất, 5 = cao nhất):**

| Mức | Walc (cuối tuần) n | G3 TB | Dalc (ngày thường) n | G3 TB |
|---|---|---|---|---|
| 1 | 375 | 12,4 | 692 | 12,3 |
| 2 | 221 | 12,2 | 181 | 11,4 |
| 3 | 191 | 11,8 | 68 | 11,1 |
| 4 | 134 | 10,9 | 23 | 10,5 |
| 5 | 69 | 11,0 | 26 | 10,4 |

**Hiệu ứng và ý nghĩa thống kê:**

| Chỉ số | Kịch bản | Spearman ρ [95% CI] | Cohen's d (mức 4–5 vs 1) | Cliff's δ | Hệ số thô / mức (p) | Hệ số điều chỉnh / mức [95% CI] (p) | β chuẩn hóa | ΔR² do thêm biến |
|---|---|---|---|---|---|---|---|---|
| Walc | A (chính) | −0,18 [−0,25; −0,10] | −0,53 | −0,29 | −0,43 (<0,001) | −0,05 [−0,10; +0,01] (0,12) | −0,02 | 0,0003 |
| Dalc | A (chính) | −0,18 [−0,25; −0,12] | −0,64 | −0,32 | −0,58 (<0,001) | −0,08 [−0,19; +0,04] (0,19) | −0,02 | 0,0005 |

Các kiểm tra độ bền (điều chỉnh G1, G2, môn, giới, tuổi, học tập, trượt môn):

- **Kịch bản B** (không loại bản ghi nào, gồm G3 = 0): thô vẫn có ý nghĩa (Dalc −0,55, p < 0,001; Walc −0,35, p < 0,001); điều chỉnh không còn ý nghĩa (Dalc −0,02, p = 0,76; Walc +0,02, p = 0,63).
- **Kịch bản C, D** (mỗi học sinh giữ một bản ghi): điều chỉnh đều không có ý nghĩa (p từ 0,09 đến 0,24).
- **Mô hình gộp** Dalc + Walc cùng lúc: Dalc −0,06 (p = 0,34), Walc −0,02 (p = 0,49).
- **Thêm goout, health, absences** làm biến kiểm soát: Dalc −0,06 (p = 0,37), Walc +0,01 (p = 0,76).
- **Theo từng môn** (điều chỉnh): Toán Dalc −0,06 [−0,19; +0,07], Walc −0,05 [−0,13; +0,03]; Tiếng Bồ Đào Nha Dalc −0,10 [−0,24; +0,05], Walc −0,05 [−0,12; +0,02]. Đều không có ý nghĩa.

## Phương pháp

1. **Ghép học sinh ở cả hai file.** Dùng đúng 13 khóa trong `student-merge.R`. Codebook ghi 382 học sinh, nhưng 16 cặp khớp có khóa trùng (12 bản ghi Toán và 8 bản ghi Tiếng Bồ Đào Nha xuất hiện nhiều lần), nên chỉ còn **366 cặp 1-1** (giữ cặp đầu tiên theo thứ tự file). Kết quả: 678 học sinh duy nhất (395 + 649 − 366), 366 học sinh học cả hai môn. Các cột không dùng làm khóa trùng giá trị ở hầu hết cặp: Dalc 99,7%, Walc 99,2%, guardian 100%, famrel 99,7%, goout 99,2%. Cột `paid` chỉ trùng 55%, phù hợp vì nó là lớp học thêm theo từng môn.
2. **Không đếm trùng học sinh.** Mỗi bản ghi là một cặp học sinh × môn. Học sinh cả hai môn có cùng `student_id`, và sai số chuẩn được gom cụm theo học sinh (cluster-robust, CR1).
3. **Xử lý G3 đáng ngờ.** Có 38 bản ghi G3 = 0 ở Toán (25 bản ghi có G2 > 0) và 15 ở Tiếng Bồ Đào Nha (8 bản ghi có G2 > 0). Điểm 0 này nhiều khả năng là bỏ học hoặc không thi cuối kỳ, không phải điểm thật, nên **mẫu chính loại các bản ghi G3 = 0**. Ngoài ra loại 1 bản ghi có G1 = 0 (Tiếng Bồ Đào Nha) vì G1 được dùng làm biến kiểm soát; mọi bản ghi G2 = 0 đều đã có G3 = 0 nên đã nằm trong nhóm loại đầu tiên. Tổng cộng 54 bản ghi bị loại (1.044 → 990). Kịch bản B đưa lại toàn bộ bản ghi vào và kết luận không đổi.
4. **Effect size:** Spearman ρ (khoảng tin cậy bootstrap theo cụm học sinh, 500 lần lặp), Cohen's d và Cliff's δ giữa mức 1 và mức 4–5, hệ số OLS theo mức, β chuẩn hóa và ΔR² do riêng biến uống rượu.
5. **Biến kiểm soát:** G1, G2 (điểm các kỳ trước, có trước G3), môn, giới, tuổi, studytime, failures. Không đưa `absences` vào mô hình chính vì nó được tích lũy trong năm học và có thể là biến trung gian; kiểm tra riêng ở mục "thêm goout, health, absences".
6. **Thống kê so sánh nhóm:** Mann–Whitney U hai phía (mức 1 so với mức 4–5). Kết quả có ý nghĩa thô (p < 0,001 với Walc và Dalc).

## Hạn chế

- **Dữ liệu quan sát, không phải thực nghiệm.** Các hệ số chỉ là liên hệ, không phải nhân quả. Ngay cả khi điều chỉnh G1 và G2, vẫn có thể còn yếu tố chưa đo được (động lực, nền tảng gia đình, hoạt động xã hội).
- **Mức uống rượu là tự báo cáo, thang 1–5.** Các mức 4–5 có ít quan sát (Dalc 49 bản ghi, Walc 203), nên khoảng tin cậy ở đó rộng.
- **Điểm G1–G2 chiếm phần lớn phương sai G3** (G2 có hệ số ≈ 0,81, R² ≈ 0,91). Khi đưa G2 vào, mọi hiệu ứng khác đều rất nhỏ. Điều này có nghĩa là câu hỏi thực tế hơn là "học sinh uống rượu có điểm thấp hơn không" chính là "học sinh uống rượu có điểm kỳ trước thấp hơn không". Dữ liệu cho thấy có, nhưng đó là câu hỏi khác.
- **Cách xử lý G3 = 0 và cặp trùng khóa** là quyết định của phân tích, không phải thông tin từ codebook. Kết luận được kiểm tra lại ở kịch bản B, C, D.

## Tệp đầu ra (`outputs/alcohol-vs-g3/`)

- `analysis.py`: toàn bộ phân tích; `charts.py`: biểu đồ.
- `results_scenarios.csv`: kết quả theo kịch bản A–D; `joint_models.csv`, `subject_models.csv`: mô hình gộp và theo môn.
- `descriptives_by_level.csv`, `data_quality.csv`, `match_agreement.csv`, `analysis_sample.csv`.
- `chart_g3_by_alcohol.png`: G3 trung bình theo mức uống rượu; `chart_adjusted_effects.png`: hệ số điều chỉnh qua các kịch bản.
