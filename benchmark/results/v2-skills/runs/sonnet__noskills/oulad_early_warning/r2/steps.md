# oulad_early_warning · sonnet__noskills · r2

| | |
|---|---|
| Điểm overall / accuracy / quality | 63.5 / 62.5 / 65.0 |
| Thời gian · chi phí · số turn | 158.0 s · $0.397 · 24 |
| Skill đã nạp (theo thứ tự) | (không có) |
| Lỗi công cụ | 9 |

## Các bước

1. Bash: `cd data; ls -la; for f in *; do echo == $f; head -3 "$f"; wc -l "$f"; done`  
  ↳ **lỗi:** A variable in this command can't be checked before it runs
2. Bash: `cd data && ls -la && for f in *; do echo "== $f"; head -3 "$f"; wc -l "$f"; done`  
  ↳ **lỗi:** A variable in this command can't be checked before it runs

> Tránh biến trong lệnh.

3. Bash: `ls -la data/ && head -3 data/*`
4. Bash: `cd data; cat aq4_decision_params.json; python3 -c " import pandas as pd for f in ['aq1_student_week','aq2_diagnostic_table','aq3_model_table','context_all_registrations','aq3_audit_attributes']: d=pd.read_csv(f+'.csv');print(f,d.shape) if 'split' in d: print(d.split.value_counts().to_dict()) c=pd.r…`
5. Bash: `cd /root/.cache/skill-bench/runs/oulad-1/sonnet__noskills/oulad_early_warning/r2/workspace; mkdir -p outputs scripts; cat > scripts/a12.py <<'E' import pandas as pd,numpy as np from scipy import stats d=pd.read_csv('data/aq2_diagnostic_table.csv') print(d.label3.value_counts(), (d.label3!=d.final_r…`  
  ↳ **lỗi:** This Bash command contains multiple operations. The following parts require approval: mkdir -p outputs scripts, cat
6. Write `scripts/a12.py`
7. Bash: `mkdir -p outputs scripts`
8. Bash: `python3 scripts/a12.py`  
  ↳ **lỗi:** Exit code 2 python3: can't open file '/root/.cache/skill-bench/runs/oulad-1/sonnet__noskills/oulad_early_warning/r2/workspace/data/scripts/a12.py': [Errno 2] No such file or directory
9. Bash: `cd /root/.cache/skill-bench/runs/oulad-1/sonnet__noskills/oulad_early_warning/r2/workspace && rmdir data/outputs data/scripts; mkdir -p outputs scripts; ls; python3 scripts/a12.py`  
  ↳ **lỗi:** This Bash command contains multiple operations. The following parts require approval: rmdir data/outputs data/scripts, mkdir -p outputs scripts

> Dọn thư mục rỗng tôi lỡ tạo trong data/, rồi chạy phân tích.

10. Bash: `cd /root/.cache/skill-bench/runs/oulad-1/sonnet__noskills/oulad_early_warning/r2/workspace && rmdir data/outputs data/scripts`
11. Bash: `python3 scripts/a12.py`
12. Write `/root/.cache/skill-bench/runs/oulad-1/sonnet__noskills/oulad_early_warning/r2/scripts/a3.py`
13. Bash: `python3 scripts/a3.py`  
  ↳ **lỗi:** Exit code 2 python3: can't open file '/root/.cache/skill-bench/runs/oulad-1/sonnet__noskills/oulad_early_warning/r2/workspace/scripts/a3.py': [Errno 2] No such file or directory
14. Bash: `cd /root/.cache/skill-bench/runs/oulad-1/sonnet__noskills/oulad_early_warning/r2 && mv scripts/a3.py workspace/scripts/ && rmdir scripts && cd workspace && python3 scripts/a3.py`  
  ↳ **lỗi:** Multiple directory changes in one command require approval for clarity
