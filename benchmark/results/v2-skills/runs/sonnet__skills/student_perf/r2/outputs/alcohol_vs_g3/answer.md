# Mức độ uống rượu và điểm cuối kỳ G3 (Toán + Bồ Đào Nha)

## Trả lời
**Có, nhưng mối liên hệ yếu đến vừa và chưa chắc là riêng của rượu.** Học sinh uống nhiều hơn có G3 thấp hơn rõ rệt về mặt thống kê, cả ngày thường (Dalc) lẫn cuối tuần (Walc):

- Spearman ρ với G3 (chuẩn hóa theo môn, trung bình theo học sinh, n = 659): **Dalc ρ = −0,19** (KTC 95% −0,26…−0,12; p = 5,2e-7); **Walc ρ = −0,18** (−0,25…−0,10; p = 4,9e-6). Sau hiệu chỉnh Holm cho 2 kiểm định vẫn p < 1e-5.
- Nhóm uống nhiều có G3 thấp hơn khoảng **1 điểm (thang 20)**, Cohen's d ≈ −0,4:
  - Dalc ≥ 2 so với Dalc = 1: 11,08 so với 12,12 điểm (−1,04), **d = −0,40** (KTC −0,56…−0,23), p(Welch) = 1,9e-6.
  - Walc ≥ 3 so với ≤ 2: −0,96 điểm, **d = −0,37** (−0,53…−0,21), p = 1,3e-5.
  - Walc ≥ 4 so với ≤ 3: 10,83 so với 12,06 (−1,23), **d = −0,47** (−0,65…−0,28), p = 3,9e-7.
- Rượu giải thích rất ít phương sai của G3: Kruskal-Wallis η² ≈ 0,033 cho cả Dalc và Walc (khoảng 3%), p ≈ 4e-5.
- **Sau khi kiểm soát yếu tố nhiễu, kết luận yếu đi.** Mô hình OLS (HC3) có cả Dalc và Walc cùng giới, tuổi, trường, địa chỉ, học vấn bố mẹ, studytime, goout: Dalc −0,10 độ lệch chuẩn/mức (−0,20…−0,01; p = 0,034), **Walc −0,04 (−0,11…0,03; p = 0,27, không còn ý nghĩa)**. Thêm failures và absences: Dalc −0,08 (p = 0,099), Walc −0,04 (p = 0,19). Phần lớn liên hệ thô của Walc gắn với việc đi chơi/đặc điểm học sinh khác, không phải bằng chứng riêng cho rượu.

## Bằng chứng
- Biểu đồ: [g3_theo_muc_ruou.png](g3_theo_muc_ruou.png) (G3 theo từng mức rượu), [do_ben_vung.png](do_ben_vung.png) (ρ qua các cách xử lý).
- Bảng: `chinh_spearman.csv`, `chinh_hai_nhom.csv`, `chinh_kruskal.csv`, `theo_muc.csv`, `hoi_quy_hieu_chinh.csv`, `nhay_cam.csv`, `g3_dang_ngo.csv`, `student_level.csv`.

| Mức | G3 TB Dalc (n) | G3 TB Walc (n) |
|---|---|---|
| 1 | 12,13 (461) | 12,25 (253) |
| 2 | 11,36 (119) | 12,07 (152) |
| 3 | 10,93 (45) | 11,65 (121) |
| 4 | 10,53 (17) | 10,82 (89) |
| 5 | 10,12 (17) | 10,85 (44) |

## Cách làm
1. **Học sinh xuất hiện ở cả hai file.** Dùng 13 thuộc tính khóa trong `student-merge.R`. Các khóa này không duy nhất (366 nhóm cho 382 dòng ghép), nên phép merge của file R tạo cặp chéo. Tôi ghép **1–1** trong từng nhóm khóa (Hungarian trên các thuộc tính ổn định, không dùng rượu/điểm), được **370 cặp**. Tổng cộng **674 học sinh duy nhất** (370 học cả hai môn, 25 chỉ Toán, 279 chỉ Bồ). Với cặp khớp, Dalc/Walc giống nhau 100% giữa hai file, nên không phải đổi giá trị. Mỗi học sinh là **một đơn vị**; G3 của học sinh học hai môn là trung bình hai điểm z (z tính trong từng môn) để không đếm đôi và không trộn thang điểm hai môn.
2. **G3 đáng ngờ.** 53 dòng có G3 = 0 (38 Toán, 15 Bồ). Cả 53 đều có absences = 0, trong khi chỉ 21,6% (Toán) và 36,1% (Bồ) học sinh có G3 > 0 vắng 0 buổi; 33 dòng có G2 > 0 nhưng G3 = 0. Điều này gợi ý đây là học sinh bỏ thi/bỏ học hoặc điểm bị ghi thiếu, không phải điểm thật bằng 0. **Phân tích chính loại các G3 = 0** (còn 659 học sinh). Điểm 0 không liên quan đến mức rượu (ρ = 0,02 cho Dalc, p = 0,61; −0,05 cho Walc, p = 0,21), nên loại chúng không làm lệch kết luận theo hướng nào.
3. **Kiểm định.** Spearman (bootstrap 2000 lần cho KTC), Cohen's d (bootstrap), Welch + Mann-Whitney, Kruskal-Wallis η², OLS với sai số HC3, hiệu chỉnh Holm.

## Độ bền vững
ρ vẫn âm trong mọi cách xử lý: giữ G3 = 0 (Dalc −0,18, Walc −0,13); chỉ Toán (−0,15/−0,19); chỉ Bồ (−0,20/−0,17); chỉ nhóm ghép không mơ hồ (−0,20/−0,18); chỉ 370 học sinh học cả hai môn (−0,22/−0,21). Gộp thô hai file (991 dòng, đếm đôi 370 học sinh) cho ρ gần như giống (−0,18/−0,18) nhưng KTC hẹp giả tạo vì quan sát không độc lập; không dùng làm kết quả chính.

## Giả định và lưu ý
- **Chỉ là liên hệ, không phải nhân quả.** Rượu được tự khai theo thang 1–5 (không phải lượng uống thật). Học sinh uống nhiều khác biệt ở nhiều mặt (đi chơi, từng trượt môn, vắng học). Chiều ngược lại cũng có thể xảy ra (điểm kém dẫn đến uống nhiều).
- Hiệu chỉnh không hoàn hảo: `failures` và `absences` có thể là biến trung gian chứ không phải nhiễu, nên tôi trình bày cả hai mô hình.
- Mức Dalc 4–5 chỉ có 17 học sinh mỗi mức nên KTC rộng; các ngưỡng nhị phân (≥2, ≥3, ≥4) là lựa chọn của tôi.
- Ghép học sinh dựa trên thuộc tính trùng nhau, không có ID thật; 12 cặp nằm trong nhóm khóa mơ hồ (kết quả không đổi khi loại chúng).
- Dữ liệu chỉ từ hai trường ở Bồ Đào Nha, không đại diện cho học sinh nói chung.
- Mã tái lập: `python -I outputs/alcohol_vs_g3/analysis.py` (chạy từ thư mục gốc dự án).
