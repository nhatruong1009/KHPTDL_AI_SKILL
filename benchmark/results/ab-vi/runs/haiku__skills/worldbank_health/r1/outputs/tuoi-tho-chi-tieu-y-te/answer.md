# Chi tiêu y tế và tuổi thọ: đã tính đến thu nhập thì sao?

**Câu hỏi:** Các quốc gia chi tiêu y tế nhiều hơn có tuổi thọ cao hơn không? Sau khi tính đến mức thu nhập, quốc gia nào "vượt kỳ vọng" hoặc "dưới kỳ vọng" nhiều nhất, và Việt Nam đứng ở đâu?

## Trả lời ngắn

1. **Có, chi tiêu nhiều hơn đi kèm tuổi thọ cao hơn.** Năm 2023, 184 quốc gia: Spearman ρ = 0,84; nhóm chi tiêu cao nhất (Q5, bình quân ~4.965 USD/người) có tuổi thọ 81,4 năm, nhóm thấp nhất (Q1, ~50 USD) là 64,2 năm.
2. **Nhưng phần lớn mối liên hệ đó là do thu nhập.** Thu nhập (ln GDP/người PPP) một mình giải thích R² = 0,75 phương sai tuổi thọ; thêm chi tiêu y tế chỉ nâng R² lên 0,76. Sau khi giữ thu nhập cố định, chi tiêu vẫn có liên hệ dương nhưng yếu (partial r = 0,20; p = 0,006): gấp đôi chi tiêu ≈ +0,75 năm tuổi thọ (95% CI bootstrap: +0,10 đến +1,53 năm).
3. **Vượt kỳ vọng nhiều nhất:** Jordan (+6,9 năm), Quần đảo Solomon (+6,8), Lebanon (+6,5), Maldives (+6,0), Cabo Verde (+5,8), Nicaragua (+5,7), Vanuatu (+5,6), Sri Lanka (+5,4), Morocco (+5,2), Malawi (+5,2).
4. **Dưới kỳ vọng nhiều nhất:** Nigeria (−15,0; thực tế 54,5 so với kỳ vọng 69,5), Nauru (−9,5), Guyana (−9,4), Guinea Xích Đạo (−9,3), Chad (−8,8), Brunei (−7,0), Lesotho (−6,8), Eswatini (−6,7), Côte d'Ivoire (−6,6), Nam Phi (−6,2).
5. **Việt Nam vượt kỳ vọng +2,3 năm.** Tuổi thọ thực tế 74,6 năm, kỳ vọng theo thu nhập (GDP/người PPP 15.034 USD) là 72,3 năm. Xếp **hạng 49/184** (nhóm top ~27%). Chi tiêu y tế 197 USD/người.

## Phương pháp

- **Dữ liệu:** World Bank WDI, ba chỉ số: tuổi thọ lúc sinh (SP.DYN.LE00.IN), chi tiêu y tế bình quân đầu người tính bằng USD hiện hành (SH.XPD.CHEX.PC.CD), GDP bình quân đầu người theo PPP (NY.GDP.PCAP.PP.CD).
- **Năm phân tích:** 2023, năm gần nhất có đủ ba chỉ số cho ≥150 quốc gia (dữ liệu 2024 chỉ có 22 nước cho chi tiêu y tế). Loại các nhóm tổng hợp (không có Region trong metadata) và giữ các quốc gia có đủ dữ liệu cả ba chỉ số năm 2023: 184 quốc gia.
- **Kỳ vọng theo thu nhập:** hồi quy tuổi thọ theo ln(GDP/người) và bình phương của nó (R² = 0,749). Phần dư = tuổi thọ thực tế − kỳ vọng. Dương là "vượt kỳ vọng", âm là "dưới kỳ vọng".
- **Điều chỉnh thu nhập cho chi tiêu:** hồi quy có thêm ln(chi tiêu y tế); hệ số chi tiêu = 1,08 năm/đơn vị ln (CI 95% 0,15–2,21), bootstrap 1.000 lần.
- **Độ nhạy theo năm:** Việt Nam luôn vượt kỳ vọng: 2021 +4,3 (hạng 28), 2022 +2,2 (hạng 57), 2023 +2,3 (hạng 49). Tương quan Spearman chi tiêu–tuổi thọ 0,82–0,84 qua các năm.
- **Việt Nam so với ASEAN (2023, 9 nước được chọn so sánh; Brunei và Đông Timor không nằm trong danh sách này):** Việt Nam +2,3; Campuchia +2,0; Thái Lan +1,7; Malaysia −0,6; Myanmar −0,7; Philippines −0,8; Lào −0,8; Indonesia −1,3; Singapore −2,6.

## Hạn chế

- **Tương quan, không phải nhân quả.** Kết quả không cho biết chi tiêu làm tăng tuổi thọ bao nhiêu trong thực tế.
- **Đa cộng tuyến mạnh:** ln chi tiêu và ln GDP tương quan 0,91. Hệ số chi tiêu "sau khi giữ thu nhập" dựa trên phần chênh lệch nhỏ và có độ bất định lớn.
- **Chi tiêu tính bằng USD hiện hành, không điều chỉnh sức mua (PPP).** So sánh chi tiêu giữa các nước bị ảnh hưởng bởi mức giá và tỷ giá; chỉ thu nhập được điều chỉnh PPP.
- **Phần dư không phải "hiệu quả" thuần túy.** Nó gộp mọi yếu tố ngoài thu nhập và chi tiêu: bệnh tật (HIV, sốt rét, lao), xung đột, dinh dưỡng, hút thuốc, chất lượng số liệu. Nhiều nước dùng ước lượng mô hình của Liên Hợp Quốc (WPP) thay cho số đo trực tiếp. Dữ liệu không đủ để giải thích nguyên nhân của từng trường hợp.
- **Giá trị cực đoan cần kiểm chứng:** Nigeria (−15 năm) lớn bất thường; nên kiểm tra lại số liệu gốc trước khi dùng để kết luận. Các nước nhỏ (Maldives, Vanuatu, Quần đảo Solomon, Nauru) có số liệu dao động mạnh hơn.
- **Một năm dữ liệu:** Thứ hạng của Việt Nam thay đổi từ 28 đến 57 giữa các năm, nhưng chiều vượt kỳ vọng ổn định.
- Dữ liệu gốc ghi "Naoero"; báo cáo hiển thị là Nauru.

## Tệp đầu ra

- `analysis.py`: toàn bộ mã phân tích (chạy lại được từ thư mục workspace).
- `gap_all_countries.csv`: phần dư của 184 quốc gia; `top15_vuot_ky_vong.csv`, `top15_duoi_ky_vong.csv`.
- `vietnam_asean_peers.csv`, `correlations.csv`, `model_summary.csv`, `quintile_health_exp.csv`, `gap_by_income_group.csv`, `sensitivity_years.csv`, `coverage_by_year.csv`, `panel_year.csv`.
- Biểu đồ: `chart1_scatter_chi_tieu_tuoi_tho.png`, `chart2_ky_vong_theo_thu_nhap.png`, `chart3_top10_vuot_duoi_ky_vong.png`, `chart4_viet_nam_asean.png`, `chart5_quintile_chi_tieu.png`.
