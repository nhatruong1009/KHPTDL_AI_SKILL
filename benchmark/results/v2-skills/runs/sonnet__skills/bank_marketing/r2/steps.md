# bank_marketing · sonnet__skills · r2

| | |
|---|---|
| Điểm overall / accuracy / quality | 74.0 / 66.7 / 85.0 |
| Thời gian · chi phí · số turn | 403.0 s · $0.499 · 31 |
| Skill đã nạp (theo thứ tự) | `data-eda` → `data-relevance` → `analysis-plan` → `data-predict` → `answer-qa` |
| Lỗi công cụ | 4 |

## Các bước

1. **SKILL `data-eda`**
2. Bash: `cd data; ls -laR | head -50; python -c "import pandas, sklearn; print(1)"`
3. Bash: `W=/root/.cache/skill-bench/runs/v2-skills/sonnet__skills/bank_marketing/r2/workspace; cd $W; python $W/.claude/skills/data-eda/scripts/inspect_data.py data 2>&1 | head -150; cat data/bank-additional/bank-additional-names.txt`  
  ↳ **lỗi:** A variable set in this command can't be checked before it runs
4. Bash: `cd /root/.cache/skill-bench/runs/v2-skills/sonnet__skills/bank_marketing/r2/workspace && python .claude/skills/data-eda/scripts/inspect_data.py data 2>&1 | head -150`
5. Read `data/bank-additional/bank-additional-names.txt`
6. **SKILL `data-relevance`**
7. **SKILL `analysis-plan`**
8. **SKILL `data-predict`**
9. Bash: `mkdir -p outputs/du-doan-dang-ky && cat > outputs/du-doan-dang-ky/analysis.py <<'EOF' import pandas as pd, numpy as np, matplotlib matplotlib.use("Agg") import matplotlib.pyplot as plt from sklearn.pipeline import Pipeline from sklearn.compose import ColumnTransformer from sklearn.preprocessing imp…`  
  ↳ **lỗi:** Contains brace with quote character (expansion obfuscation)

> Mình đang viết lại script mô hình gọn hơn (dùng tệp bank-additional-full.csv, chia theo thời gian, bỏ `duration`).

10. Write `outputs/du-doan-dang-ky/analysis.py`
11. Bash: `python -W ignore -I outputs/du-doan-dang-ky/analysis.py 2>&1 | tail -80; cat outputs/du-doan-dang-ky/split_base_rate.csv`
12. Bash: `python -W ignore -I -c " import pandas as pd d=pd.read_csv('data/bank-additional/bank-additional-full.csv',sep=';');d['y']=(d.y=='yes') n=len(d);d['s']=['tr']*int(n*.6)+['va']*(int(n*.8)-int(n*.6))+['te']*(n-int(n*.8)) print(pd.crosstab(d.s,d.month));print(d.groupby(['s','month'],sort=False).y.mean…`
13. Bash: `python - <<'EOF' p="outputs/du-doan-dang-ky/analysis.py" s=open(p).read() s=s.replace('''run("Baseline: tỉ lệ nền (Dummy)", DummyClassifier(strategy="prior"), cat, num) ''','''for dn, d in (("valid", va), ("test", te)): rows.append(metrics("Baseline: gọi ngẫu nhiên", d.y.values, np.random.RandomSta…`

> Chạy lại trước, rồi đặt tiêu đề biểu đồ theo kết quả thật. Mình cũng thêm CV ngẫu nhiên (chỉ để tham chiếu).

