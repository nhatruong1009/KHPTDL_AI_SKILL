# Chi tiêu y tế, thu nhập và tuổi thọ: Việt Nam đứng ở đâu?

**Trả lời ngắn:**
1. **Có, nhưng đây là tương quan, phần lớn đi cùng thu nhập.** Năm 2023 (184 nước), chi tiêu y tế/người và tuổi thọ có tương quan mạnh (Pearson trên ln(chi tiêu) = 0,83; Spearman = 0,84). Mỗi lần chi gấp đôi đi cùng tuổi thọ cao hơn khoảng 2,5 năm (R² = 0,69). Khi đưa thêm GDP/người (PPP) vào mô hình, hiệu ứng riêng của chi tiêu y tế còn khoảng 0,8 năm mỗi lần gấp đôi. Con số này không ổn định giữa các năm: p = 0,003 (2023), 0,19 (2022), 0,08 (2019).
2. **Vượt kỳ vọng nhiều nhất (theo thu nhập):** Quần đảo Solomon (+7,2 năm), Jordan (+6,6), Liban (+6,1), Malawi (+5,9), Maldives (+5,7), Vanuatu (+5,6). **Dưới kỳ vọng nhiều nhất:** Nigeria (−15,3), Nauru (−9,8), Guinea Xích đạo (−9,6), Guyana (−9,3), Chad (−8,5), Eswatini (−7,0).
3. **Việt Nam:** tuổi thọ 74,6 năm, kỳ vọng theo thu nhập 72,6 năm, tức **vượt khoảng +1,9 năm** (hạng 56/184). Trong nhóm thu nhập trung bình cao, Việt Nam xếp 16/56. Mức này nhỉnh hơn trung bình một chút nhưng chưa phải ngoại lệ, vì độ lệch chuẩn của phần dư là 3,6 năm. Với chi tiêu y tế chỉ 197 US$/người (thấp hơn 68% các nước), Việt Nam đạt tuổi thọ cao hơn kỳ vọng, và khoảng cách này tăng lên +4,4 năm (hạng 23) nếu chỉ so theo chi tiêu y tế.

## Bằng chứng
| Mô hình 2023 (n = 184) | R² | Hệ số (năm / mỗi lần gấp đôi) |
|---|---|---|
| Tuổi thọ ~ ln(chi tiêu y tế) | 0,688 | +2,5 |
| Tuổi thọ ~ ln(GDP PPP) | 0,746 | +3,7 |
| Cả hai | 0,758 | chi tiêu +0,8; GDP +2,7 |

- Thu nhập giải thích tuổi thọ tốt hơn chi tiêu y tế (R² 0,75 so với 0,69). Thêm chi tiêu y tế vào mô hình đã có thu nhập chỉ tăng R² thêm 0,012.
- Trong từng nhóm thu nhập, tương quan giữa ln(chi tiêu) và tuổi thọ yếu hơn: thu nhập thấp r = −0,03 (n = 20), trung bình thấp 0,39 (n = 46), trung bình cao 0,20 (n = 56), cao 0,57 (n = 62).
- Việt Nam qua các năm (phần dư theo thu nhập): 2019 +2,9 (hạng 45/186); 2022 +2,7 (47/185); 2023 +1,9 (56/184). Mức vượt kỳ vọng luôn dương nhưng đang thu hẹp.
- So với nước có chi tiêu y tế tương đương (0,7–1,4 lần Việt Nam, n = 19): tuổi thọ trung vị 71,6, Việt Nam 74,6, cao hơn 68% nhóm này.
- Trong khu vực Đông Á–Thái Bình Dương, Việt Nam đứng thứ 10 về phần dư, sau Nhật, Hàn Quốc, Trung Quốc và các đảo nhỏ. Cao hơn Thái Lan (+1,4) và Indonesia (−1,6).

Biểu đồ: [chi tiêu vs tuổi thọ](chart1_spend_vs_life.png) · [vượt/dưới kỳ vọng](chart2_over_under.png) · [xếp hạng](chart3_residual_ranking.png)
Bảng: `residuals_2023.csv`, `model_summary.csv`, `residuals_all_years.csv`

## Phương pháp
- Dữ liệu: World Bank WDI, gồm tuổi thọ khi sinh (SP.DYN.LE00.IN), chi tiêu y tế hiện hành/người (SH.XPD.CHEX.PC.CD) và GDP/người PPP (NY.GDP.PCAP.PP.CD). Đã loại 48 nhóm tổng hợp (không có Region trong metadata). Năm 2023 là năm gần nhất có đủ cả 3 chỉ số cho hầu hết quốc gia (2024 chỉ có chi tiêu y tế của 24 nước).
- "Vượt/dưới kỳ vọng" = phần dư của hồi quy OLS tuổi thọ ~ ln(GDP PPP/người). Phiên bản kiểm soát cả chi tiêu y tế nằm trong `residuals_2023.csv` (cột `res_both`).
- Kiểm tra độ vững: chạy lại với 2022 và 2019. Tương quan hạng của phần dư giữa các năm là 0,94. Trong 10 nước vượt kỳ vọng nhất năm 2023, cả 10 vẫn nằm trong top 20 năm 2022 và 7 nằm trong top 20 năm 2019. Trong 10 nước dưới kỳ vọng nhất, 10 và 9 nước vẫn nằm trong nhóm 20 thấp nhất. Bỏ các nước có tuổi thọ ≤ 55 thì hệ số gần như không đổi (+2,47 năm mỗi lần gấp đôi).

## Giả định và hạn chế
- **Quan sát, không phải nhân quả.** Không thể kết luận tăng chi tiêu y tế sẽ làm tăng tuổi thọ. Chi tiêu cao cũng đi cùng giáo dục, vệ sinh, dinh dưỡng, tuổi dân số và các yếu tố khác mà dữ liệu không có.
- **Lệch đơn vị:** chi tiêu y tế tính bằng US$ hiện hành theo tỷ giá, còn GDP tính theo PPP. Chi tiêu y tế của nước có giá dịch vụ thấp (trong đó có Việt Nam) vì vậy bị đánh giá thấp so với sức mua thực, nên mức "hiệu quả" có thể bị thổi phồng.
- **Dạng hàm:** giả định tuyến tính theo logarit. Thứ hạng của các nước nhỏ và các nước có xung đột hoặc dịch bệnh (Nigeria, Chad, Eswatini, Lesotho) nhạy với các giá trị ngoại lai và với chất lượng ước tính tuổi thọ của Liên Hợp Quốc. Nauru, Palau và các đảo nhỏ có thể bất ổn thống kê.
- Số liệu chi tiêu y tế hoặc GDP bị thiếu ở một số quốc gia/vùng lãnh thổ (còn 184 nước có đủ cả 3 chỉ số trong năm 2023, trên khoảng 217 nước), nên kết quả không phủ toàn bộ các nước. Tuổi thọ là trung bình toàn quốc, không phản ánh chênh lệch giữa các vùng hay nhóm dân cư.
- Phần dư chỉ là chênh lệch so với đường xu hướng toàn cầu, không phải thước đo hiệu quả của hệ thống y tế.
