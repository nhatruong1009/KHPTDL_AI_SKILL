# retail_uk · haiku · r1

| | |
|---|---|
| Điểm overall / accuracy / quality | 93.3 / 100.0 / 83.3 |
| Thời gian · chi phí · số turn | 464.9 s · $0.038 · 25 |
| Skill đã nạp (theo thứ tự) | (không có) |
| Lỗi công cụ | 2 |

## Các bước

1. Bash: `ls -la data/ && python -c "import pandas, numpy, matplotlib; print(pandas.__version__)" ; find data -type f | head -50`
2. Bash: `mkdir -p outputs/doanh-thu-2011-vs-2010 && cat > /tmp/eda.py <<'EOF' import pandas as pd x = pd.ExcelFile("data/online_retail_II.xlsx") print(x.sheet_names) for s in x.sheet_names: df = x.parse(s) print(s, df.shape) print(df.dtypes) print(df.head(3).to_string()) print(df.isna().sum()) print(df["Inv…`  
  ↳ **lỗi:** Parser skipped input between top-level statements
3. Write `outputs/doanh-thu-2011-vs-2010/eda_check.py`
4. Bash: `timeout 900 python outputs/doanh-thu-2011-vs-2010/eda_check.py 2>&1 | tail -120`

> Data is two sheets with overlapping dates (Dec 1–9, 2010 appears in both), 2009-12 to 2011-12-09 coverage, and about 25% of rows lack a Customer ID. I'll build the analysis script with those handled explicitly.

5. Write `outputs/doanh-thu-2011-vs-2010/analysis.py`
6. Bash: `timeout 900 python outputs/doanh-thu-2011-vs-2010/analysis.py 2>&1 | tail -150`

> The decomposition reconciles exactly: 1.42M new + (−1.07M churned − 0.39M retained + 0.04M returning) + 0.08M unidentified + 0.06M returns-only = +0.156M. Before writing conclusions, I'll check whether the new-customer gain is concentrated in a few large accounts, and how the markets split between …

7. Write `outputs/doanh-thu-2011-vs-2010/concentration_check.py`
8. Bash: `timeout 300 python outputs/doanh-thu-2011-vs-2010/concentration_check.py 2>&1 | tail -80`

> Market and customer-type splits are clear. Next I'll compute the per-customer averages and retention figures for the story, then check the charts.

9. Edit `outputs/doanh-thu-2011-vs-2010/concentration_check.py`
10. Bash: `timeout 300 python outputs/doanh-thu-2011-vs-2010/concentration_check.py 2>&1 | sed -n '1,20p'; ls -la outputs/doanh-thu-2011-vs-2010/`
11. Read `outputs/doanh-thu-2011-vs-2010/waterfall_change.png`

> The waterfall reconciles visually. One labelling problem: `delta_old_customers` in `summary.csv` currently includes the unidentified-customer bucket, so it doesn't match the segment table. I'll fix that and rerun.

12. Edit `outputs/doanh-thu-2011-vs-2010/analysis.py`
13. Edit `outputs/doanh-thu-2011-vs-2010/analysis.py`
14. Bash: `rm -f outputs/doanh-thu-2011-vs-2010/eda_check.py && timeout 900 python outputs/doanh-thu-2011-vs-2010/analysis.py > outputs/doanh-thu-2011-vs-2010/run_log.txt 2>&1; echo EXIT $?; timeout 300 python outputs/doanh-thu-2011-vs-2010/concentration_check.py > outputs/doanh-thu-2011-vs-2010/concentration…`  
  ↳ **lỗi:** A variable in this command can't be checked before it runs
15. Bash: `rm -f outputs/doanh-thu-2011-vs-2010/eda_check.py && timeout 900 python outputs/doanh-thu-2011-vs-2010/analysis.py > outputs/doanh-thu-2011-vs-2010/run_log.txt 2>&1; echo "analysis exit $?"; timeout 300 python outputs/doanh-thu-2011-vs-2010/concentration_check.py > outputs/doanh-thu-2011-vs-2010/co…`

> Both scripts run cleanly and the decomposition reconciles. I'll write the CEO story and the full answer now.

16. Write `outputs/doanh-thu-2011-vs-2010/story.md`

