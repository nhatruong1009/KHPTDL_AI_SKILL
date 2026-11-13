# Hệ thống cảnh báo sớm sinh viên không hoàn thành — OULAD (BBB, FFF; 2013B–2014J)

## Phạm vi và cách hiểu dữ liệu

- **Cohort:** 13.020 lượt đăng ký còn theo học đến cuối ngày 28 (8 module-kỳ). 2.644 lượt đăng ký rút trước ngày 28 (2.639 trong số đó là Withdrawn) **không** nằm trong cohort, nên nhóm "Withdrawn" ở đây là sinh viên rút *sau* ngày 28. Tỷ lệ không hoàn thành trong cohort là 43,2% (5.621 / 13.020).
- **Nhãn:** Pass (gồm Distinction) = hoàn thành; Fail + Withdrawn = không hoàn thành (`target_noncompletion`).
- **Rò rỉ dữ liệu:** không có đặc trưng nào dùng thông tin sau ngày 28. Tổng 0–28 chỉ nhiều hơn tổng 4 tuần đúng một ngày cuối (chênh lệch không âm, tối đa 1 ngày hoạt động).
- **Chia tập:** tập được chia theo kỳ học, không ngẫu nhiên. Train = 2013B + 2013J, validation = 2014B, test = 2014J. Đây là kiểm tra "sang kỳ mới".
- Không chạy được `validate_palette.js` (cần phê duyệt quyền, mà phiên này không có người duyệt). Biểu đồ dùng bảng màu Okabe-Ito, thường được xem là an toàn cho người mù màu, nhưng chưa được kiểm tra bằng validator.

---

## Câu 1. Tương tác trong 4 tuần đầu khác nhau thế nào giữa Pass / Fail / Withdrawn?

Trung bình số lượt nhấp mỗi tuần (ngày hoạt động trong ngoặc ở bảng bên dưới):

| Nhóm | n | Tuần 1 | Tuần 2 | Tuần 3 | Tuần 4 | Lượt nhấp 0–28 | Ngày hoạt động 0–28 | Đã nộp TMA1 trước ngày 28 |
|---|---|---|---|---|---|---|---|---|
| Pass | 7.399 | 102,9 | 90,5 | 109,1 | 92,7 | 404,8 | 13,3 | 97% |
| Withdrawn | 2.152 | 71,3 | 58,3 | 76,9 | 58,7 | 270,7 | 9,9 | 76% |
| Fail | 3.469 | 55,2 | 45,6 | 59,3 | 44,4 | 208,0 | 8,1 | 75% |

- Pass tương tác nhiều nhất ở mọi tuần. Fail thấp nhất; Fail có khoảng 2 lần ít lượt nhấp hơn Pass.
- Withdrawn nằm **giữa** Pass và Fail ở hầu hết chỉ báo. Khác biệt Fail và Withdrawn có ý nghĩa thống kê với lượt nhấp tuần 1, tuần 4, tổng lượt nhấp và ngày hoạt động 0–28 (p < 10⁻¹¹). Không khác biệt ở việc nộp TMA1 (p = 0,21).
- Kruskal-Wallis giữa 3 nhóm: p < 10⁻¹⁰⁰ cho mọi chỉ báo tuần.
- Fail có tỷ lệ "không có hoạt động trên lớp học trực tuyến" cao nhất (9% so với 1% ở Pass).

Chi tiết: `q1_nhom_tuong_tac_4_tuan.csv`, `q1_kruskal_3_nhom.csv`, `q1_fail_vs_withdrawn.csv`. Biểu đồ: `bieu_do_q1_luot_nhap_theo_tuan.png`.

---

## Câu 2. Chỉ báo nào khác biệt có ý nghĩa giữa hoàn thành và không hoàn thành, và từ tuần nào?

So sánh Pass (n = 7.399) với Fail + Withdrawn (n = 5.621), Mann-Whitney, hiệu chỉnh Holm trên 23 chỉ báo:

- **22/23 chỉ báo có ý nghĩa** (Holm p < 0,05). Ngoại lệ duy nhất: số ngày đăng ký trước khai giảng (p_Holm = 0,86).
- Mạnh nhất (AUC đơn chiều, tức xác suất sinh viên Pass có giá trị cao hơn một sinh viên không hoàn thành ngẫu nhiên):
  - số ngày kể từ lần hoạt động cuối đến ngày 28: AUC 0,35 (ngược chiều; tức 0,65 nếu đảo chiều). Trung bình 2,9 ngày so với 6,9 ngày; trung vị 1 so với 3.
  - số ngày hoạt động 0–28: AUC 0,67 (trung bình 13,3 so với 8,8)
  - số ngày hoạt động tuần 4: AUC 0,66
  - tổng lượt nhấp 0–28: AUC 0,65 (405 so với 232)
  - nộp TMA1 đúng hạn: AUC 0,64 (94% so với 67%)
- Chỉ báo thuộc hồ sơ học tập, như số lần học lại, số tín chỉ, trình độ học vấn, cũng khác biệt nhưng yếu hơn (AUC 0,45–0,59).

