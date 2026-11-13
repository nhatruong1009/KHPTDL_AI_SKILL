# Chi tiêu y tế, thu nhập và tuổi thọ: Việt Nam đang ở đâu?

**Thông điệp chính:** Việt Nam sống thọ hơn khoảng 1,9 năm so với mức mà thu nhập dự báo, dù chi tiêu y tế bình quân chỉ 197 US$/người; so sánh quốc tế cho thấy thu nhập giải thích phần lớn chênh lệch tuổi thọ, còn tác động riêng của chi tiêu y tế chưa rõ ràng.

**Đối tượng:** Lãnh đạo Bộ Y tế, cần định hướng ưu tiên đầu tư và cách đọc các so sánh quốc tế.

## 1. Bối cảnh
Chúng tôi dùng số liệu World Bank năm 2023 cho 184 quốc gia/vùng lãnh thổ: tuổi thọ khi sinh, chi tiêu y tế bình quân đầu người (US$) và GDP bình quân đầu người theo sức mua (PPP).

## 2. Vấn đề
Nước chi nhiều cho y tế có sống thọ hơn không? Và nếu so với những nước có cùng mức thu nhập, ai làm tốt hơn hay kém hơn kỳ vọng, và Việt Nam ở đâu?

## 3. Phát hiện
**a) Nước chi nhiều hơn thường sống thọ hơn, nhưng thu nhập giải thích gần hết.** Tương quan hạng giữa chi tiêu y tế và tuổi thọ là 0,84. Tuy nhiên GDP/người PPP đã giải thích 75% biến thiên tuổi thọ giữa các nước; thêm chi tiêu y tế chỉ nâng lên 76%. Sau khi kiểm soát thu nhập, liên hệ riêng của chi tiêu y tế nhỏ và không ổn định: có ý nghĩa thống kê năm 2023 (r = 0,22) nhưng không có ở năm 2022 (r = 0,10). Trong nhóm nước thu nhập thấp, hầu như không thấy liên hệ (Spearman ≈ 0). [Biểu đồ 1](01_chi_tieu_vs_tuoi_tho.png)

**b) Có những nước sống thọ hơn hẳn hoặc kém hơn hẳn mức thu nhập.** Vượt kỳ vọng nhiều nhất: Quần đảo Solomon (+7,2 năm), Jordan (+6,6), Lebanon (+6,1), Malawi (+5,9), Maldives (+5,7). Dưới kỳ vọng nhiều nhất: Nigeria (−15,3), Nauru (−9,8), Guinea Xích đạo (−9,6), Guyana (−9,3), Chad (−8,5); nhóm dưới kỳ vọng tập trung ở châu Phi cận Sahara. Nhiều nước vượt kỳ vọng chi rất ít (Sri Lanka 134 US$, Malawi 41 US$/người). [Biểu đồ 3](03_vuot_duoi_ky_vong.png)

**c) Việt Nam: trên đường xu thế, chưa thuộc nhóm dẫn đầu.** Tuổi thọ 74,6 năm so với kỳ vọng khoảng 72,6 năm theo GDP PPP 15.034 int-$: vượt +1,9 năm (khoảng tin cậy 95%: +1,4 đến +2,5), hạng 56/184; kết quả tương tự năm 2022 (+2,7). Trong 27 nước cùng mức thu nhập, Việt Nam ở nửa trên, nhưng Lebanon, Jordan, Peru, Sri Lanka, Ecuador, Tunisia và Algeria đạt 76–78 năm; Việt Nam chi 197 US$/người, thấp hơn trung vị nhóm này (333 US$). [Biểu đồ 2](02_phan_du_theo_thu_nhap.png)

## 4. Gợi ý hành động (đề xuất, không phải kết luận của dữ liệu)
- Dùng nhóm nước cùng thu nhập có tuổi thọ cao hơn (Sri Lanka, Jordan, Lebanon...) làm đối sánh để tìm hiểu mô hình chăm sóc ban đầu và hiệu quả chi tiêu, thay vì chỉ so mức chi.
- Không dùng dữ liệu này để kết luận rằng tăng ngân sách sẽ tự động nâng tuổi thọ; cần phân tích theo cơ cấu chi và theo thời gian (dữ liệu chuỗi nhiều năm, chỉ số tử vong theo nguyên nhân).

## Lưu ý
- Đây là so sánh giữa các nước, cho thấy liên hệ chứ không chứng minh nhân quả.
- Chi tiêu y tế tính theo US$ hiện hành, GDP theo PPP: hai thước đo khác nhau, nên chi tiêu của nước giá thấp như Việt Nam có thể bị đánh giá thấp.
- 33 nước thiếu số liệu bị loại; phần dư của các nước nhỏ (Nauru, Solomon...) nhiều nhiễu.

*Nguồn: World Bank WDI (WHO GHED, UN WPP, ICP). Mã và bảng kết quả: `analysis.py`, `phan_du_theo_quoc_gia_2023.csv`.*
