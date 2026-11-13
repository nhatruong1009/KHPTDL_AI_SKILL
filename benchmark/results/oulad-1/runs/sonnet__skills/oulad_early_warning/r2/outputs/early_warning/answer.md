# Hệ thống cảnh báo sớm OULAD (BBB, FFF) - mốc cuối ngày 28

**Phạm vi:** 13.020 lượt đăng ký còn theo học đến hết ngày 28 (BBB + FFF, 4 kỳ 2013B-2014J). Tỷ lệ không hoàn thành (Fail + Withdrawn) = 43,2%.
Mọi số liệu đến từ `analysis.py` (cùng thư mục); log đầy đủ ở `run_log.txt`.
Cách chia dữ liệu theo thời gian: **train** = 2013B + 2013J, **validation** = 2014B, **test** = 2014J (chỉ dùng để báo cáo cuối).

## Trả lời ngắn
1. Nhóm **Pass** học nhiều hơn rõ rệt ngay từ tuần 1: trung vị 257 lượt click / 12 ngày hoạt động trong 28 ngày đầu, so với **Withdrawn 160,5 / 9** và **Fail 112 / 7**. Fail thấp nhất, không phải Withdrawn.
2. Gần như mọi chỉ báo hoạt động trên VLE và việc nộp bài TMA1 đều khác biệt có ý nghĩa (Mann-Whitney, hiệu chỉnh Bonferroni); khác biệt **đã có từ tuần 1** (Cliff's delta ≈ 0,26) và tăng nhẹ lên ≈ 0,30 ở tuần 2-4. Mạnh nhất: số ngày hoạt động (δ = 0,35), click trang chủ (0,33), số ngày kể từ lần học cuối (-0,30), click diễn đàn (0,30).
3. **Dự báo được ở mức vừa phải, chưa đạt kỳ vọng 70%** ở ngưỡng vận hành chọn trên validation. Trên test (2014J): AUC = 0,72 (KTC 95% 0,71-0,74). Để bắt 70% sinh viên không hoàn thành phải gắn cờ **khoảng 51%** sinh viên (độ chính xác ~53%); ngưỡng chọn từ validation chỉ bắt được **65,8%**.
4. Với 200 người/module-kỳ, nên xếp hạng theo điểm rủi ro (hoặc quy tắc "chưa nộp TMA1 rồi ít ngày hoạt động"). Danh sách 400 người (2 module-kỳ test) **trúng 291 người (72,8%)** với mô hình, so với 37,8% nếu chọn ngẫu nhiên; nhưng chỉ bao phủ **21,2%** tổng số sinh viên không hoàn thành (291/1.376) - **không thể đạt 70% với K = 200**.
5. Đóng góp lớn nhất vào điểm rủi ro: số ngày vào học, bài TMA1 (chưa nộp/muộn), lượng truy cập học liệu, hồ sơ nền và khoảng cách từ lần học gần nhất. Diễn đạt cho cố vấn ở mục 5 và file `q5_priority_list_with_reasons.csv` (từng sinh viên).

## 1. Tương tác 4 tuần đầu theo kết quả (`q1_*`, biểu đồ `q1_weekly_engagement.png`)
| Nhóm | n | Click 0-28 (trung vị) | Ngày hoạt động (trung vị) | % không hoạt động VLE | % nộp TMA1 trước ngày 28 |
|---|---|---|---|---|---|
| Pass | 7.399 | 257 | 12 | 0,9% | 97,3% |
| Withdrawn | 2.152 | 160,5 | 9 | 7,4% | 76,4% |
| Fail | 3.469 | 112 | 7 | 9,1% | 74,9% |

- Mỗi tuần, trung vị click của Pass là 43-60, Withdrawn 21-36, Fail 10-23. Tỷ lệ tuần "không click nào": Pass 8-12%, Withdrawn 20-27%, Fail 25-34%.
- Kruskal-Wallis cho cả click và số ngày hoạt động: p < 1e-200. Kiểm định từng cặp (Bonferroni) cũng đều có ý nghĩa; Fail < Withdrawn < Pass.
- Lưu ý: bảng theo tuần (`aq1`) có 12.904 sinh viên, ít hơn bảng chẩn đoán (13.020); tôi dùng bảng tuần cho biểu đồ theo tuần và bảng chẩn đoán cho tổng 0-28.

## 2. Chỉ báo khác biệt giữa hoàn thành và không hoàn thành (`q2_*`)
- Đã kiểm định 36 chỉ báo, hiệu chỉnh Bonferroni; 35/36 có ý nghĩa, và **cả 8 module-kỳ đều cùng chiều** cho 35 chỉ báo đó. Chỉ `registration_lead_days` không có ý nghĩa (δ ≈ 0). Với n lớn, p-value gần như vô nghĩa nên cần nhìn **độ lớn hiệu ứng**.
- Hiệu ứng "vừa" (|δ| 0,24-0,35): số ngày hoạt động 0-28 (0,35), click trang chủ (0,33), số ngày hoạt động tuần 4 (0,31), click 0-28 (0,31), click diễn đàn (0,30), ngày kể từ lần học cuối (-0,30), nộp TMA1 đúng hạn (0,27), số ngày nộp TMA1 sớm hơn hạn (0,24), click tuần 1 (0,26).
- Hiệu ứng "nhỏ": click quiz, tài liệu, nội dung bài học, liên kết ngoài, trình độ học vấn (0,17-0,20). Không đáng kể: số lần học lại, tín chỉ.
- **Từ tuần nào?** Từ **tuần 1**: click tuần 1 δ = 0,26 (Pass so với Fail 0,30; Pass so với Withdrawn 0,19); chênh lệch tăng nhẹ ở tuần 2 và vẫn ổn định đến tuần 4. Ngay cả click **trước khi khóa bắt đầu** đã khác (δ = 0,26) - tức là tín hiệu có thể thấy rất sớm.
- Hình: `q2_top_indicators.png`, `q2_effect_by_week.png`.

## 3. Dự báo chỉ bằng dữ liệu ngày 0-28 (`q3_*`, `q3_model_performance.png`)
Mục tiêu: `target_noncompletion`. Đặc trưng: hành vi VLE 0-28, TMA1 đến ngày 28, thông tin đăng ký/học tập. Không dùng nhân khẩu học (giữ cho kiểm tra công bằng). Chuẩn hóa/huấn luyện chỉ trên train; chọn mô hình và ngưỡng trên validation; test chỉ báo cáo.

| Mô hình | AUC val | AUC test | PR-AUC test | Recall test @ngưỡng val | Precision test | % gắn cờ |
|---|---|---|---|---|---|---|
| Logistic (đã chọn) | 0,761 | **0,723** | 0,635 | 65,8% | 53,0% | 46,9% |
| Gradient boosting | 0,762 | 0,742 | 0,659 | 68,8% | 55,3% | 47,0% |
| Baseline: ít click | 0,647 | 0,652 | 0,541 | 70,4% | 45,2% | 58,8% |
| Baseline: chưa nộp TMA1 + ít ngày | 0,697 | 0,686 | 0,615 | 71,4% | 47,2% | 57,1% |

- Tỷ lệ không hoàn thành ở test là 37,8%, nên precision 53% là cải thiện thực chất nhưng vẫn có gần một nửa người bị gắn cờ sẽ hoàn thành.
- Chọn Logistic vì AUC validation ngang gradient boosting (chênh < 0,01) và giải thích được cho Q5. Gradient boosting tốt hơn nhẹ ở test.
- **Mục tiêu 70%:** ngưỡng chọn trên validation cho recall 70% ở validation nhưng chỉ 65,8% ở test (phân phối thay đổi giữa các kỳ). Để đạt 70% trên test phải gắn cờ 50,8% sinh viên. Các baseline đạt ≥70% chỉ vì gắn cờ nhiều hơn (57-59%) với precision thấp hơn.
- Hiệu chỉnh: Brier 0,200 (test); bảng deciles trong `q3_calibration_test_deciles.csv`.
- **Phát hiện chất lượng dữ liệu:** ở BBB 2014J, 38% sinh viên có `tma1_score` = 1 (các kỳ khác không có), phần còn lại ≈ 100 - thang điểm khác các kỳ khác. Nếu giữ nguyên, mô hình coi đó là điểm rất thấp và AUC test tụt xuống 0,686 (BBB 2014J: 0,62). Tôi gán các điểm này bằng trung vị của train (module-kỳ nào có >10% điểm = 1) và báo kết quả cả hai cách trong `q3_sensitivity_tma1_scale_artifact.csv`. Đây là phán đoán của tôi; nên xác nhận với bộ phận dữ liệu của trường. Hiệu năng ở BBB 2014J (AUC 0,64) vẫn kém FFF 2014J (0,79).

## 4. Quy tắc ưu tiên với K = 200 mỗi module-kỳ (`q4_*`, `q4_priority_list.png`)
Quy tắc: xếp theo điểm rủi ro giảm dần trong từng module-kỳ, lấy 200 người đầu. Trên tập test (BBB 2014J, FFF 2014J; 400 người):

| Quy tắc (K = 200) | Trúng | Precision | Recall | Ước tính được hỗ trợ thành công* |
|---|---|---|---|---|
| Mô hình logistic | 291 | 72,8% | 21,2% | ~41 |
| Chưa nộp TMA1, rồi ít ngày hoạt động | 322 | 80,5% | 23,4% | ~45 |
| Ít click nhất 0-28 | 288 | 72,0% | 20,9% | ~40 |
| Ngẫu nhiên | ~151 | 37,8% | 11,0% | ~21 |

\*Giả định 14% chuyển đổi (`aq4_decision_params.json`) - đây là giả định của nhà trường, không đo được từ dữ liệu.

- Theo module-kỳ: FFF 2014J trúng 173/200 (86,5%), BBB 2014J trúng 118/200 (59,0%; tỷ lệ nền 35,6%).
- Tổng không hoàn thành ở 2 module-kỳ test là 1.376, nên 400 liên hệ tối đa bao phủ 29% ngay cả khi hoàn hảo. K = 100 / 300: precision 77% / 70,2%, recall 11,2% / 30,6% (mô hình).
- **So sánh:** trên validation mô hình thắng (88,3% so với 82,8% của quy tắc TMA1), trên test quy tắc đơn giản TMA1 thắng (80,5% so với 72,8%). Chênh lệch này không nhất quán, nên **khuyến nghị**: dùng quy tắc minh bạch "chưa nộp TMA1 trước ngày 28, sau đó ít ngày hoạt động nhất" làm cơ sở (không nộp TMA1 → 81-93% không hoàn thành ở cả 8 module-kỳ), và dùng mô hình để bổ sung phần còn lại (đặc biệt ở BBB, nơi chỉ ~6% sinh viên chưa nộp TMA1). Nên theo dõi precision thực tế mỗi kỳ.
- Công bằng (test, `q4_audit_flag_rate_by_group.csv`): tỷ lệ vào danh sách nữ 10,3% so với nam 11,7%; có khuyết tật 12,9% so với không 10,8%. Chênh lệch nhỏ, nhưng nên theo dõi.
- Để bắt ≥70% cần mở rộng năng lực (hoặc dùng kênh rẻ hơn như nhắn tin tự động cho nhóm rủi ro trung bình) - ngoài 200 cuộc liên hệ trực tiếp.

## 5. Lý do rủi ro cho từng sinh viên ưu tiên (`q5_*`)
Cách tính: với mô hình logistic, mỗi đặc trưng đóng góp = hệ số × (giá trị chuẩn hóa so với sinh viên trung bình của train); gộp các đặc trưng tương quan thành 7 chủ đề rồi lấy 3 chủ đề lớn nhất. File `q5_priority_list_with_reasons.csv` có 400 sinh viên, mỗi người kèm 2-3 câu viết sẵn cho cố vấn (cột `ghi_chu_co_van`).

Số sinh viên (trong 400 người) có chủ đề này trong top-3: số ngày vào học 333, bài TMA1 245, hồ sơ nền 241, lượng truy cập học liệu 227, khoảng cách từ lần học gần nhất 117, xu hướng học giảm 20, chuẩn bị trước khóa 17.

Ví dụ lời nhắn (sinh viên đầu danh sách BBB, số liệu thật của sinh viên): *"Sinh viên này được ưu tiên chủ yếu vì bài TMA1 nộp muộn hoặc kết quả chưa tốt, lượng truy cập học liệu chỉ 70 lượt click trong 28 ngày đầu (trung vị toàn khóa: 192) và chỉ vào học 3 ngày trong 29 ngày đầu (trung vị: 10). Nên liên hệ sớm để hỏi về khó khăn và hỗ trợ lịch học."*

## Hạn chế
- Dữ liệu quan sát: chỉ cho thấy **tương quan**, không chứng minh việc học ít *gây ra* trượt/rút lui. Các "lý do" ở Q5 là yếu tố làm tăng điểm rủi ro, không phải nguyên nhân.
- Chỉ gồm sinh viên còn theo học đến hết ngày 28; những người rút trước đó nằm ngoài phạm vi.
- Test chỉ gồm một kỳ (2014J) và 2 module; kết quả có thể thay đổi ở kỳ khác (AUC validation 0,76 so với test 0,72). Nên huấn luyện lại hàng kỳ và theo dõi.
- Gộp Fail và Withdrawn: hai nhóm có hành vi khác nhau (Fail thấp nhất), có thể cần can thiệp khác nhau.
- Mô hình dùng điểm TMA1; thang điểm BBB 2014J bất thường đã được xử lý như mô tả ở mục 3.
