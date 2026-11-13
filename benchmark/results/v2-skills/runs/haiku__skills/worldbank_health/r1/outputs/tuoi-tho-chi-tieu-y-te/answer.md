**Trả lời:** Có. Các nước chi tiêu y tế bình quân đầu người cao hơn thường có tuổi thọ cao hơn rõ rệt (r = 0,81 trên thang log, n = 186 quốc gia, năm 2019). Nhưng phần lớn mối liên hệ này trùng với thu nhập: GDP bình quân đầu người (PPP) một mình giải thích R² = 0,72 phương sai tuổi thọ; thêm chi tiêu y tế chỉ tăng R² thêm 0,005. Sau khi tính đến thu nhập, chi tiêu y tế có liên hệ dương nhưng yếu (partial r = 0,14; p = 0,06 ở năm 2019), và mức ý nghĩa không ổn định qua các cách tính.

**Quốc gia vượt / dưới kỳ vọng (sau khi tính thu nhập, năm 2019):**
- Vượt kỳ vọng nhiều nhất: Quần đảo Solomon (+7,6 năm), Palestine (+7,6), Tajikistan (+6,7), Syria (+6,6), Burundi (+6,5), Nicaragua (+6,1), Malawi (+6,1), Vanuatu (+6,0), Jordan (+5,9), Albania (+5,7).
- Dưới kỳ vọng nhiều nhất: Cộng hòa Trung Phi (−25,0, nhưng xem cảnh báo dữ liệu bên dưới), Nigeria (−16,1), Guinea Xích Đạo (−11,5), Eswatini (−10,4), Nauru (−9,7), Chad (−8,9), Lesotho (−7,2), Brunei (−7,1), Bahamas (−7,0), Namibia (−7,0).
- **Việt Nam:** tuổi thọ 74,2 năm; kỳ vọng theo thu nhập 71,4 năm; **vượt kỳ vọng +2,9 năm**, xếp **hạng 47/186** (năm 2019). Với trung bình 2017–2019, Việt Nam xếp 38/186 (+3,4 năm); với năm 2022, xếp 57/185 (+2,2 năm). Việt Nam vượt kỳ vọng ở cả ba cách tính.

**Bối cảnh chi tiêu:** Chi tiêu y tế bình quân đầu người của Việt Nam là 171 USD (2019), thấp hơn trung vị nhóm thu nhập trung-cao (389 USD, 57 nước) — nằm trong nhóm thấp nhất khoảng 5% của nhóm này. Tuổi thọ của Việt Nam (74,2) vẫn cao hơn trung vị nhóm (73,7).

**Bằng chứng:**
- [Biểu đồ 1: tuổi thọ theo chi tiêu y tế](chart1_le_vs_chi_tieu_2019.png)
- [Biểu đồ 2: kỳ vọng theo thu nhập và các nước ngoại lệ](chart2_ky_vong_theo_thu_nhap_2019.png)
- Bảng xếp hạng đầy đủ: `ranking_2019.csv` (cũng có `ranking_2022_sensitivity.csv`, `ranking_tb3nam_2017_2019_sensitivity.csv`)

**Cách làm:**
- Dữ liệu: World Bank WDI — tuổi thọ (SP.DYN.LE00.IN), chi tiêu y tế bình quân đầu người theo USD hiện hành (SH.XPD.CHEX.PC.CD), GDP bình quân đầu người PPP theo USD quốc tế hiện hành (NY.GDP.PCAP.PP.CD).
- Năm chính: 2019 (trước đại dịch COVID-19), chỉ giữ quốc gia có đủ cả ba chỉ số và có Region trong metadata (loại các tổng hợp khu vực/nhóm thu nhập). n = 186.
- Mô hình thu nhập: tuổi thọ ~ log(GDP) + log(GDP)², đường "kỳ vọng". Chênh lệch = tuổi thọ thực tế − kỳ vọng.
- Kiểm tra chi tiêu sau thu nhập: hồi quy tuổi thọ ~ log(chi tiêu) + log(GDP) + log(GDP)²; và partial correlation giữa phần dư.
- Độ nhạy: năm 2022 và trung bình 2017–2019. Thứ hạng chênh lệch gần như giống nhau (Spearman 0,95 với 2022; 0,99 với trung bình 3 năm).
- Chi tiết: `analysis.py`.

**Giả định và cảnh báo:**
- **Dữ liệu Cộng hòa Trung Phi không đáng tin:** chuỗi tuổi thọ của nước này dao động bất thường (40,3 → 51,9 → … → 31,5 năm 2019 → 18,8 năm 2022 → 57,4 năm 2023). Mức chênh −25 năm vì vậy phần lớn là lỗi/độ biến động của nguồn dữ liệu, không phải kết quả thực. Với trung bình 3 năm, chênh lệch còn −13,9 năm, vẫn là ngoại lệ nhưng không còn cực đoan. Không nên dùng con số −25 năm trong các báo cáo.
- Các nước nhỏ (Nauru, Quần đảo Solomon, Vanuatu, Bahamas, Brunei) có chi tiêu và tuổi thọ dao động mạnh; coi là nhiễu, không phải mẫu đại diện.
- Chi tiêu đo bằng USD hiện hành, nên chịu ảnh hưởng tỷ giá; GDP và chi tiêu cùng bị ảnh hưởng bởi tỷ giá, nên có thể làm tăng tương quan giả.
- Đây là dữ liệu quan sát: cho thấy liên hệ (association), không chứng minh nhân quả. Chênh lệch "vượt/dưới kỳ vọng" là so với mô hình chỉ có thu nhập, chưa tính đến các yếu tố khác (giáo dục, HIV, xung đột, cơ cấu tuổi, chất lượng quản trị).
- Thứ hạng là tương đối; với n = 186, một số nước thứ hạng chỉ cách nhau vài năm.
- Các giả thuyết về lý do (ví dụ gánh nặng HIV ở Nam Phi) là gợi ý để kiểm tra thêm, không phải kết luận từ dữ liệu này.