15. Bash: `mv /root/.cache/skill-bench/runs/oulad-1/sonnet__noskills/oulad_early_warning/r2/scripts/a3.py scripts/a3.py`  
  ↳ **lỗi:** mv in '/root/.cache/skill-bench/runs/oulad-1/sonnet__noskills/oulad_early_warning/r2/scripts/a3.py' needs approval. The path is outside the working directories for this session ('/root/.cache/skill-b…
16. Bash: `python3 scripts/a3.py`  
  ↳ **lỗi:** Exit code 2 python3: can't open file '/root/.cache/skill-bench/runs/oulad-1/sonnet__noskills/oulad_early_warning/r2/workspace/scripts/a3.py': [Errno 2] No such file or directory
17. Write `scripts/model.py`
18. Bash: `python3 scripts/model.py 2>&1 | grep -v Warning`

> Thiếu thư mục outputs (lệnh mkdir trước đó chạy nhầm chỗ); tạo lại rồi chạy tiếp.

19. Bash: `mkdir -p outputs && python3 scripts/model.py 2>&1 | grep -v Warning | tail -n +28`
20. Bash: `sed -i "s/X\['tma1_score'\]=df.tma1_score.fillna(50).*/X['tma1_score']=df.tma1_score.fillna(df.tma1_score.median()) # chưa nộp -> trung vị; tín hiệu nằm ở tma1_submitted/" scripts/model.py && sed -i "s/c=contrib.loc\[i\].sort_values/c=contrib.loc[i].drop('module_FFF').sort_values/" scripts/model.py…`
21. Bash: `cat >> scripts/model.py <<'E' # bo sung: flag-rate can de dat recall 70% tren test (oracle) va tren thang diem s=m.score[te].values; yy=y[te].values o=np.argsort(-s); cr=np.cumsum(yy[o])/yy.sum() n70=int(np.argmax(cr>=0.7))+1; print('test: can flag',n70,'SV =',n70/len(s),'de dat 70% recall; precisi…`

> Giờ viết answer.md và story.md.

22. Write `outputs/answer.md`
23. Write `outputs/story.md`

> Hệ thống cảnh báo sớm dùng được để xếp thứ tự ưu tiên, nhưng chưa đạt mục tiêu bắt 70% sinh viên không hoàn thành. Trên kỳ 2014J mô hình chỉ bắt được 65%. Mô hình huấn luyện trên 2013B/2013J, chọn ngưỡng trên 2014B, và kiểm tra trên 2014J (kỳ chưa từng thấy). Tôi gộp Distinction vào Pass và coi "kh…


## Trả lời cuối cùng

Hệ thống cảnh báo sớm dùng được để xếp thứ tự ưu tiên, nhưng chưa đạt mục tiêu bắt 70% sinh viên không hoàn thành. Trên kỳ 2014J mô hình chỉ bắt được 65%. Mô hình huấn luyện trên 2013B/2013J, chọn ngưỡng trên 2014B, và kiểm tra trên 2014J (kỳ chưa từng thấy). Tôi gộp Distinction vào Pass và coi "không hoàn thành" là Fail hoặc Withdrawn. 1. **Tương tác 4 tuần đầu:** Pass > Withdrawn > Fail ở cả 4 tuần. Tổng click 0–28 (trung vị): Pass 257, Withdrawn 161, Fail 112. 2. **Chỉ báo khác biệt:** mạnh nhất là số ngày hoạt động (trung vị 12 so với 7), click trang chủ, click diễn đàn và nộp TMA1 đúng hạn. Khác biệt đã có từ tuần 1. Tuần 2 mạnh nhất rồi gần như đi ngang. 3. **Dự báo:** AUC 0,69 trên 2014J (khoảng tin cậy 95%: 0,67–0,70). Ngưỡng chọn để đạt 70% recall trên 2014B chỉ cho 65,3% recall (precision 51,5%) trên 2014J, vì tỷ lệ không hoàn thành của kỳ mới thấp hơn. Mô hình khá tốt ở FFF (recall 75%) nhưng yếu ở BBB (54%). Recall cũng lệch giữa các nhóm, ví dụ nữ 57% so với nam 73%. 4. **Ưu tiên 200 sinh viên mỗi module-kỳ:** xếp theo điểm rủi ro của mô hình logistic, giảm dần. Danh sách 400 người (2 module) trúng 305 người, tức 76% (ngẫu nhiên chỉ 35%). Tuy vậy danh sách chỉ chạm 22% tổng số sinh viên sẽ không hoàn thành, và trần lý thuyết là 29%. Để đạt 70% cần khoảng 1.900 liên hệ. Với tỷ lệ chuyển đổi 14% do nhà trường giả định (chưa kiểm chứng), ước tính chỉ khoảng 43 sinh viên thực sự được giúp. 5. **Lý do cho cố vấn:** với mỗi người trong danh sách, tôi lấy 3 đặc trưng đóng góp nhiều nhất vào điểm rủi ro và viết thành lời nhắn tiếng Việt. Lý do hay gặp nhất là ít ngày hoạt động, nộp TMA1 trễ, chưa nộp TMA1, điểm TMA1 thấp. Khoảng 1/4 người trong danh sách vẫn hoàn thành khóa, nên lời nhắn chỉ là gợi ý hỏi thăm. Tôi đã bỏ "module FFF" khỏi phần lý do vì cố vấn không can thiệp được vào đó. **Tệp trong `outputs/`:** - `answer.md` - `story.md` - `q4_priority_list_top200.csv` - `q4_rule_comparison.csv` - `q3_metrics.json` - `q3_fairness_test.csv` - `q2_weekly_tests.csv` - `chart1_clicks_by_week.png` - `chart2_recall_vs_capacity.png` Mã nằm trong `scripts/`. Lúc đầu tôi lỡ tạo một thư mục `scripts/` rỗng ở `r2/`, bên ngoài workspace, và chưa dọn được vì lệnh cần quyền ngoài thư mục làm việc. Thư mục `data/` vẫn nguyên vẹn.

## Tiêu chí bị trượt (giám khảo)

- AQ3 rò rỉ/đạo đức: không dùng cột kết quả hay thuộc tính nhạy cảm; tma1_score bị loại hoặc được cảnh báo look-ahead  
  ↳ model.py đưa tma1_score vào làm đặc trưng, giá trị thiếu điền bằng trung vị, và không hề cảnh báo nguy cơ look-ahead. 'Điểm TMA1 thấp' còn xuất hiện trong lý do gửi cố vấn (173 lần). Không dùng thuộc tính nhạy cảm.
- AQ3 kết quả: PR-AUC test ±0,05 so với tham chiếu, có baseline, recall/precision tại ngưỡng chọn trên validation, nói rõ có đạt 70% hay không  
  ↳ AP test 0,60 so với tham chiếu ~0,665 (logistic), lệch 0,065, vượt ngưỡng sai số; GBM chỉ báo AUC 0,699. Có so với tỷ lệ nền 37,8% và baseline click. Recall test 65,3%, precision 51,5%, nói rõ là trượt mục tiêu 70%.
- AQ4: xếp hạng trong từng module-kỳ (200 mỗi bên), precision@200 khớp tham chiếu, so với tỷ lệ nền  
  ↳ Có tách quota đúng cách (groupby module-kỳ, head 200). Tuy nhiên BBB chỉ trúng 122/200 = 0,61, so với tham chiếu ~0,76, lệch quá ±0,08; FFF 183/200 = 0,915 thì khớp. Chỉ có tỷ lệ nền gộp 37,8%, thiếu tỷ lệ nền riêng từng module.
