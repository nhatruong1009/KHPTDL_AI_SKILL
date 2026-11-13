# Trả lời: chi tiêu y tế, thu nhập và tuổi thọ

**Ngắn gọn:** Có, các nước chi tiêu y tế đầu người nhiều hơn thường có tuổi thọ cao hơn (r = 0,81, năm 2019, 186 nước). Nhưng khi tính đến GDP bình quân đầu người, chi tiêu gần như không giải thích thêm: thu nhập giải thích 72% sự khác biệt tuổi thọ, thêm chi tiêu chỉ tăng R² lên 0,73. Hệ số chi tiêu sau khi kiểm soát thu nhập là 0,94 năm mỗi đơn vị log (SE 0,50, t ≈ 1,9, ở ngưỡng biên).

**Vượt kỳ vọng nhiều nhất (sau khi kiểm soát thu nhập):** Solomon Islands (+7,6 năm), West Bank and Gaza (+7,6), Tajikistan (+6,6), Syria (+6,6), Burundi (+6,5), Nicaragua (+6,1), Malawi (+6,1), Vanuatu (+6,0).

**Dưới kỳ vọng nhiều nhất:** Central African Republic (−25,0, nhưng dữ liệu nghi ngờ), Nigeria (−16,1), Equatorial Guinea (−11,4), Eswatini (−10,4), Nauru (−9,7), Chad (−8,9), Lesotho (−7,2), Brunei Darussalam (−7,1).

**Việt Nam:** tuổi thọ 74,2 năm, kỳ vọng theo thu nhập 71,4 năm, chênh **+2,9 năm**, hạng **47/186** (vượt kỳ vọng). Chi tiêu y tế đầu người 171 USD. Chênh lệch dương cũng xuất hiện ở năm 2015 (+4,8) và 2023 (+2,3).

## Phương pháp

- Dữ liệu: World Bank WDI, ba chỉ số: tuổi thọ (SP.DYN.LE00.IN), chi tiêu y tế đầu người USD hiện hành (SH.XPD.CHEX.PC.CD), GDP đầu người PPP (NY.GDP.PCAP.PP.CD).
- Năm phân tích: **2019** (trước đại dịch, độ phủ đầy đủ nhất). Kiểm tra độ bền vững với 2015 và 2023.
- Mẫu: 186 nước có nhóm thu nhập và đủ ba chỉ số; đã loại các tổng hợp khu vực.
- Kỳ vọng: hồi quy tuổi thọ theo ln(GDP/người PPP) và bình phương của nó; chênh lệch = thực tế − kỳ vọng.
- Chi tiêu được thêm vào hồi quy thứ hai để kiểm tra đóng góp sau khi kiểm soát thu nhập.

## Hạn chế

- Tương quan cắt ngang, không phải nhân quả.
- Chi tiêu bằng USD hiện hành, thu nhập bằng PPP: không cùng cơ sở tiền tệ.
- Central African Republic 2019 (31,5 năm) là điểm bất thường, dữ liệu chuỗi thời gian của nước này không ổn định. Kết luận về chi tiêu vẫn đúng khi bỏ nước này (hệ số 1,13).
- Một số nước vượt/dưới kỳ vọng nhiều (Syria, Burundi, Malawi, Nigeria) có thể chịu ảnh hưởng của xung đột, HIV, hoặc chất lượng dữ liệu; chưa kiểm định nguyên nhân.
- Tên nước theo WB: "Naoero" được hiển thị là Nauru trên biểu đồ.
- **Chưa chạy validator bảng màu** (`scripts/validate_palette.js`) vì lệnh cần phê duyệt quyền mà môi trường không cấp. Màu biểu đồ lấy trực tiếp từ các slot đã kiểm chứng trong bảng màu tham chiếu (xanh #2a78d6 cho Việt Nam và các nước vượt kỳ vọng, đỏ #e34948 cho các nước dưới kỳ vọng, xám cho điểm nền), nhưng chưa được kiểm tra lại trong môi trường này.

## File đầu ra

- `story.md`: data story ngắn cho lãnh đạo Bộ Y tế.
- `charts/bieu_do_1_tuoi_tho_vs_thu_nhap.png`: tuổi thọ theo GDP/người, có đường kỳ vọng và Việt Nam.
- `charts/bieu_do_2_chenh_lech_ky_vong.png`: top 8 vượt, top 8 dưới kỳ vọng, và Việt Nam.
- `tables/ty_le_ky_vong_2019.csv`: chênh lệch đầy đủ 186 nước (năm 2019).
- `tables/theo_nhom_thu_nhap_2019.csv`, `tables/tom_tat_2019.csv`.
- `code/`: `load.py`, `analysis.py`, `check.py`, `charts.py`, và nhật ký chạy (`analysis_log.txt`, `check_log.txt`).