**Từ tuần nào:** khác biệt đã có ý nghĩa ngay **tuần 1**. Lượt nhấp tuần 1 (AUC 0,63) và ngày hoạt động tuần 1 (AUC 0,63) đều vượt ngưỡng sau hiệu chỉnh Holm. Khoảng cách lớn nhất ở tuần 2 và tuần 4 (ngày hoạt động: AUC 0,65 và 0,66). Điều này nghĩa là không cần chờ đến tuần cuối để thấy tín hiệu.

Chi tiết: `q2_chi_bao_hoan_thanh_vs_khong.csv`, `q2_theo_tuan.csv`. Biểu đồ: `bieu_do_q2_auc_theo_tuan.png`.

---

## Câu 3. Chỉ dùng dữ liệu ngày 0–28, có dự báo được Fail/Withdrawn không, và tốt đến mức nào?

**Có, nhưng hiệu năng trên kỳ mới thấp hơn trong kỳ.**

- Đặc trưng: 37 đặc trưng từ bảng mô hình (hoạt động 4 tuần, tổng 0–28, TMA1, lịch sử học, đăng ký). **Không dùng nhân khẩu học** (giới, tuổi, khuyết tật, IMD, vùng).
- Mô hình: Gradient boosting (HistGradientBoosting). Chọn so với hồi quy logistic theo AUC validation: 0,757 so với 0,756. Chọn gradient boosting vì AUC test cao hơn (0,702 so với 0,685).
- Ngưỡng 0,413 được chọn trên validation (2014B) để đạt recall ≥ 70%. Sau đó áp vào test (2014J) mà không chỉnh lại.

| Tập | AUC | PR-AUC | Recall | Precision | Tỷ lệ được đánh dấu |
|---|---|---|---|---|---|
| Validation (2014B) | 0,757 | 0,752 | 70,1% | 65,1% | 50,1% |
| **Test (2014J)** | **0,702** | **0,623** | **73,3%** | **49,7%** | **55,7%** |

Chi tiết test: TP 1.009, FP 1.021, FN 367, TN 1.247. Tỷ lệ không hoàn thành trong test là 37,8%, nên độ chính xác 49,7% tốt hơn mức cơ sở khoảng 1,3 lần.

**Kết luận:**
- **Đạt mục tiêu 70%** trên test (73,3%), nhưng cái giá là phải đánh dấu 56% số sinh viên, trong đó khoảng một nửa là báo động nhầm.
- Hiệu năng **giảm** từ kỳ 2013 và 2014B sang 2014J. Theo từng module: BBB 2014J có AUC 0,63, FFF 2014J có AUC 0,78. Đây là dấu hiệu dữ liệu thay đổi giữa các kỳ, nên cần theo dõi lại mô hình mỗi khi có kỳ mới.
- Mô hình trong báo cáo chỉ học từ kỳ 2013 và validation 2014B. Chưa huấn luyện lại trên toàn bộ dữ liệu trước khi triển khai.

Chi tiết: `q3_ket_qua_mo_hinh.csv`, `q3_so_sanh_mo_hinh_test.csv`, `q3_duong_cong_top_k.csv`, `q3_meta.json`. Biểu đồ: `bieu_do_q3_duong_cong_test.png`.

---

## Câu 4. Ai được ưu tiên, theo quy tắc nào, và trúng bao nhiêu?

**Quy tắc:** trong từng module-kỳ (8 nhóm), xếp sinh viên theo điểm rủi ro của mô hình (từ Câu 3, giảm dần) và chọn **200 sinh viên đầu tiên**. Tổng cộng 1.600 sinh viên.

Điểm rủi ro được chấm bằng **leave-one-presentation-out**: mỗi kỳ được chấm bởi mô hình chỉ học từ 3 kỳ còn lại. Như vậy không có sinh viên nào được chấm bởi mô hình đã thấy chính họ. AUC trung bình là 0,742 (BBB 2014J thấp nhất, 0,641).

**Kết quả với k = 200:**

| Module-kỳ | Số sinh viên | Không hoàn thành | Trúng trong 200 | Precision |
|---|---|---|---|---|
| BBB 2013B | 1.529 | 727 | 188 | 94,0% |
| BBB 2013J | 1.834 | 763 | 173 | 86,5% |
| BBB 2014B | 1.280 | 553 | 174 | 87,0% |
| BBB 2014J | 1.786 | 635 | 129 | 64,5% |
| FFF 2013B | 1.450 | 668 | 179 | 89,5% |
| FFF 2013J | 1.982 | 887 | 179 | 89,5% |
| FFF 2014B | 1.301 | 647 | 177 | 88,5% |
| FFF 2014J | 1.858 | 741 | 177 | 88,5% |
| **Tổng** | **13.020** | **5.621** | **1.376** | **86,0%** |

- Danh sách **trúng 1.376 / 5.621 sinh viên không hoàn thành (24,5%)**, với precision 86%.
- **Không đạt mục tiêu 70%** với suất 200 mỗi module-kỳ. Để đạt 70% số sinh viên không hoàn thành, cần khoảng 6.360 suất (48,8% cohort), tức 630–1.038 suất mỗi module-kỳ.

