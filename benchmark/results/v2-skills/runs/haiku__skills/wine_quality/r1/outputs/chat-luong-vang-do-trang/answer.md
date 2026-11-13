# Rượu vang nào được chấm điểm cao nhất? Vang đỏ/trắng và vang Pháp/Bồ Đào Nha

## Trả lời ngắn gọn

- **Không trả lời được** phần "giống nho" và "mức giá": bộ dữ liệu không có cột giống nho và không có giá bán (xác nhận trong `data/winequality.names`).
- **Không trả lời được** phần "Pháp hay Bồ Đào Nha": toàn bộ 6.497 mẫu đều là vang Vinho Verde của Bồ Đào Nha (đỏ 1.599, trắng 4.898). Không có cột xuất xứ, nên không thể so sánh với vang Pháp.
- **Phần trả lời được (câu hỏi thu hẹp):** Trong vang Vinho Verde, **vang trắng được chấm điểm cao hơn vang đỏ** khoảng 0,23–0,24 điểm (trên thang 0–10). Điểm cao nhất (từ 7 trở lên) gặp ở cả hai loại, nhưng tập trung ở rượu có **độ cồn cao**.

## Bằng chứng

**1. Vang trắng so với vang đỏ** (điểm chất lượng, thang 0–10)

| Loại | n (gốc) | Điểm TB (95% CI) | Tỉ lệ điểm ≥ 7 | n (đã loại trùng) | Điểm TB (đã loại trùng) |
|---|---|---|---|---|---|
| Trắng | 4.898 | 5,88 (5,85–5,90) | 21,6% | 3.961 | 5,86 |
| Đỏ | 1.599 | 5,64 (5,60–5,68) | 13,6% | 1.359 | 5,62 |

- Chênh lệch (trắng − đỏ): +0,24 điểm (gốc); +0,23 điểm (đã loại trùng).
- Kiểm định Mann-Whitney: p < 10⁻¹⁸ ở cả hai cách xử lý dữ liệu. Kết luận không đổi.

**2. Điểm cao nhất nằm ở đâu?** Trên dữ liệu đã loại trùng lặp:
- Điểm 8 trở lên: 136 mẫu vang trắng (3,4%) và 17 mẫu vang đỏ (1,3%).
- Điểm 9: chỉ 5 mẫu, đều là vang trắng.

**3. Độ cồn liên quan mạnh nhất tới điểm cao** (dữ liệu đã loại trùng; chia 4 nhóm theo độ cồn)

| Loại | Nhóm độ cồn | n | Điểm TB | Tỉ lệ điểm ≥ 7 |
|---|---|---|---|---|
| Trắng | Thấp nhất (Q1) | 1.020 | 5,40 | 4,8% |
| Trắng | Cao nhất (Q4) | 969 | 6,46 | 46,9% |
| Đỏ | Thấp nhất (Q1) | 374 | 5,23 | 0,8% |
| Đỏ | Cao nhất (Q4) | 247 | 6,34 | 40,9% |

- Tương quan Spearman giữa độ cồn và điểm: ρ ≈ 0,48 (trắng) và ρ ≈ 0,49 (đỏ), đều p < 0,001.

## Phương pháp

- Gộp hai file `winequality-red.csv` và `winequality-white.csv` (phân cách bằng dấu `;`), thêm cột loại vang.
- Phát hiện 240 dòng trùng hoàn toàn ở vang đỏ và 937 dòng ở vang trắng. Báo cáo cả hai cách xử lý: có trùng lặp và đã loại trùng lặp. Kết luận giống nhau.
- So sánh điểm bằng Mann-Whitney và Welch t-test. So sánh tỉ lệ điểm ≥ 7 bằng chi-square.
- Tương quan bằng Spearman, vì điểm là thang thứ hạng rời rạc.
- Script: `analysis.py`. Log đầy đủ: `analysis_log.txt`.

## Hạn chế

- **Dữ liệu quan sát, không phải thí nghiệm.** Các kết quả chỉ thể hiện **liên quan**, không chứng minh độ cồn *làm tăng* điểm hay màu trắng *tốt hơn*.
- **Điểm là đánh giá cảm quan** (trung vị của ít nhất 3 chuyên gia), nên có thể mang tính chủ quan.
- **Chỉ có vang Vinho Verde của Bồ Đào Nha.** Không thể khái quát sang vang Pháp hoặc các vùng khác.
- **Không có giá, giống nho, nhà sản xuất, hay năm sản xuất**, nên không thể trả lời về mối quan hệ giữa giá và chất lượng.
- Độ cồn và các biến hóa học có tương quan với nhau, nên không thể tách riêng tác động của từng biến nếu không có mô hình đa biến (chưa chạy trong phân tích này).