14. Bash: `cat >> outputs/du-doan-dang-ky/analysis.py <<'EOF' # reference only: random stratified 5-fold CV (NOT a future-looking estimate) from sklearn.model_selection import StratifiedKFold, cross_val_predict cv = StratifiedKFold(5, shuffle=True, random_state=42) cvr = [] for nm, c, nu in (("A Logistic đầy …`
15. Bash: `sed -i 's/("n", StandardScaler(), num)\])/("n", StandardScaler(), num)], sparse_threshold=0)/' outputs/du-doan-dang-ky/analysis.py && python -W ignore -I outputs/du-doan-dang-ky/analysis.py 2>&1 | tail -60`
16. Bash: `python - <<'EOF' p="outputs/du-doan-dang-ky/analysis.py" s=open(p).read() s=s.replace('best = "C Logistic: bỏ vĩ mô + tháng"','best = "B Logistic: bỏ vĩ mô"') s=s.replace('fitted["C HistGB: bỏ vĩ mô + tháng"]','fitted["B HistGB: bỏ vĩ mô"]') s=s.replace('"C Logistic: bỏ vĩ mô + tháng", "C HistGB: b…`
17. Bash: `python -W ignore -I -c " import pandas as pd d=pd.read_csv('data/bank-additional/bank-additional-full.csv',sep=';');d['y']=d.y=='yes' print(d.y.mean());print(d.groupby('poutcome').y.agg(['mean','size']).round(3));print(d.groupby('contact').y.mean().round(3));print(d.groupby(d.pdays!=999).y.agg(['me…`
18. Write `outputs/du-doan-dang-ky/answer.md`
19. **SKILL `answer-qa`**
20. Bash: `cd /root/.cache/skill-bench/runs/v2-skills/sonnet__skills/bank_marketing/r2/workspace/outputs/du-doan-dang-ky && sed -i 's/riêng 60+ là 52,0% nhưng chiếm 41,8% nhóm đó được chọn do base rate cao/riêng 60+ là 52,0%, nhưng 41,8% khách 60+ lọt vào nhóm được gọi do tỉ lệ nền cao 45,9%/' answer.md && gr…`
21. Read `outputs/du-doan-dang-ky/precision_top20.png`
22. Read `outputs/du-doan-dang-ky/feature_importance.png`

> Đang kiểm tra lần cuối: sửa tiêu đề biểu đồ 1 cho nêu đúng việc luật đơn giản nhỉnh hơn mô hình, rồi chạy lại.

23. Bash: `cd /root/.cache/skill-bench/runs/v2-skills/sonnet__skills/bank_marketing/r2/workspace && sed -i 's/ax.set_title(f"Gọi 20% khách điểm cao nhất.*/ax.set_title(f"Logistic: top 20% đạt {v[2]:.0f}% đăng ký (ngẫu nhiên {v[0]:.0f}%), nhưng luật đơn giản còn nhỉnh hơn {v[1]:.0f}%", fontsize=11)/' outputs/d…`  
  ↳ **lỗi:** A variable in this command can't be checked before it runs
24. Bash: `cd /root/.cache/skill-bench/runs/v2-skills/sonnet__skills/bank_marketing/r2/workspace && python -W ignore -I - <<'EOF' import re p="outputs/du-doan-dang-ky/analysis.py" s=open(p).read() s=re.sub(r'ax\.set_title\(f"Gọi 20% khách.*\n','ax.set_title(f"Logistic: top 20% đạt {v[2]:.0f}% đăng ký (ngẫu nh…`  
  ↳ **lỗi:** A variable in this command can't be checked before it runs
25. Bash: `cd /root/.cache/skill-bench/runs/v2-skills/sonnet__skills/bank_marketing/r2/workspace && python -W ignore -I - <<'EOF' import re p="outputs/du-doan-dang-ky/analysis.py" s=open(p).read() s=re.sub(r'ax\.set_title\(f"Gọi 20% khách.*\n','ax.set_title(f"Logistic: top 20% đạt {v[2]:.0f}% đăng ký (ngẫu nh…`

