# Trả lời: doanh thu 2011 so với 2010

**Phạm vi và cách tính:** Dữ liệu 01/12/2009 – 09/12/2011. So sánh công bằng là cùng kỳ tháng 1–11 của cả hai năm (2011 chưa đủ tháng 12). Doanh thu = số lượng × đơn giá, đã loại trùng lặp, phí/chi phí không phải hàng hóa (bưu phí, phí ngân hàng, điều chỉnh, v.v.) và dòng giá bằng 0; hoàn trả được trừ ròng. Đơn vị giả định là bảng Anh (£).

## 1. Thay đổi doanh thu
- Tháng 1–11/2010: **£8,38M**
- Tháng 1–11/2011: **£8,57M**
- Thay đổi: **+£194k (+2,3%)**
- Độ nhạy: so 1/1–9/12 cả hai năm cho +2,7%. So cả năm 2010 với 2011 (chưa đủ) sẽ cho −1,4%, là kết quả sai.

## 2. Đến từ khách mới hay khách cũ?
| Hạng mục | £ |
|---|---|
| Doanh thu 2010 | 8.379.289 |
| Mất khách (2010 có, 2011 không; 1.528 khách) | −1.049.480 |
| Khách cũ còn lại đổi chi tiêu (2.617 khách) | −379.506 |
| Khách quay lại sau khi nghỉ (62 khách) | +44.174 |
| Khách mới 2011 (1.505 khách) | +1.328.941 |
| Giao dịch không có mã khách | +250.011 |
| Doanh thu 2011 | 8.573.429 |

Khách mới bù đắp phần lớn mức giảm từ khách cũ (khách cũ có mã giảm ròng khoảng £1,38M). Phần "không có mã khách" (~14% doanh thu) không phân loại được.

## 3. Thị trường tăng/giảm nhiều nhất
- **Tăng mạnh nhất:** Australia +£107k (nhưng gần như toàn bộ là một khách hàng), Pháp +£61k, Tây Ban Nha +£24k, Nhật +£23k, Na Uy +£20k.
- **Giảm mạnh nhất:** Ailen (EIRE) −£81k (−25%, chỉ 3 khách), Đan Mạch −£27k (−62%), Thụy Điển −£16k (−34%), Hy Lạp −£10k (−72%).
- **Anh:** +£13k (+0,2%), đi ngang.

## 4. Khuyến nghị
Ưu tiên **giữ chân khách cũ**, vì mức mất khách (£1,05M) lớn hơn mức tăng của khách mới ròng trên phần có mã. Tìm khách mới là cần thiết để bù, nhưng không đủ nếu không giữ được khách. Chi tiết xem `story.md`.

## Đầu ra
- `story.md`: data story cho CEO
- `bieu_do_cau_noi_doanh_thu.png`: cầu nối 2010 → 2011
- `bieu_do_thi_truong.png`: thay đổi theo thị trường
- `cau_noi_doanh_thu_2010_2011.csv`, `doanh_thu_theo_thi_truong.csv`: số liệu
