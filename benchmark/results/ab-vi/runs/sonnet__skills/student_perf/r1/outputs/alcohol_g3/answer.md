# Uống rượu và điểm cuối kỳ G3 (Toán + Tiếng Bồ Đào Nha)

## Kết luận
**Có.** Học sinh uống rượu nhiều hơn có G3 thấp hơn, ở cả ngày thường (Dalc) lẫn cuối tuần (Walc). Mối liên quan có ý nghĩa thống kê nhưng **mức độ nhỏ đến trung bình**, và đây là quan hệ liên quan, không phải nhân quả.

Phân tích chính: 674 học sinh duy nhất, loại G3 = 0, còn 659 học sinh có G3 hợp lệ.

| Chỉ số | Dalc (ngày thường) | Walc (cuối tuần) |
|---|---|---|
| Spearman ρ (95% CI bootstrap) | −0,19 (−0,26; −0,11), p < 0,001 | −0,18 (−0,25; −0,10), p < 0,001 |
| Kruskal–Wallis ε² | 0,031 (p < 0,001) | 0,033 (p < 0,001) |
| G3 trung bình: nhóm uống nhiều vs ít* | chênh −1,45 điểm | chênh −1,36 điểm |
| Hedges g (95% CI) | −0,55 (−0,79; −0,31) | −0,52 (−0,72; −0,32) |
| Hồi quy thô: hệ số trên mỗi bậc | −0,56 điểm (−0,76; −0,36) | −0,40 điểm (−0,56; −0,25) |
| Hồi quy có kiểm soát** | −0,33 (−0,54; −0,12), p = 0,002 | −0,25 (−0,42; −0,09), p = 0,002 |

\* Dalc: ≥3 so với =1; Walc: ≥4 so với ≤2.
\** Kiểm soát: tuổi, học vấn bố/mẹ, thời gian học, số lần trượt, goout, giới, trường, địa chỉ, nguyện vọng học cao hơn. Sai số chuẩn HC3.

Mỗi bậc rượu tăng đi kèm G3 thấp hơn khoảng 0,3–0,6 điểm trên thang 20. Rượu giải thích chỉ khoảng 3–4% phương sai của G3 (ρ² ≈ 0,035). Khi đưa Dalc và Walc vào cùng một mô hình, hai biến chồng lấn nhau (tương quan cao). Lúc đó từng biến mất ý nghĩa riêng (p ≈ 0,09 và 0,08), nên không tách được biến nào "gây hại" hơn.

## Cách xử lý dữ liệu
1. **Học sinh xuất hiện ở cả hai file.** Ghép theo 13 thuộc tính trong `student-merge.R`. Khóa này **không duy nhất**: 8 dòng Toán và 23 dòng Văn trùng khóa. Vì vậy phép merge của R cho 382 dòng, đã bị thổi phồng do ghép nhiều–nhiều. Tôi ghép thêm 12 thuộc tính ổn định (guardian, studytime, famrel, goout, health…) và dùng ghép một–một tối ưu. Kết quả: **370 học sinh** trùng, tất cả khớp đủ 12/12 thuộc tính. Tổng số học sinh duy nhất là 395 + 649 − 370 = **674**. Mỗi học sinh được đếm một lần, nên không còn tính lặp mẫu. Với học sinh có hai môn, G3 là trung bình các môn hợp lệ; Dalc/Walc lấy trung bình hai file, vì chúng giống nhau ở 97–99% cặp.
2. **G3 = 0 đáng ngờ.** Có 38 dòng Toán và 15 dòng Văn (51 học sinh). Cả 53 dòng đều có `absences = 0`, và G2 thường bằng 0 hoặc rất thấp. Đây gần như chắc chắn là bỏ thi hoặc bỏ học, không phải điểm thật. Tôi coi chúng là thiếu dữ liệu ở phân tích chính. Tỉ lệ G3 = 0 không khác nhau có ý nghĩa giữa nhóm uống nhiều và ít (Fisher p = 0,15–0,70), nên việc loại bỏ không làm lệch theo mức uống rượu theo cách đo được.
3. **Độ nhạy.** Nếu giữ G3 = 0, mối liên quan yếu đi nhưng vẫn cùng chiều: Dalc ρ = −0,17, g = −0,37; Walc ρ = −0,13, g = −0,35. Sau khi kiểm soát, Dalc có p = 0,053 và Walc p = 0,125, tức là không còn rõ. Chỉ riêng môn Văn thì kết quả ổn định (ρ ≈ −0,2, g ≈ −0,5…−0,7). Riêng môn Toán thì yếu hơn và phụ thuộc vào xử lý G3 = 0: loại 0 cho ρ ≈ −0,15…−0,19, giữ 0 cho ρ ≈ −0,10…−0,12 (Welch p > 0,2). Xem `ket_qua_tuong_quan.csv` và `forest_hedges_g.png`.

## Hạn chế
- Dữ liệu quan sát: không loại trừ được yếu tố gây nhiễu (bạn bè, động lực học, hoàn cảnh gia đình) hoặc quan hệ ngược chiều. Kiểm soát biến chỉ giảm bớt, không loại hết.
- Rượu là thang tự báo cáo 1–5; các mức 4–5 của Dalc chỉ có 17 học sinh mỗi mức, nên CI rất rộng.
- Hồi quy OLS giả định tuyến tính trên thang thứ tự. Kết quả Spearman và Kruskal làm kiểm chứng không tham số và cùng kết luận.
- Ghép học sinh dựa vào thuộc tính trùng nhau, không có ID thật; sai lệch nhỏ vẫn có thể xảy ra.
- Có nhiều phép thử (nhiều biến, nhiều tập con), nhưng kết quả chính rất nhất quán nên không phụ thuộc vào một p-value đơn lẻ.

## Tệp
`analysis.py`, `match.py`, `student_level.csv`, `ket_qua_tuong_quan.csv`, `ket_qua_hoi_quy.csv`, `g3_bang_0_theo_ruou.csv`, `g3_theo_ruou.png`, `forest_hedges_g.png`.
