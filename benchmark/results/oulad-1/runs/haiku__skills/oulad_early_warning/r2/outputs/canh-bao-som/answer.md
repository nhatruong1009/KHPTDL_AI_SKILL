# Cảnh báo sớm sinh viên OULAD — mốc quyết định cuối ngày 28

## Trả lời ngắn

1. **Tương tác 4 tuần đầu:** Pass cao nhất, Fail thấp nhất ở hầu hết chỉ số, Withdrawn nằm giữa. Trung vị lượt truy cập tuần 1 là 53 (Pass), 33 (Withdrawn), 20 (Fail). Riêng số ngày truy cập tuần 1 thì Withdrawn và Fail bằng nhau (trung vị 2).
2. **Chỉ báo khác biệt:** 28 trên 34 chỉ báo khác biệt có ý nghĩa giữa nhóm hoàn thành (Pass + Distinction) và không hoàn thành (Fail + Withdrawn). Khác biệt xuất hiện **ngay từ tuần 1** và duy trì đến tuần 4, với lượt truy cập lẫn số ngày truy cập. Nổi bật nhất là tỉ lệ nộp TMA1 đúng hạn (93,6% so với 66,5%).
3. **Dự báo bằng dữ liệu đến ngày 28:** Có dự báo được, mức vừa phải. AUC trên tập test 2014J là **0,685** (validation 0,756). Với ngưỡng chọn trên validation, mô hình bắt được **63%** sinh viên không hoàn thành trên test (chưa đạt 70%). Để đạt 70% phải liên hệ khoảng **52%** số sinh viên mỗi module-kỳ.
4. **Danh sách 200 mỗi module-kỳ:** Xếp hạng theo điểm rủi ro của mô hình (giảm dần), đồng hạng thì ưu tiên ít lượt truy cập đến ngày 28. Trên 2014J, danh sách 400 sinh viên **trúng 284** (71%), tương đương luật đơn giản "ít click nhất" (289). Danh sách này chỉ bắt được **21%** tổng số sinh viên không hoàn thành (284/1.376). **Mục tiêu 70% không khả thi với giới hạn 200**: ngay cả xếp hạng hoàn hảo cũng chỉ bắt tối đa khoảng 28%.
5. **Giải thích cho cố vấn:** Yếu tố đóng góp nhiều nhất là lượt truy cập đến ngày 28 thấp (90% danh sách), chưa có hoặc điểm TMA1 thấp (57% và 43%), và số ngày truy cập thấp (26%). Mỗi sinh viên có 2–3 câu giải thích trong `q4_danh_sach_uu_tien_test_2014J_kem_giai_thich.csv`.

---

## 1. Tương tác trong 4 tuần đầu theo nhóm kết quả

**Quần thể:** 13.020 sinh viên còn active tại ngày 28 (`aq3_model_table`). Trong đó Pass 6.053, Fail 3.469, Withdrawn 2.152. Distinction (1.346) không nằm trong câu hỏi ba nhóm nên bị loại khỏi bảng này.

| Chỉ tiêu (trung vị) | Pass | Fail | Withdrawn |
|---|---|---|---|
| Lượt truy cập tuần 1 / 2 / 3 / 4 | 53 / 45 / 56 / 38 | 20 / 15 / 23 / 10 | 33 / 24,5 / 36 / 21 |
| Số ngày có truy cập tuần 1 / 2 / 3 / 4 | 3 / 3 / 3 / 3 | 2 / 1 / 2 / 1 | 2 / 2 / 2 / 2 |
| Lượt truy cập đến ngày 28 | 238 | 112 | 160,5 |

- Kruskal–Wallis cho mọi chỉ tiêu đều p < 10⁻⁹⁰.
- So sánh từng cặp (BH-điều chỉnh, q < 10⁻¹¹): Fail thấp hơn Pass với hiệu độ khoảng −0,27 đến −0,37. Withdrawn thấp hơn Pass với hiệu độ khoảng −0,16 đến −0,22. Withdrawn **cao hơn** Fail với hiệu độ khoảng +0,11 đến +0,14.

