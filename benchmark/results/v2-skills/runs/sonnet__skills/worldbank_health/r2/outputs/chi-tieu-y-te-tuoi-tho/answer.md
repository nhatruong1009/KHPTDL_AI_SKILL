**Trả lời:** Có, nhưng phần lớn là do thu nhập. Năm 2023, nước chi tiêu y tế bình quân đầu người cao hơn thường có tuổi thọ cao hơn (Spearman = 0,84; n = 184 quốc gia/vùng lãnh thổ). Khi đã tính đến GDP/người PPP, phần "cộng thêm" của chi tiêu y tế nhỏ và không ổn định: tương quan riêng phần r = 0,22 (p = 0,003) năm 2023 nhưng chỉ r = 0,10 (p = 0,19) năm 2022. Việt Nam sống thọ hơn kỳ vọng theo thu nhập khoảng **+1,9 năm** (74,6 so với ~72,6 dự đoán), xếp hạng 56/184 về mức "vượt kỳ vọng", thuộc nhóm nhỉnh hơn mức trung bình chứ chưa phải nhóm nổi bật nhất.

**Bằng chứng**

1. Chi tiêu y tế và tuổi thọ ([biểu đồ 1](01_chi_tieu_vs_tuoi_tho.png)): R² của hồi quy tuổi thọ ~ ln(chi tiêu y tế) = 0,69; của tuổi thọ ~ ln(GDP PPP) = 0,75; cả hai biến = 0,76. Thêm chi tiêu y tế vào mô hình đã có thu nhập chỉ tăng R² thêm khoảng 0,01. Trong từng nhóm thu nhập, mối liên hệ yếu hơn nhiều: Spearman 0,67 (thu nhập cao), 0,42 (trung bình thấp), 0,25 (trung bình cao), ≈0 (thu nhập thấp).
2. Vượt/dưới kỳ vọng (phần dư của tuổi thọ ~ ln GDP PPP, độ lệch chuẩn phần dư 3,6 năm; [biểu đồ 2](02_phan_du_theo_thu_nhap.png), [biểu đồ 3](03_vuot_duoi_ky_vong.png), bảng đầy đủ: `phan_du_theo_quoc_gia_2023.csv`):

| Vượt kỳ vọng nhất | Năm | Dưới kỳ vọng nhất | Năm |
|---|---|---|---|
| Quần đảo Solomon | +7,2 | Nigeria | −15,3 |
| Jordan | +6,6 | Nauru | −9,8 |
| Lebanon | +6,1 | Guinea Xích đạo | −9,6 |
| Malawi | +5,9 | Guyana | −9,3 |
| Maldives | +5,7 | Chad | −8,5 |
| Vanuatu | +5,6 | Eswatini | −7,0 |
| Cabo Verde | +5,4 | Côte d'Ivoire | −6,8 |
| Nicaragua | +5,4 | Nam Phi | −6,6 |
| Sri Lanka | +5,0 | Lesotho | −6,5 |
| Tajikistan | +5,0 | Brunei | −6,5 |

   Nhóm dưới kỳ vọng tập trung ở châu Phi cận Sahara (và vài nền kinh tế giàu tài nguyên/đảo nhỏ). Nhóm vượt kỳ vọng gồm nhiều nước chi tiêu y tế thấp (Sri Lanka 134 US$, Tajikistan 85 US$, Malawi 41 US$).
3. Việt Nam (2023): tuổi thọ 74,6; GDP PPP 15.034 int-$; chi tiêu y tế 197 US$/người. Phần dư +1,94 năm (khoảng tin cậy bootstrap 95%: +1,4 đến +2,5), hạng 56/184. Nếu kiểm soát cả chi tiêu y tế, phần dư là +2,73 năm (hạng 44). Năm 2022: +2,72. So với 27 nước có GDP PPP trong ±25% mức của Việt Nam, Việt Nam đứng giữa nhóm trên (tuổi thọ trung vị nhóm đó 72,1; chi tiêu y tế trung vị 333 US$ so với 197 US$ của Việt Nam). Các nước cùng mức thu nhập có tuổi thọ cao hơn Việt Nam gồm Lebanon, Jordan, Peru, Sri Lanka, Ecuador, Tunisia, Algeria (76,3–77,8) ([nhom_tuong_dong_vn.csv](nhom_tuong_dong_vn.csv)).

**Cách làm**
- Dữ liệu: World Bank WDI, 3 chỉ số năm 2023 (tuổi thọ khi sinh SP.DYN.LE00.IN; chi tiêu y tế hiện hành/người SH.XPD.CHEX.PC.CD, US$ hiện hành; GDP/người PPP NY.GDP.PCAP.PP.CD). Bỏ 49 dòng tổng hợp khu vực (không có `Region` trong metadata) → 217 quốc gia/vùng; còn 184 sau khi bỏ các nước thiếu ít nhất một chỉ số.
- Mô hình "kỳ vọng": OLS tuổi thọ ~ ln(GDP PPP). Phần dư = tuổi thọ thực − kỳ vọng. Mô hình thay thế: thêm ln(chi tiêu y tế). Thêm số hạng bậc hai của ln(GDP) gần như không cải thiện (R² 0,746 → 0,749).
- Kiểm tra độ vững: lặp lại với năm 2022 (tương quan hạng của phần dư 2023 vs 2022 = 0,94; hai mô hình 2023 = 0,97). Trong top 15 vượt kỳ vọng, 14/15 nước trùng giữa 2023 và 2022, 12/15 trùng giữa hai mô hình; top 15 dưới kỳ vọng trùng 11/15 và 12/15.

**Giả định & hạn chế**
- Đây là liên hệ giữa các quốc gia tại một năm, không chứng minh chi tiêu y tế làm tăng tuổi thọ (chiều ngược lại và các yếu tố nhiễu như giáo dục, dinh dưỡng, nước sạch, xung đột, HIV đều có thể tác động).
- Chi tiêu y tế tính bằng US$ hiện hành (tỷ giá), còn GDP bằng PPP, nên không cùng thước đo; với nước có giá dịch vụ thấp như Việt Nam, chi tiêu thực có thể được đánh giá thấp so với giá trị 197 US$.
- Hệ số chi tiêu y tế sau khi kiểm soát thu nhập đổi từ 1,14 (p = 0,003, năm 2023) sang 0,68 (p = 0,19, năm 2022): kết luận "chi tiêu có tác dụng thêm" chưa vững, nên báo cáo ở mức "yếu/không ổn định".
- Phần dư của nước nhỏ hoặc nước nhiều biến động (Nauru, Palau, Solomon, Guyana, Brunei) và các nước có số liệu tuổi thọ ước tính chịu sai số lớn; số liệu 2023 có thể là ước tính. 33 nước thiếu dữ liệu bị loại (có thể lệch mẫu).
- Sai số bootstrap của phần dư Việt Nam chỉ phản ánh độ bất định của đường hồi quy, không bao gồm sai số đo lường tuổi thọ.