> Before finalising, I'm checking the story's figures against the outputs. Three statements need correcting: the UK share (it's ~84% of 2011 revenue, not 85%), the "without new customers" figure (should be −1.27M, not −1.35M), and an unsupported claim that new customers outside the UK are "more stabl…

17. Edit `outputs/doanh-thu-2011-vs-2010/story.md`
18. Edit `outputs/doanh-thu-2011-vs-2010/story.md`
19. Edit `outputs/doanh-thu-2011-vs-2010/story.md`
20. Read `outputs/doanh-thu-2011-vs-2010/delta_by_country.png`

> The charts check out: the top-8 bar chart captures the largest movers, and the "other markets" bar is the remainder. Now I'll write `answer.md` for the skill's output contract.

21. Write `outputs/doanh-thu-2011-vs-2010/answer.md`

> I found two wrong numbers in `answer.md` while checking the table: the returning/returns-only row should be +102,033 (not +101,633), and missing Customer IDs run at ~20–25% of rows by sheet, not a flat 25%. Fixing both.

22. Edit `outputs/doanh-thu-2011-vs-2010/answer.md`
23. Edit `outputs/doanh-thu-2011-vs-2010/answer.md`
24. Edit `outputs/doanh-thu-2011-vs-2010/story.md`

> Doanh thu thuần 2011 tăng **+1,8%** so với 2010 khi so cùng kỳ 1/1–9/12 của cả hai năm: 8,85M → 9,00M GBP (+156K). Phần tăng này đến từ khách mới; khách cũ đang giảm mạnh. UK giảm nhẹ, còn các thị trường ngoài UK tăng. **Vì sao không so cả năm:** 2011 chỉ có dữ liệu đến 9/12. So cả năm 2010 (9,22M)…


## Trả lời cuối cùng

Doanh thu thuần 2011 tăng **+1,8%** so với 2010 khi so cùng kỳ 1/1–9/12 của cả hai năm: 8,85M → 9,00M GBP (+156K). Phần tăng này đến từ khách mới; khách cũ đang giảm mạnh. UK giảm nhẹ, còn các thị trường ngoài UK tăng. **Vì sao không so cả năm:** 2011 chỉ có dữ liệu đến 9/12. So cả năm 2010 (9,22M) với 2011 cho −2,3%, nhưng đó là so sánh sai. **Khách mới hay cũ** (bảng phân rã đối chiếu khớp với tổng, +155.746 GBP): - Khách mới (1.536 khách lần đầu mua 2011): **+1,42M** - Khách cũ ngừng mua (1.557 khách, 37% số khách 2010): **−1,07M** - Khách cũ vẫn mua (2.642 khách): **−0,39M**, chi tiêu bình quân mỗi khách giảm 5,8% - Khách cũ quay lại hoặc chỉ có hoàn trả: +0,10M - Không rõ mã khách: +0,08M Nếu bỏ khách mới, doanh thu 2011 giảm khoảng 1,27M (−14%) so với 2010. **Thị trường:** - UK: −59K (−0,8%). Đây là nơi mất khách lớn nhất (−0,93M từ khách ngừng mua). - Tăng mạnh nhất: Australia +106K (gần như toàn bộ từ khách cũ), Pháp +63K, Na Uy +28K, Hà Lan +27K. - Giảm mạnh nhất: Ireland (EIRE) −79K, Đan Mạch −28K, Thụy Điển −17K. **Gợi ý cho CEO:** ưu tiên giữ chân khách cũ, đặc biệt ở UK, và tiếp tục tìm khách mới ở ngoài UK. Mất khách cũ và chi tiêu giảm ở khách còn lại cộng lại −1,45M, gần bằng toàn bộ doanh thu khách mới (+1,42M). Dữ liệu không có chi phí thu hút khách hay biên lợi nhuận, nên lựa chọn cuối cùng cần kiểm tra thêm các số liệu đó. **Giả định và giới hạn:** - Đơn vị tiền tệ không ghi trong dữ liệu; tôi giả định GBP. - Hai sheet chồng lấp 1–9/12/2010; mỗi ngày được tính một lần. Đã loại 11.812 dòng trùng lặp hoàn toàn. - Doanh thu được tính sau khi trừ hàng trả lại; bỏ các dòng đơn giá ≤ 0. - Khoảng 20–25% dòng không có mã khách, nên không phân loại mới/cũ được cho phần đó. - Dữ liệu bắt đầu từ 12/2009, nên một số khách "mới" có thể đã mua trước đó. - Chỉ tính dòng sản phẩm (bỏ phí gửi, phí ngân hàng...) thì tăng trưởng là +2,7% thay vì +1,8%; kết luận không đổi. - Đây là quan sát, không phải nhân quả. **Tệp đầu ra** (trong `outputs/doanh-thu-2011-vs-2010/`): - `story.md`: bản kể chuyện cho CEO - `answer.md`: trả lời đầy đủ kèm phương pháp và giới hạn - `analysis.py`, `concentration_check.py`: mã chạy được; log trong `run_log.txt` và `concentration_log.txt` - `summary.csv`, `decomposition_by_segment.csv`, `delta_by_country.csv`, `delta_by_country_segment.csv`, `customer_segments.csv` - `waterfall_change.png`, `delta_by_country.png`
