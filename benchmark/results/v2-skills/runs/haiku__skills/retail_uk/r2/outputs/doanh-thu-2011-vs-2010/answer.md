# Doanh thu thuần 2011 so với 2010: tăng nhờ khách mới, còn khách cũ đang mất đi

## Trả lời ngắn gọn
- **So sánh công bằng (Tháng 1–11, cả hai năm):** doanh thu thuần 2011 là **8,546,582 GBP**, 2010 là **8,332,860 GBP**. Mức thay đổi là **+213,722 GBP (+2.6%)**.
- **Phần thay đổi đến từ khách hàng mới:** khách mua lần đầu trong 2011 mang lại **+1,309,116 GBP** (1,494 khách). Khách cũ (những người có mua trong 2010) giảm **−1,453,338 GBP** (−19.5%), trong đó khách rời đi chiếm −1,115,434 GBP (1,539 khách) và khách mua cả hai năm giảm −337,904 GBP. Phần còn lại: khách quay lại +76,337 GBP, nhóm chỉ có hoàn trả +101,163 GBP, và các giao dịch không có Customer ID +180,444 GBP.
- **Thị trường:** Vương quốc Anh (UK) gần như đi ngang (+10,551 GBP, +0.15%), nên toàn bộ mức tăng đến từ thị trường ngoài UK (+203,171 GBP, +16.4%). Các thị trường kéo tăng mạnh nhất là **Úc (+106,688 GBP)**, **Pháp (+61,850 GBP)**, **Na Uy (+28,784 GBP)** và **Tây Ban Nha (+24,302 GBP)**. Các thị trường kéo giảm mạnh nhất là **Ireland/EIRE (−81,192 GBP, −25%)**, **Đan Mạch (−26,989 GBP, −61%)** và **Thụy Điển (−16,991 GBP, −33%)**.

## Phương pháp
- **Dữ liệu:** `data/online_retail_II.xlsx`, gộp hai sheet (2009–2010 và 2010–2011). Hai sheet trùng nhau từ 1–9/12/2010, và có các dòng trùng hoàn toàn. Sau khi loại trùng, còn 1,033,036 dòng (loại 34,335 dòng).
- **Chỉ tiêu:** doanh thu thuần = `Quantity × Price`, gồm cả dòng hoàn trả (hóa đơn bắt đầu bằng "C", số lượng âm). Đây là doanh thu sau hoàn trả.
- **Kỳ so sánh:** Tháng 1–11 của cả hai năm. Tháng 12/2011 chỉ có dữ liệu đến ngày 9/12, và tháng 12/2010 chỉ là một phần của sheet 2010–2011, nên hai tháng này bị loại để tránh so sánh lệch. (Để tham khảo: cả năm 2010 là 9,079,584 GBP; 2011 đến 9/12 là 8,979,301 GBP. Hai con số này không so sánh công bằng.)
- **Khách mới / khách cũ:** dựa trên ngày mua đầu tiên của mỗi Customer ID trong toàn bộ dữ liệu. Phân rã theo cấp khách hàng (bridge): so sánh doanh thu của từng khách trong Tháng 1–11 của 2010 và 2011.
- **Thị trường:** theo cột `Country`.
- **Kiểm tra độ nhạy:** chỉ giữ dòng sản phẩm (mã 5 chữ số đầu) và giá > 0, loại phí vận chuyển, điều chỉnh và các dòng phụ. Kết quả: +2.33% (so với +2.56%). Kết luận không đổi.

## Bảng phân rã (Tháng 1–11, GBP)

| Nhóm | 2010 | 2011 | Thay đổi | Số khách |
|---|---:|---:|---:|---:|
| Khách 2010 rời đi (không mua 2011) | 1,103,566 | −11,867 | **−1,115,434** | 1,539 |
| Khách 2010 mua cả 2 năm | 6,353,963 | 6,016,059 | **−337,904** | 2,587 |
| Khách mới 2011 | 0 | 1,309,116 | **+1,309,116** | 1,494 |
| Mua trước 2010 nhưng không mua 2010 | −3,659 | 72,678 | +76,337 | 76 |
| Nhóm chỉ có hoàn trả trong 2010 | −102,542 | −1,379 | +101,163 | 81 |
| Không rõ Customer ID | 981,531 | 1,161,975 | +180,444 | — |
| **Tổng** | **8,332,860** | **8,546,582** | **+213,722** | |

Số khách có mua trong 2010 là 4,126 và trong 2011 là 4,157, gần như không đổi. Mức chi tiêu trung bình mỗi khách cũng gần như không đổi (1,807 so với 1,780 GBP). Điều thay đổi là **thành phần khách**: 37% khách 2010 không quay lại, và phần lớn doanh thu mới đến từ khách mới.

## Hình minh họa
- `chart1_bridge_khach_moi_vs_cu.png`: bridge doanh thu theo nhóm khách.
- `chart2_thi_truong_tang_giam.png`: thay đổi doanh thu theo thị trường.

## Lưu ý và hạn chế
1. **Đây là số liệu quan sát, không phải nhân quả.** Khách mới tăng không chứng minh việc chi tiêu cho marketing gây ra việc đó.
2. **22.8% số dòng không có Customer ID.** Nhóm này có +180,444 GBP và không được phân loại khách mới/cũ. Nhóm này được tính riêng và không đổi kết luận chính, nhưng không thể biết nó gồm khách mới hay khách cũ.
3. **"Rời đi" = không có doanh thu trong Tháng 1–11/2011.** Một số khách có thể quay lại trong tháng 12/2011 mà dữ liệu không ghi nhận đủ.
4. **Phân loại "Khách quay lại" bao gồm cả khách có ngày mua đầu tiên là tháng 12/2010** (chỉ mua trong 2010 vào tháng 12, nên không có doanh thu Tháng 1–11/2010). Nhóm này khoảng 76 khách và +76,337 GBP, nên ảnh hưởng nhỏ đến kết luận.
5. **Phân rã theo thị trường không tách khách mới/cũ.** Không kiểm tra được Ireland giảm do khách cũ rời đi hay do ít khách mới.
6. Một số thị trường nhỏ (Na Uy, Úc) có doanh thu 2010 rất thấp, nên % tăng rất lớn; nên dùng số tuyệt đối để xếp hạng.
7. Bộ dữ liệu có doanh thu âm ở một số dòng (điều chỉnh, hoàn trả, bad debt). Các dòng này được tính vào doanh thu thuần, phù hợp với định nghĩa "thuần".

## Tệp đầu ra
- `analysis.py`, `charts.py`: mã chạy lại được.
- `revenue_by_segment_year.csv`, `customer_bridge_2010_2011.csv`, `revenue_by_country_2010_2011.csv`: kết quả tính toán.
- `chart1_bridge_khach_moi_vs_cu.png`, `chart2_thi_truong_tang_giam.png`: biểu đồ.
- `story.md`: data story cho CEO.