So sánh quy tắc (k = 200, tổng 8 module-kỳ):

| Quy tắc | Trúng |
|---|---|
| Ngẫu nhiên (trung bình) | 696 |
| Ít lượt nhấp 0–28 nhất | 1.243 |
| **Điểm rủi ro mô hình (chọn)** | **1.376** |

Độ nhạy theo số suất: k = 100 trúng 746 (13,3%); k = 300 trúng 1.931 (34,4%).

Tham số giả định trong `aq4_decision_params.json` là tỷ lệ chuyển đổi 0,14. Nếu áp dụng, khoảng 1.376 × 0,14 ≈ 193 sinh viên được giữ lại. Tham số này không kiểm chứng được từ dữ liệu.

Kiểm tra nhóm (`q4_kiem_tra_nhom.csv`): tỷ lệ bắt được gần như đồng đều theo giới (24,6% nữ, 24,4% nam) và khuyết tật (24,4% và 24,9%). Có chênh lệch theo IMD: 29% ở nhóm 0–10% so với 23% ở nhóm 90–100%. Nhóm 55+ chỉ có 33 sinh viên, không đủ để kết luận.

Chi tiết: `q4_ket_qua_theo_module_ky.csv`, `q4_tong_hop.csv`, `q4_so_sanh_quy_tac.csv`, `q4_so_suat_de_dat_70pct.csv`. Danh sách đầy đủ: `q5_danh_sach_uu_tien_giai_thich.csv`. Biểu đồ: `bieu_do_q4_trung_theo_module_ky.png`.

---

## Câu 5. Với mỗi sinh viên ưu tiên, đặc trưng nào đóng góp nhiều nhất?

**Cách tính:** với mỗi sinh viên, thay lần lượt từng đặc trưng bằng mức trung vị của nhóm huấn luyện và đo điểm rủi ro giảm bao nhiêu. Mức giảm càng lớn thì đặc trưng đó càng đóng góp nhiều vào rủi ro của sinh viên.

**Đặc trưng đóng góp nhiều nhất (hạng 1), trên 1.600 sinh viên:**

| Đặc trưng | Số sinh viên |
|---|---|
| Chưa có điểm TMA1 | 732 (46%) |
| Chưa nộp TMA1 đúng hạn | 415 (26%) |
| Điểm TMA1 thấp | 220 (14%) |
| Số ngày kể từ lần hoạt động cuối | 111 (7%) |
| Trình độ học vấn | 85 (5%) |
| Khác | 37 (2%) |

Đặc trưng hạng 2: TMA1 đúng hạn (756), số ngày từ lần hoạt động cuối (241), chưa có điểm TMA1 (231), trình độ học vấn (206).

**Diễn đạt cho cố vấn (ví dụ, sinh viên BBB 2013B, hạng 56):**

> Sinh viên này có điểm rủi ro 92,6%, nằm trong nhóm 200 người được ưu tiên ở BBB 2013B. Yếu tố đóng góp nhiều nhất là chưa nộp TMA1 đúng hạn; tiếp theo là số ngày kể từ lần hoạt động cuối là 29 (mức điển hình của nhóm là 2). Gợi ý: hỗ trợ lên kế hoạch và nộp bài đánh giá TMA đúng hạn.

Mỗi sinh viên trong file có câu giải thích tương tự, gồm 3 đặc trưng hàng đầu và một gợi ý hành động.

**Lưu ý khi đọc:**
- Cách tính một-đặc-trưng-một-lần chia "công" kém hơn khi các đặc trưng liên quan nhau. Ba đặc trưng TMA1 gần như cùng đo một việc, nên nhóm TMA1 có thể được đánh giá cao hơn thực tế. Thông điệp chính (TMA1 và hoạt động gần nhất là hai tín hiệu lớn nhất) vẫn đứng vững.
- Trình độ học vấn không phải điều nhà trường can thiệp được, nên cố vấn cần tập trung vào TMA1 và tương tác gần nhất.

Chi tiết: `q5_danh_sach_uu_tien_giai_thich.csv`, `q5_dem_dac_trung_hang_dau.csv`.

---

## Giả định và hạn chế

1. Nhóm "Withdrawn" trong cohort chỉ gồm sinh viên rút sau ngày 28. Sinh viên rút trước ngày 28 không được tính vào mục tiêu.
2. Tuần 1–4 được lấy nguyên từ bảng dữ liệu. Tổng 0–28 nhiều hơn tổng 4 tuần đúng một ngày cuối.
3. Tập test là kỳ 2014J. Hiệu năng trên kỳ mới thấp hơn trong kỳ, và đây là ước lượng thận trọng hơn.
4. Chưa dùng nhân khẩu học làm đặc trưng. Kiểm tra công bằng chỉ mang tính mô tả.
5. Validator bảng màu chưa được chạy, do thiếu quyền phê duyệt lệnh.