**Lưu ý:** Nhóm Withdrawn chỉ gồm sinh viên rút sau ngày 28 (2.152/4.791 người rút). Những người rút trước ngày 28 đã bị loại khỏi quần thể nên nhóm này trông tích cực hơn thực tế.

Biểu đồ: `q1_tuong_tac_theo_tuan.png`. Bảng: `q1_tuong_tac_4_tuan_theo_nhom.csv`, `q1_so_sanh_cap_nhom.csv`.

## 2. Chỉ báo khác biệt giữa hoàn thành và không hoàn thành

**Phương pháp:** Hoàn thành = Pass + Distinction (target = 0), không hoàn thành = Fail + Withdrawn (target = 1). Kiểm định Mann–Whitney cho chỉ tiêu liên tục và chi-square cho chỉ tiêu nhị phân, hiệu chỉnh BH trên 34 chỉ tiêu. Một chỉ tiêu được coi là khác biệt khi q < 0,05 và hiệu độ đủ lớn (|Cliff's δ| ≥ 0,147, hoặc chênh lệch tỉ lệ ≥ 0,05).

**Khác biệt theo tuần (hoàn thành vs không hoàn thành):**

| Tuần | Lượt truy cập: trung vị | δ | Số ngày truy cập: trung vị | δ |
|---|---|---|---|---|
| 1 | 59 vs 24 | −0,26 | 3 vs 2 | −0,26 |
| 2 | 50 vs 18 | −0,30 | 3 vs 1 | −0,31 |
| 3 | 60 vs 27 | −0,26 | 3 vs 2 | −0,30 |
| 4 | 43 vs 13 | −0,29 | 3 vs 2 | −0,31 |

Lượt truy cập lũy kế cũng có ý nghĩa từ tuần 1 (δ −0,26) và tăng dần đến ngày 28 (δ −0,31).

**Các chỉ báo khác biệt mạnh nhất (đến ngày 28):**
- Số ngày có truy cập đến ngày 28: δ −0,35.
- Đã nộp TMA1 trước ngày 28: 97,3% (hoàn thành) so với 75,5% (không hoàn thành).
- Nộp TMA1 đúng hạn: 93,6% so với 66,5% (người chưa nộp được tính là "không").
- Điểm TMA1 thấp hơn ở nhóm không hoàn thành, δ −0,22.

**Không khác biệt đáng kể:** Thay đổi lượt truy cập tuần 1→4 (δ −0,04), số tín chỉ (δ 0,06), thời điểm đăng ký (δ ≈ 0), đăng ký muộn, đã học module ở kỳ trước (chênh lệch tỉ lệ 0,035). Số lần học lại trước đây có p rất nhỏ nhưng hiệu độ chỉ 0,10 nên không được coi là khác biệt đáng kể.

Biểu đồ: `q2_hieu_do_theo_tuan.png`. Bảng: `q2_chi_bao_hoan_thanh_vs_khong.csv`.

## 3. Dự báo chỉ dùng dữ liệu đến ngày 28

**Thiết lập:** 34 đặc trưng, tất cả tính đến ngày 28 (tuần 1–4, lượt truy cập theo loại tài nguyên, TMA1, lịch sử học, thời điểm đăng ký). Huấn luyện trên 2013B + 2013J (n = 6.795), chọn ngưỡng trên 2014B (n = 2.581), đánh giá trên 2014J (n = 3.644). Tỉ lệ không hoàn thành: 44,8% / 46,5% / 37,8%.

Chọn hồi quy logistic vì dễ giải thích và đóng góp từng đặc trưng cần cho câu 5. Gradient boosting cho kết quả gần tương đương.

| Mô hình | AUC validation | AUC test | AP test (nền 0,378) | Bắt được 70% trên validation → trên test: recall / tỉ lệ được liên hệ |
|---|---|---|---|---|
| Hồi quy logistic (chọn) | 0,756 | 0,685 | 0,540 | 63% (ngưỡng từ validation) / cần 52% |
| Gradient boosting | 0,753 | 0,691 | 0,591 | 65% / cần 53% |
| Cơ sở: ít lượt truy cập đến ngày 28 | 0,647 | 0,652 | 0,541 | 70% / cần 58% |

**Kết luận:** Mô hình phân biệt được rủi ro (AUC 0,69–0,76), nhưng hiệu quả giảm mạnh trên kỳ 2014J (tỉ lệ nền thấp hơn và AUC thấp hơn). Ngưỡng chọn trên validation chỉ đạt 63% trên test, không đạt 70%. Để đạt 70%, phải liên hệ khoảng 52% sinh viên, tức khoảng 920 (BBB) và 960 (FFF) mỗi module-kỳ, gấp gần 5 lần giới hạn 200.

Biểu đồ: `q3_duong_bat_duoc_tren_test.png`. Bảng: `q3_do_luong_du_bao.csv`, `q3_he_so_hoi_quy_logistic.csv`.

## 4. Ưu tiên 200 sinh viên mỗi module-kỳ

**Quy tắc đề xuất:** Với mỗi module-kỳ, xếp sinh viên theo điểm rủi ro của hồi quy logistic (giảm dần). Đồng hạng thì ưu tiên người có ít lượt truy cập đến ngày 28. Lấy 200 người đầu tiên.

**Kết quả trên tập test 2014J** (mô hình huấn luyện trên 2013):

| Module-kỳ | Số sinh viên | Không hoàn thành | Trúng trong 200 | Tỉ lệ trúng | Ngẫu nhiên kỳ vọng |
|---|---|---|---|---|---|
| BBB 2014J | 1.786 | 635 | 108 | 54% | 71 |
| FFF 2014J | 1.858 | 741 | 176 | 88% | 80 |
| **Tổng** | 3.644 | 1.376 | **284 / 400 (71%)** | | 151 |

Luật "ít lượt truy cập đến ngày 28" trúng 289/400 (72%) trên cùng tập. Trên validation 2014B, mô hình trúng 352/400 so với 314/400 của luật cơ sở. Kiểm định chéo theo kỳ (giữ từng kỳ ra để kiểm tra, 8 module-kỳ, 1.600 liên hệ): mô hình trúng **1.356** (85%) so với 1.243 (78%) của luật cơ sở.

**Đánh giá:** Mô hình nhỉnh hơn luật đơn giản một cách nhất quán trên validation và kiểm định chéo, nhưng trên 2014J thì ngang bằng. Nên dùng mô hình, kèm luật đơn giản làm đối chiếu.

**Giới hạn của nhân lực:** Với 200 liên hệ mỗi module-kỳ, dù xếp hạng hoàn hảo thì recall tối đa khoảng 28% (kiểm định chéo: 28,5%). Mô hình đạt 24,1% (1.356/5.621).

Biểu đồ: `q4_trung_theo_module_ky.png`. Bảng: `q4_hieu_qua_200_tren_test.csv`, `q4_hieu_qua_200_tren_validation.csv`, `q4_kiem_dinh_cheo_8_module_ky.csv`, `q4_kiem_dinh_cheo_co_so_it_click.csv`, `q4_auc_kiem_dinh_cheo.csv`.

## 5. Yếu tố đóng góp nhiều nhất cho từng sinh viên trong danh sách

**Phương pháp:** Với hồi quy logistic, đóng góp của mỗi đặc trưng vào log-odds = hệ số × (giá trị đã chuẩn hóa). Lấy 3 đóng góp dương lớn nhất mỗi sinh viên, rồi viết thành 2–3 câu tiếng Việt không chuyên. Áp dụng cho 400 sinh viên của danh sách 2014J.

**Yếu tố xuất hiện nhiều nhất trong top 3:**
- Tổng lượt truy cập đến ngày 28 thấp: 90%.
- Chưa có điểm TMA1 (chưa nộp trước ngày 28): 57%.
- Điểm TMA1 thấp: 43%.
- Số ngày có truy cập đến ngày 28 ít: 26%.
- Không nộp TMA1 đúng hạn: 24%.
- Lâu chưa truy cập lại tính đến ngày 28: 22%.
- Trình độ học vấn ban đầu thấp: 20%.

**Ví dụ câu cho cố vấn** (sinh viên hạng 1, BBB 2014J):
> Sinh viên 654923 (module BBB, kỳ 2014J) nằm trong nhóm ưu tiên cao nhất của module-kỳ này (hạng 1 trong 200). Các yếu tố đẩy nguy cơ lên nhiều nhất là: điểm TMA1 là 1 (trung vị 77); tổng lượt truy cập đến ngày 28 là 0 (trung vị 205); nộp TMA1 trễ 8 ngày so với hạn. Đây là mối liên hệ trong dữ liệu, không phải nguyên nhân chắc chắn; nên trò chuyện trực tiếp để hiểu hoàn cảnh trước khi kết luận.

Tệp: `q4_danh_sach_uu_tien_test_2014J_kem_giai_thich.csv` (cột `giai_thich_cho_co_van`). Cột `ket_qua_thuc_te_chi_de_danh_gia` chỉ dùng để đánh giá, không dùng khi ra quyết định. Tần suất: `q5_tan_suat_yeu_to_trong_danh_sach.csv`.

Chúng tôi không đưa xác suất thô vào câu giải thích vì xác suất có thể bị lệch khi tỉ lệ không hoàn thành đổi theo kỳ (ví dụ 2014J thấp hơn 2013).

---

## Phương pháp và giả định

- **Quần thể:** `aq3_model_table.csv`, 13.020 sinh viên còn active tại ngày 28, không trùng khóa. Kết quả cuối kỳ được ghép từ `context_all_registrations.csv` (khớp 100%).
- **Mục tiêu:** `target_noncompletion` = 1 khi Fail hoặc Withdrawn (đã kiểm tra khớp với `final_result`).
- **Rò rỉ dữ liệu:** Không dùng `flag_high_activity` (cờ dẫn xuất) và `log_clicks_0_28` (trùng thông tin). Điểm TMA1 chỉ có khi đã nộp trước ngày 28. Các tổng theo tuần khớp với bảng tổng.
- **Nhân khẩu học:** Bảng model không chứa giới tính, khuyết tật, độ tuổi, vùng hay IMD, nên mô hình không dùng các yếu tố này.
- **Tuần 1–4:** Giả định tương ứng ngày 0–27. `clicks_0_28` bao gồm cả ngày 28, nên lệch với tổng tuần ở một số sinh viên.
- **Tham số quyết định** (`aq4_decision_params.json`): dùng giới hạn 200 mỗi module-kỳ. Không dùng `assumed_conversion_rate = 0,14` vì không kiểm chứng được trong dữ liệu và không cần cho việc xếp hạng.
- **Đánh giá:** Huấn luyện trên 2013, chọn ngưỡng trên 2014B, đánh giá trên 2014J. Kiểm định chéo theo kỳ là kiểm tra độ ổn định.
- **Tái lập:** `python outputs/canh-bao-som/analysis.py` từ thư mục dự án. Nhật ký: `run_log.txt`. Chỉ số: `metrics.json`.

## Giới hạn

- Kết quả là **liên quan, không phải nhân quả**. Điểm rủi ro không cho biết liệu liên hệ có làm thay đổi kết quả hay không.
- **Trôi dạt theo kỳ:** AUC giảm trên 2014J (0,69 so với 0,75–0,76 ở các kỳ khác). Cần theo dõi hiệu quả thực tế mỗi kỳ.
- **Nhóm Withdrawn bị chọn lọc:** Chỉ gồm người rút sau ngày 28, nên không phản ánh toàn bộ người rút.
- **Xác suất chưa hiệu chỉnh:** Không dùng xác suất thô làm ngưỡng tuyệt đối.
- **Không có thông tin ngoài VLE:** Hoàn cảnh cá nhân, tài chính, sức khỏe không có trong dữ liệu. Đây là lý do cố vấn cần trò chuyện trực tiếp.
- **Trần 200 liên hệ** là ràng buộc cứng: nếu nhà trường muốn đạt 70% không hoàn thành, cần nhân lực lớn hơn nhiều, hoặc chấp nhận bắt được khoảng 20–25%.