> Mô hình tốt nhất tôi chọn chỉ hơn gọi ngẫu nhiên rõ rệt, còn so với một luật đơn giản thì gần như ngang nhau. Chia theo thời gian, nó đưa tỉ lệ đăng ký trong 20% khách được gọi trước lên 53,4%, so với 29,8% khi gọi ngẫu nhiên (gấp khoảng 1,8 lần). Tôi dùng bản đầy đủ nhất là `bank-additional/bank-a…


## Trả lời cuối cùng

Mô hình tốt nhất tôi chọn chỉ hơn gọi ngẫu nhiên rõ rệt, còn so với một luật đơn giản thì gần như ngang nhau. Chia theo thời gian, nó đưa tỉ lệ đăng ký trong 20% khách được gọi trước lên 53,4%, so với 29,8% khi gọi ngẫu nhiên (gấp khoảng 1,8 lần). Tôi dùng bản đầy đủ nhất là `bank-additional/bank-additional-full.csv` (41.188 khách, sắp theo thời gian từ 05/2008 đến 11/2010). Đây là bản duy nhất có các chỉ số vĩ mô và thứ tự thời gian. **Kết quả trên tập test** (20% cuối theo thời gian, chỉ đọc một lần; mô hình được chọn trên tập validation): | Mô hình | AUC | Tỉ lệ đăng ký trong 20% khách xếp đầu | |---|---|---| | Gọi ngẫu nhiên | 0,49 | 29,8% | | Luật "từng đăng ký ở chiến dịch trước" | 0,63 | 56,6% | | **Logistic, chỉ dùng thông tin biết trước cuộc gọi và bỏ chỉ số vĩ mô** | **0,68** | 53,4% | | Gradient Boosting (cùng biến) | 0,68 | 45,2% | - **So với luật đơn giản:** mô hình xếp hạng tổng thể tốt hơn một chút (AUC 0,68 so với 0,63), nhưng ở top 20% thì luật đơn giản nhỉnh hơn (56,6% so với 53,4%). Chưa có khoảng tin cậy cho chênh lệch này, nên tôi coi hai cách là ngang nhau về thực dụng. - **Yếu tố quan trọng nhất:** lịch sử chiến dịch trước (`poutcome`, `pdays`, `previous`). Xáo trộn nhóm này làm AUC giảm 0,060, các nhóm còn lại giảm dưới 0,004. - Khách từng đăng ký ở chiến dịch trước đăng ký lại 65,1% (1.373 khách), khách chưa từng liên hệ chỉ 8,8%. - Gọi bằng điện thoại di động đăng ký 14,7%, điện thoại bàn 5,2%. - Đây là mối liên hệ, không chứng minh nguyên nhân. - **Dữ liệu trôi rất mạnh theo thời gian.** Tỉ lệ đăng ký là 4,8% ở phần train, 11,1% ở validation và 30,8% ở test. Giai đoạn test có euribor3m từ 0,63 đến 1,30, nằm hẳn ngoài khoảng của train (4,19 đến 5,05). - Vì thế mô hình dùng chỉ số vĩ mô và tháng không ngoại suy được (AUC test 0,50). - AUC 0,79 chỉ xuất hiện khi chia ngẫu nhiên, tức trộn lẫn các giai đoạn, nên tôi không dùng làm kết quả chính. - **Loại để tránh rò rỉ:** - `duration` chỉ biết sau cuộc gọi. Thêm vào thì AUC lên 0,80, nhưng đó là rò rỉ nên không dùng được để lập danh sách gọi. - `campaign` đếm cả cuộc gọi cuối nên không kiểm chứng được trước cuộc gọi. Thêm vào gần như không đổi kết quả. - `age` và `marital` không dùng làm biến dự đoán, chỉ để kiểm tra theo nhóm. Trong top 20%, tỉ lệ đăng ký khá đều giữa các nhóm tuổi (49,5% đến 55,9%) và tình trạng hôn nhân (51,8% đến 53,7%). AUC thấp nhất ở nhóm 60 tuổi trở lên (0,56). **Khuyến nghị:** bắt đầu từ luật "ưu tiên khách từng đăng ký hoặc từng được liên hệ ở chiến dịch trước, gọi qua di động", rồi dùng điểm Logistic để xếp phần còn lại. Nên huấn luyện lại bằng dữ liệu mới nhất và theo dõi tỉ lệ đăng ký thực tế vài tuần đầu. Mọi tệp nằm trong `outputs/du-doan-dang-ky/`. Mở `answer.md` trước, mã chạy nằm ở `analysis.py`; `metrics.csv` và `feature_group_importance.csv` có số liệu chi tiết, hai biểu đồ là `precision_top20.png` và `feature_importance.png`.

## Tiêu chí bị trượt (giám khảo)

- 4. Xử lý rõ pdays=999 và 'unknown'  
  ↳ pdays=999 được xử lý rõ bằng cờ pdays_contacted, còn pdays_val đặt bằng 0. Nhưng 'unknown' bị giữ lại âm thầm như một nhóm one-hot, không phân tích hay nhắc đến trong answer.md. Có ghi chú về 12 dòng trùng.
- 5. Yếu tố quan trọng khớp với tham chiếu  
  ↳ Chỉ nêu poutcome/pdays/previous (AUC giảm 0,060) và contact (14,7% so với 5,2%). Các chỉ số vĩ mô (nr.employed/euribor3m/emp.var.rate) và month bị loại khỏi mô hình chính vì trôi theo thời gian, nên không được xếp vào nhóm yếu tố quan trọng. Agent chỉ nhắc rằng vĩ mô giải thích khác biệt giữa các giai đoạn. Như vậy mới khớp một phần.
