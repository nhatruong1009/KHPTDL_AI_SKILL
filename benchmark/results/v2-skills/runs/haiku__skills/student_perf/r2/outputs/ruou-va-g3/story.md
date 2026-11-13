# Câu chuyện: Rượu, điểm số và điều thực sự đứng sau

**Thông điệp chính:** Học sinh uống nhiều rượu có điểm cuối kỳ thấp hơn, nhưng khoảng cách này gần như biến mất khi so sánh học sinh có cùng điểm các kỳ trước. Vấn đề nằm ở học lực có sẵn, không phải riêng ở rượu.

## 1. Bối cảnh
Dữ liệu gồm 395 học sinh môn Toán và 649 học sinh môn Bồ Đào Nha, trong đó 366 học sinh học cả hai môn. Câu hỏi: học sinh uống nhiều rượu có điểm cuối kỳ (G3) thấp hơn không?

## 2. Điều đầu tiên ta thấy
Chưa điều chỉnh, nhóm uống nhiều (mức 4–5) có G3 thấp hơn nhóm uống ít (mức 1–2) khoảng 1,4 điểm (cuối tuần) đến 1,7 điểm (ngày thường). Cỡ hiệu ứng khoảng d ≈ −0,5 và có ý nghĩa thống kê (p < 0,001). Biểu đồ: [chart_g3_theo_muc_ruou.png](chart_g3_theo_muc_ruou.png).

## 3. Điều gì thay đổi bức tranh
Khi đưa điểm kỳ 1 và kỳ 2 vào mô hình, mỗi bậc uống chỉ còn khác biệt −0,05 điểm (Walc) và −0,08 điểm (Dalc), không có ý nghĩa thống kê. Học sinh uống nhiều đã có điểm thấp hơn từ trước, và đó là nguồn gốc của khoảng cách ở điểm cuối kỳ. Biểu đồ: [chart_forest_ols.png](chart_forest_ols.png).

## 4. Điều này nghĩa là gì
- Không nên kết luận rằng uống rượu làm giảm điểm. Dữ liệu cho thấy liên quan, và phần lớn liên quan đó đi qua học lực trước đó.
- Những học sinh có điểm thấp ở kỳ 1 và kỳ 2 là nhóm nên được hỗ trợ học tập, bất kể thói quen uống rượu.

## 5. Lưu ý trung thực
- Dữ liệu quan sát, chỉ thể hiện mối liên quan.
- 53 bản ghi có G3 = 0 được coi là không hoàn thành và bị loại khỏi mẫu chính. Kết quả giữ lại chúng vẫn cho cùng kết luận.
- Dalc và Walc là tự khai báo.
