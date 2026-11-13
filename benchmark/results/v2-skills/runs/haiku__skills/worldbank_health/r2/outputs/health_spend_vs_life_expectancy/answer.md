# Chi tiêu y tế và tuổi thọ: kết luận

**Trả lời ngắn:**
1. **Có.** Ở cấp quốc gia, chi tiêu y tế bình quân đầu người cao đi kèm tuổi thọ cao hơn rất rõ (Spearman = 0,84; n = 186 quốc gia, năm 2019).
2. **Nhưng phần lớn là do thu nhập.** GDP/người PPP một mình giải thích 72% phương sai tuổi thọ (R² = 0,72). Khi thêm chi tiêu y tế, R² chỉ tăng lên 0,73. Hệ số của chi tiêu y tế sau khi kiểm soát thu nhập là +0,84 năm cho mỗi lần tăng gấp 1 đơn vị log (tức khoảng +0,6 năm khi chi tiêu tăng gấp đôi), với khoảng tin cậy 95% khoảng [−0,1; +1,2] năm và **không có ý nghĩa thống kê ở mức 5%** (t = 1,76). Ở các năm khác, t dao động từ 1,3 đến 3,3, nên bằng chứng không ổn định.
3. **Vượt / dưới kỳ vọng:** kỳ vọng được lấy từ hồi quy tuổi thọ theo log(GDP/người PPP). Những nước vượt nhiều nhất (2019): Palestine (+7,7 năm), Quần đảo Solomon (+7,6), Tajikistan (+6,6), Syria (+6,6), Nicaragua (+6,2). Những nước dưới kỳ vọng nhiều nhất: Cộng hòa Trung Phi (−25,3, nhưng xem cảnh báo dữ liệu), Nigeria (−16,0), Xích Đạo Guinea (−11,4), Eswatini (−10,4), Nauru (−9,6).
4. **Việt Nam:** tuổi thọ 74,2 năm, kỳ vọng theo thu nhập 71,3 năm → **vượt kỳ vọng +2,9 năm, hạng 45/186** (nhóm top ~24%). Năm 2023: +1,9 năm, hạng 56/184. Chi tiêu y tế của Việt Nam (171 USD/người, 2019) thấp hơn trung vị nhóm thu nhập trung bình cao (389 USD); chỉ 3/57 nước cùng nhóm chi ít hơn.

## Phương pháp

- **Dữ liệu:** World Bank WDI, ba chỉ số: tuổi thọ khi sinh (SP.DYN.LE00.IN), chi tiêu y tế bình quân đầu người USD hiện hành (SH.XPD.CHEX.PC.CD), GDP/người PPP USD hiện hành (NY.GDP.PCAP.PP.CD). Loại các dòng tổng hợp khu vực/nhóm thu nhập (không có nhóm thu nhập trong metadata).
- **Năm chính: 2019.** Năm gần nhất có nhiều quốc gia đủ cả ba chỉ số (186). Chọn 2019 để tránh cú sốc COVID-19 của 2020–2021. 2023 (184 nước) là kiểm tra độ nhạy.
- **Kỳ vọng theo thu nhập:** hồi quy tuyến tính tuổi thọ ~ log(GDP/người PPP); khoảng cách = thực tế − dự báo. Kiểm tra bằng mô hình bậc 2 trong log(GDP): thứ hạng gần như giống hệt (tương quan của khoảng cách 0,995–1,0).
- **Kiểm định “chi tiêu có thêm giá trị không”:** hồi quy tuổi thọ ~ log(GDP) + log(chi tiêu), so sánh hệ số và R².
- **Mã:** `analysis.py`, `make_charts.py`, `robust_lists.py`.

## Độ tin cậy và cảnh báo

- **Tương quan, không phải nhân quả.** Dữ liệu quan sát, một thời điểm (cắt ngang); thu nhập và chi tiêu rất tương quan với nhau nên khó tách riêng hiệu ứng của chi tiêu.
- **Cộng hòa Trung Phi (2019) có vẻ là lỗi dữ liệu:** tuổi thọ ước tính 31,5 năm, trong khi các năm lân cận dao động bất thường (50,6 năm năm 2020; 18,8 năm năm 2022; 57,4 năm năm 2023). Không nên dùng con số này để kết luận; nó được giữ trong bảng gốc nhưng không đưa vào danh sách “ổn định”.
- **Thu nhập PPP bị méo ở nước giàu tài nguyên** (Xích Đạo Guinea, Brunei, Nauru); Palestine và Syria có ước tính trong bối cảnh xung đột, độ chắc chắn thấp.
- **Danh sách ổn định qua 2019 và 2023** (nằm trong top/bottom 15 cả hai năm):
  - Vượt kỳ vọng: Quần đảo Solomon, Jordan, Malawi, Vanuatu, Cabo Verde, Nicaragua, Tajikistan, Morocco, Nhật Bản, Bangladesh, Burundi.
  - Dưới kỳ vọng: Botswana, Nam Phi, Angola, Côte d'Ivoire, Brunei, Lesotho, Chad, Nauru, Eswatini, Xích Đạo Guinea, Nigeria.
  - Việt Nam không nằm trong danh sách “ổn định top 15” (hạng 45–56), nhưng vẫn ở phía vượt kỳ vọng trong cả hai năm.

## Ý nghĩa cho Bộ Y tế

Chi tiêu y tế lớn hơn không tự động đồng nghĩa tuổi thọ cao hơn sau khi tính đến thu nhập. Việt Nam đạt tuổi thọ cao hơn mức thu nhập dự báo với chi tiêu thấp hơn đa số nước cùng nhóm. Đây là tín hiệu tích cực về hiệu quả, nhưng cần kiểm tra thêm bằng dữ liệu theo nhóm bệnh, tuyến y tế và nguồn chi (túi tiền người dân, bảo hiểm) trước khi kết luận về chính sách.
