# oulad_early_warning · sonnet__noskills · r1

| | |
|---|---|
| Điểm overall / accuracy / quality | 61.5 / 62.5 / 60.0 |
| Thời gian · chi phí · số turn | 167.1 s · $0.458 · 13 |
| Skill đã nạp (theo thứ tự) | (không có) |
| Lỗi công cụ | 4 |

## Các bước

1. Bash: `cd data; ls -la; for f in *; do echo == $f; head -3 "$f" | cut -c1-600; wc -l "$f"; done`  
  ↳ **lỗi:** A variable in this command can't be checked before it runs
2. Bash: `cd data; ls -la; for f in *; do echo "== $f"; head -3 "$f" | cut -c1-600; wc -l "$f"; done`  
  ↳ **lỗi:** A variable in this command can't be checked before it runs

> Tránh biến vòng lặp.

3. Bash: `ls -la data; head -c 800 data/*.csv | cut -c1-800; wc -l data/*`
4. Bash: `cd data; cat aq4_decision_params.json; python3 -I -c " import pandas as pd c=pd.read_csv('context_all_registrations.csv');print(c.groupby(['split','code_presentation']).size().unstack());print(c.describe(include='all').T.iloc[:,:4]) print(c.groupby(['active_d28','unregistered_by_d28','registered_af…`
5. Bash: `cd /root/.cache/skill-bench/runs/oulad-1/sonnet__noskills/oulad_early_warning/r1/workspace; python3 -I -c " import pandas as pd m=pd.read_csv('data/aq3_model_table.csv') print(m.describe().T[['mean','min','max']].to_string()) print(m.groupby(['code_module','code_presentation','split']).size()) prin…`  
  ↳ **lỗi:** This Bash command contains multiple operations. The following part requires approval: cd /root/.cache/skill-bench/runs/oulad-1/sonnet__noskills/oulad_early_warning/r1/workspace; python3 -I -c " impor…
6. Bash: `cd /root/.cache/skill-bench/runs/oulad-1/sonnet__noskills/oulad_early_warning/r1/workspace && python3 -I -c " import pandas as pd m=pd.read_csv('data/aq3_model_table.csv') print(m.describe().T[['mean','min','max']].to_string()) print(m.groupby(['code_module','code_presentation','split']).size()) pr…`
7. Bash: `mkdir -p outputs scripts && cat > scripts/a.py <<'E' import pandas as pd, numpy as np, json from scipy import stats from sklearn.linear_model import LogisticRegression from sklearn.ensemble import HistGradientBoostingClassifier from sklearn.preprocessing import StandardScaler from sklearn.metrics i…`  
  ↳ **lỗi:** Contains brace with quote character (expansion obfuscation)
8. Write `scripts/a.py`
9. Bash: `python3 -I scripts/a.py 2>&1 | grep -v Warning`

> Chạy script lần đầu thất bại vì thư mục `outputs` chưa được tạo (lệnh mkdir trước đó bị chặn). Tôi tạo thư mục rồi chạy lại.

10. Bash: `mkdir -p outputs && python3 -I scripts/a.py 2>&1 | grep -v Warning`
11. Write `outputs/answer.md`
12. Write `outputs/story.md`

> Với dữ liệu ngày 0–28, có dự báo được sinh viên Fail/Withdrawn nhưng chỉ ở mức vừa phải, và mục tiêu bắt 70% không đạt được khi chỉ có 200 suất liên hệ mỗi module-kỳ. Tôi chia dữ liệu theo thời gian: train 2013B+2013J, validation 2014B, test 2014J (3.644 sinh viên). Câu 1–2 là mô tả và kiểm định tr…


## Trả lời cuối cùng

