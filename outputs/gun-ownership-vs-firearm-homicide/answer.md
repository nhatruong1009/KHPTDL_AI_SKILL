# Lượng súng trong dân và tỷ lệ giết người bằng súng giữa các nước

**Câu hỏi:** Mối liên hệ giữa lượng súng trong dân và tỷ lệ giết người bằng súng giữa các nước, kèm thu nhập và bất bình đẳng (Gini).
**Cách hiểu:** súng = số súng dân sự trên 100 người (2017); giết người bằng súng = trung bình 2013-2022 trên 100,000 dân. Chỉ có 95 nước có cả hai số; kiểm soát thu nhập (GDP/người, lấy log) và Gini chỉ làm được với 51 nước.

## Trả lời
1. **So sánh thô: gần như không có liên hệ.** Hệ số tương quan hạng Spearman = **-0.003** (95 nước, khoảng tin cậy bootstrap -0.22 đến 0.20); bỏ Mỹ vẫn ~0 (-0.015). Trong từng nhóm thu nhập: cao 47 nước -0.03, trung bình cao 37 nước 0.13.
2. **Vì sao thô ~0:** nước có nhiều súng trong dân thường giàu hơn (tương quan súng-GDP +0.41), còn nước giàu có tỷ lệ giết người bằng súng thấp (GDP-giết người -0.43). Hai tác động ngược nhau triệt tiêu. Ví dụ Iceland, Áo, Phần Lan có 30-32 súng/100 người nhưng chỉ 0.08-0.17 vụ/100K; trong khi El Salvador, Jamaica, Honduras (9-14 súng/100 người) có 37-38 vụ/100K.
3. **Sau khi tính thu nhập và Gini (51 nước): súng có liên hệ dương.** Hồi quy log(tỷ lệ giết người bằng súng) theo súng, log(GDP/người), Gini (đã chuẩn hóa): hệ số của súng **+0.54** (khoảng tin cậy bootstrap 95%: 0.24 đến 0.94), nghĩa là mỗi độ lệch chuẩn súng tăng thêm gắn với tỷ lệ cao hơn khoảng 1.7 lần. Gini mạnh hơn: hệ số +1.19; GDP -0.57. Riêng Gini có tương quan hạng +0.65 với tỷ lệ giết người bằng súng, cao nhất trong các biến.
4. **Điểm ngoại lệ lớn:** Mỹ có 120.5 súng/100 người (gấp 3 lần nước đứng sau) nhưng tỷ lệ giết người bằng súng chỉ 3.5, thấp hơn nhiều nước Mỹ Latinh và Caribe có ít súng hơn nhiều.

**Tóm lại:** chênh lệch giữa các nước chủ yếu gắn với bất bình đẳng và thu nhập; lượng súng chỉ cho thấy liên hệ dương khi đã kiểm soát hai yếu tố này, và kết quả đó kém chắc chắn (xem lưu ý).

## Biểu đồ
- [guns_vs_firearm_homicide.png](guns_vs_firearm_homicide.png) - phân tán 95 nước, tô màu theo nhóm thu nhập

## Cách làm
- Từ `country_gun_profile.csv` (217 nước; 95 có cả súng và tỷ lệ giết người bằng súng; 51 có thêm GDP và Gini). Spearman cho quan hệ thô; hồi quy bình phương tối thiểu trên log(tỷ lệ) với biến chuẩn hóa; khoảng tin cậy bằng bootstrap 2,000 lần.
- Code: [analysis.py](analysis.py), log `run_log.txt`; bảng `by_income_group.csv`, `by_region.csv`.

## Lưu ý
- **Chỉ là mối liên hệ giữa các nước, không chứng minh súng gây ra giết người** (hoặc ngược lại: nơi bất an có thể mua súng nhiều hơn). Đây cũng không phải kết luận cho một nước cụ thể.
- **Mẫu thiếu và lệch**: chỉ 95/217 nước có tỷ lệ giết người bằng súng, hầu hết là nước thu nhập cao và trung bình cao (84 nước); nhóm thu nhập thấp chỉ có 1 nước, thu nhập trung bình thấp 10. Châu Phi cận Sahara chỉ 5 nước.
- Kết quả hiệu chỉnh (51 nước) nhạy với mẫu và dạng mô hình (tuyến tính trên log, chỉ 3 biến); chưa thử các biến khác như luật súng, tội phạm có tổ chức, chất lượng ghi nhận số liệu.
- Súng 2017 (ước tính, nhiều nước chỉ có số ước lượng) so với tỷ lệ giết người trung bình 2013-2022: thời điểm không hoàn toàn khớp.
- Mình chưa phân tích theo thời gian trong `firearm_homicides_country_year.csv`.
