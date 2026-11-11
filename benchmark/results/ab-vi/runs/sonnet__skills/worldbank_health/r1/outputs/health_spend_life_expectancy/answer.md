# Chi tiêu y tế, thu nhập và tuổi thọ (World Bank, 2023)

## Trả lời
1. **Chi y tế cao hơn đi cùng tuổi thọ cao hơn:** có (r = 0,83 giữa log chi y tế/người và tuổi thọ, n = 184). Nhưng thu nhập giải thích mạnh hơn (r = 0,86). Sau khi kiểm soát GDP/người PPP, chi y tế chỉ còn liên hệ nhỏ: +10% chi tiêu ≈ +0,11 năm (hệ số theo log 1,14, CI 95% 0,16–2,11; tương quan riêng phần 0,22). Chỉ là mối liên hệ, không phải nhân quả.
2. **Vượt kỳ vọng nhất (so với tuổi thọ dự đoán từ thu nhập):** Solomon +7,2, Jordan +6,6, Lebanon +6,1, Malawi +5,9, Maldives +5,7 năm. **Dưới kỳ vọng nhất:** Nigeria −15,3, Nauru −9,8, Guinea Xích đạo −9,6, Guyana −9,3, Chad −8,5 năm.
3. **Việt Nam:** tuổi thọ 74,6 so với kỳ vọng 72,6, tức **+1,9 năm, hạng 56/184** (bootstrap: hạng 54–58). Chi y tế 197 US$/người (hạng 125). Năm 2019: +2,9 năm, hạng 45.

## Phương pháp
- Lấy năm 2023 (năm mới nhất đủ dữ liệu chi y tế); loại nhóm tổng hợp; giữ 184/217 quốc gia có đủ 3 chỉ số.
- Mô hình OLS: tuổi thọ ~ log(GDP/người PPP). Phần dư = tuổi thọ thực − kỳ vọng. Mô hình thêm log(chi y tế) dùng sai số chuẩn HC3.
- Độ vững: bootstrap 2.000 lần, so sánh năm 2019, so với 28 nước có GDP trong ±25% của Việt Nam.

## Lưu ý
- Chi y tế theo US$ hiện hành, GDP theo PPP (không cùng cơ sở); có thể đánh giá thấp chi tiêu hiệu dụng của Việt Nam.
- Đây là liên hệ quan sát; phần dư gồm cả sai số mô hình và yếu tố ngoài y tế. Tuổi thọ ở một số nước là ước tính không chắc chắn; nước đảo nhỏ biến động lớn.
- 33 nước/vùng thiếu dữ liệu bị loại.

Tệp: `analysis.py`, `residuals_all_countries.csv`, `top10_over.csv`, `top10_under.csv`, `vietnam_income_peers.csv`, `summary_stats.csv`, `fig1..3*.png`, `story.md`.