Với dữ liệu ngày 0–28, có dự báo được sinh viên Fail/Withdrawn nhưng chỉ ở mức vừa phải, và mục tiêu bắt 70% không đạt được khi chỉ có 200 suất liên hệ mỗi module-kỳ. Tôi chia dữ liệu theo thời gian: train 2013B+2013J, validation 2014B, test 2014J (3.644 sinh viên). Câu 1–2 là mô tả và kiểm định trên toàn bộ dữ liệu. 1. **Ba nhóm kết quả:** Pass tương tác nhiều nhất, Fail thấp nhất, Withdrawn ở giữa. Trung vị click tuần 1 là 59 (Pass), 33 (Withdrawn) và 20 (Fail). Tổng click 0–28 lần lượt là 257, 160 và 112. Khoảng cách có ngay từ tuần 1 và giữ suốt 4 tuần. 2. **Chỉ báo khác biệt:** 31 trong 32 chỉ báo khác biệt có ý nghĩa giữa hoàn thành và không hoàn thành (hiệu chỉnh Holm), và cùng chiều ở cả 8 nhóm module-kỳ. Mạnh nhất là số ngày hoạt động, click trang chủ và diễn đàn, số ngày chưa vào lại, và nộp bài TMA1 đúng hạn. Khác biệt có từ tuần 1 (AUC khoảng 0,63) và chỉ tăng nhẹ lên 0,65 ở tuần 2–4. 3. **Dự báo:** mô hình hồi quy logistic đạt AUC 0,685 trên test (FFF 0,79; BBB 0,62). Ngưỡng chọn trên validation bắt được 66,7% sinh viên không hoàn thành, chưa đủ 70%. Để bắt 70% phải gắn cờ khoảng 52% sinh viên, và chỉ khoảng 51% trong số đó thật sự không hoàn thành. 4. **Ưu tiên top 200:** xếp theo điểm rủi ro của mô hình, lấy 200 người cao nhất mỗi module-kỳ. - Danh sách 400 người trúng 280 sinh viên không hoàn thành (precision 70%), nhưng chỉ bắt được 20,3% tổng số. - Trần lý thuyết là 27–31%, nên 70% không thể đạt với giới hạn này. Cần liên hệ khoảng 1.880 người. - Với tỉ lệ chuyển đổi giả định 14%, danh sách ước tính giúp được khoảng 39 sinh viên. - Quy tắc đơn giản "ít ngày hoạt động nhất" trúng 297/400, nhỉnh hơn mô hình, nên cân nhắc dùng quy tắc này. - Kiểm tra công bằng cho thấy sinh viên trình độ đầu vào "Lower Than A Level" được chọn nhiều hơn rõ rệt, cần rà soát trước khi triển khai. 5. **Giải thích cho cố vấn:** với 399 trong 400 sinh viên ưu tiên, bài TMA1 (chưa nộp, nộp trễ hoặc điểm thấp) là yếu tố đóng góp lớn nhất. Số ngày hoạt động và tổng click thường đứng sau. Mỗi sinh viên có sẵn một lời nhắn 2–3 câu trong cột `loi_nhan_cho_co_van`. Các dấu hiệu này chỉ liên quan, không chứng minh nguyên nhân. Hạn chế: chỉ có một kỳ test và hai module, và AUC giảm từ validation (0,76) sang test (0,685), nên nên kỳ vọng ở mức test. Báo cáo đầy đủ và bản tóm tắt cho lãnh đạo nằm trong `outputs/answer.md` và `outputs/story.md`, kèm các bảng CSV và 3 hình PNG. Danh sách 400 sinh viên là `outputs/q5_priority_list_with_explanations.csv`, mã nguồn là `scripts/a.py`.

## Tiêu chí bị trượt (giám khảo)

- AQ3 rò rỉ/đạo đức: không dùng biến kết quả hay biến nhạy cảm; tma1_score bị loại hoặc được cảnh báo  
  ↳ scripts/a.py dòng 29 loại gender/age/disability/imd/region nhưng giữ tma1_score làm đặc trưng (kèm tma1_score_missing) và không hề cảnh báo nguy cơ nhìn trước; giải thích còn nhắc 'điểm thấp' TMA1
- AQ3 kết quả: PR-AUC test ≈0,66 so với baseline; recall tại ngưỡng validation  
  ↳ avg_precision test = 0,533 (tham chiếu 0,665; trùng biến thể có tma1_score là 0,533), không báo PR-AUC trong answer mà dùng ROC-AUC 0,685; dù vậy đã nêu trung thực recall 66,7% < 70% với precision 51,9%
- AQ4: xếp hạng riêng từng module-kỳ, precision@200 ≈ BBB 0,76 / FFF 0,88, so với tỉ lệ nền  
  ↳ Có chia 200/module và so với tỉ lệ nền 35,6%/39,9%, nhưng BBB precision 0,52 (104/200) lệch xa 0,76; FFF 0,88 khớp; mô hình còn thua quy tắc 'ít ngày hoạt động' (297 so với 280)
