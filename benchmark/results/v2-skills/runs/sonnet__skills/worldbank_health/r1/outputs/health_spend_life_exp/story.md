# Chi tiêu y tế và tuổi thọ: Việt Nam sống thọ hơn mức "đáng có" theo thu nhập

**Thông điệp chính:** Việt Nam có tuổi thọ 74,6 năm, cao hơn khoảng 1,9 năm so với mức kỳ vọng của một nước có cùng thu nhập, dù chi tiêu y tế chỉ khoảng 197 US$/người. Lợi thế này tích cực nhưng khiêm tốn, và đang thu hẹp.

**Đối tượng:** Lãnh đạo Bộ Y tế, những người cần biết Việt Nam đang ở đâu so với thế giới và nên đọc các so sánh quốc tế thận trọng đến mức nào.

## 1. Bối cảnh
Chúng tôi so sánh 184 quốc gia và vùng lãnh thổ năm 2023 (dữ liệu World Bank, WHO) về tuổi thọ, chi tiêu y tế bình quân đầu người và GDP/người theo sức mua (PPP).

## 2. Vấn đề
Nước chi nhiều cho y tế có sống thọ hơn không? Và nếu nước giàu vốn đã chi nhiều, thì những nước nào thực sự sống thọ hơn mức thu nhập cho phép?

## 3. Phát hiện
**Chi nhiều hơn đi cùng sống thọ hơn, nhưng phần lớn là hiệu ứng của thu nhập.** Mỗi lần chi tiêu y tế gấp đôi đi cùng tuổi thọ cao hơn khoảng 2,5 năm (tương quan 0,83). Khi tính đến thu nhập, phần riêng của chi tiêu y tế còn khoảng 0,8 năm mỗi lần gấp đôi, và con số này không ổn định giữa 2019, 2022 và 2023. Thu nhập giải thích tuổi thọ tốt hơn chi tiêu y tế (R² 0,75 so với 0,69). [Biểu đồ 1](chart1_spend_vs_life.png)

**Những nước vượt và dưới kỳ vọng nhiều nhất** [Biểu đồ 2](chart2_over_under.png), [Biểu đồ 3](chart3_residual_ranking.png)
- Vượt kỳ vọng: Quần đảo Solomon (+7,2 năm), Jordan (+6,6), Liban (+6,1), Malawi (+5,9), Maldives (+5,7).
- Dưới kỳ vọng: Nigeria (−15,3), Nauru (−9,8), Guinea Xích đạo (−9,6), Guyana (−9,3), Chad (−8,5).
- Nhóm này khá ổn định: khi chạy lại với 2022, cả 10 nước vượt và cả 10 nước dưới kỳ vọng nhiều nhất của 2023 vẫn nằm trong nhóm 20 đầu hoặc 20 cuối; với 2019 là 7 và 9 nước.

**Việt Nam:** hạng 56/184 về mức vượt kỳ vọng (+1,9 năm), hạng 16/56 trong nhóm thu nhập trung bình cao. Chi tiêu y tế 197 US$/người thấp hơn khoảng 68% số nước. Trong 19 nước có chi tiêu tương đương, Việt Nam có tuổi thọ cao hơn 68% (74,6 năm so với trung vị 71,6). Mức vượt kỳ vọng qua các năm giảm từ +2,9 (2019) và +2,7 (2022) xuống +1,9 (2023). Độ lệch chuẩn giữa các nước là 3,6 năm, nên Việt Nam chỉ nhỉnh hơn bình thường, chưa phải ngoại lệ.

## 4. Gợi ý hành động (đề xuất, không phải kết luận của dữ liệu)
- Dùng "vượt/dưới kỳ vọng" làm công cụ định vị, không phải bằng chứng rằng tăng ngân sách sẽ tăng tuổi thọ. Dữ liệu này không chứng minh nhân quả.
- Theo dõi vì sao khoảng cách có lợi đang thu hẹp, bằng các số liệu chi tiết hơn (tỷ lệ tử vong theo nhóm tuổi, bệnh không lây nhiễm, vùng miền).
- Chọn một vài nước vượt kỳ vọng nhưng thu nhập gần Việt Nam (Jordan, Sri Lanka, Maldives, Nicaragua) để nghiên cứu chính sách, kèm kiểm tra bối cảnh riêng của từng nước.

## Lưu ý
- Đây là so sánh quan sát giữa các nước. Không kết luận được chi tiêu y tế gây ra tuổi thọ cao.
- Chi tiêu y tế tính bằng US$ hiện hành, còn GDP tính theo PPP, nên chi tiêu của Việt Nam có thể bị đánh giá thấp so với sức mua thực.
- Các nước nhỏ hoặc có xung đột (Nauru, Nigeria, Chad) có số liệu ít ổn định hơn.
- Kết quả là trung bình quốc gia, không thể hiện chênh lệch giữa các vùng hay nhóm dân cư.

Chi tiết và mã nguồn: `answer.md`, `analysis.py`, `residuals_2023.csv`.
