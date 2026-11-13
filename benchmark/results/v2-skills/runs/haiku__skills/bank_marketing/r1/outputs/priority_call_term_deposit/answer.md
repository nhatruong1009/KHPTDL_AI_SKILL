# Dự đoán khách đăng ký tiền gửi có kỳ hạn trước khi gọi

**Câu hỏi:** Trước khi gọi, mô hình có xếp hạng khách đăng ký tốt hơn một baseline đơn giản không, và yếu tố nào quan trọng nhất?

**Trả lời ngắn:** Trên validation, mô hình tốt hơn baseline rất nhiều (AUC 0,660 so với 0,484). Nhưng trên giai đoạn test cuối (15% dữ liệu theo thời gian), mô hình **kém** baseline đơn giản "chỉ dùng kết quả chiến dịch trước (poutcome)": AUC 0,578 so với 0,621, khoảng tin cậy chênh lệch −0,067 đến −0,022. Khi gọi 20% danh sách đầu, mô hình bắt được 25% người đăng ký, baseline bắt được 35%. Vì vậy **chưa có bằng chứng mô hình này đáng tin hơn baseline** khi áp dụng cho giai đoạn sau. Yếu tố mạnh nhất trong mô hình là các biến thời điểm và kinh tế (`nr.employed`, `pdays`, `month`, `poutcome`, `emp.var.rate`); đặc điểm khách hàng (nghề nghiệp, học vấn, vay nhà, vay tiêu dùng, nợ xấu) gần như không đóng góp.

## Bằng chứng

**Kết quả trên test (giai đoạn cuối, n = 6.179 khách, tỷ lệ đăng ký thực tế 38,5%):**

| Mô hình | AUC | PR-AUC | Tỷ lệ đăng ký trong 20% đầu | Bắt được (recall) 20% đầu |
|---|---|---|---|---|
| Ngẫu nhiên | 0,501 | 0,387 | 38,8% | 20,2% |
| Baseline: chỉ poutcome | **0,621** | **0,510** | **67,0%** | **34,9%** |
| Logistic đầy đủ (mô hình chọn) | 0,578 | 0,447 | 47,5% | 24,7% |

**Chọn mô hình trên validation (n = 6.178, tỷ lệ 10,7%):** Logistic có macro 0,660; Logistic không macro 0,658; GBM 0,58–0,61; baseline poutcome 0,484. Mô hình được chọn theo validation, không dùng test.

**Độ nhạy (cùng họ mô hình, cùng thời gian):**

| Kịch bản | AUC test |
|---|---|
| Chính (thông tin biết trước khi gọi, có macro) | 0,578 |
| Bỏ chỉ số kinh tế vĩ mô | 0,605 |
| Thêm `campaign` (không dùng được trước khi gọi) | 0,579 |
| Thêm `duration` (**rò rỉ**, chỉ biết sau cuộc gọi) | 0,652 |
| Thêm `age` + `marital` (nhạy cảm, chỉ đối chiếu) | 0,575 |

Ngay cả khi bỏ macro, AUC (0,605) vẫn dưới baseline (0,621). Thêm `duration` làm AUC tăng nhưng không dùng được trong dự đoán thực tế.

**Kiểm tra trên bank-full.csv** (45.211 dòng, có `balance`, không có macro): Logistic AUC 0,647 so với baseline 0,633, nhưng bắt được 27,6% người đăng ký trong 20% đầu so với 34,0% của baseline. Kết quả lẫn lộn, không ủng hộ mô hình.

**Yếu tố quan trọng nhất** (giảm AUC khi xáo trộn biến trên test):

| Biến | Giảm AUC | Nhóm |
|---|---|---|
| nr.employed | 0,085 | kinh tế / thời điểm |
| pdays (đã làm sạch) | 0,047 | lịch sử liên hệ |
| month | 0,042 | thời điểm gọi |
| poutcome | 0,030 | lịch sử chiến dịch trước |
| emp.var.rate | 0,026 | kinh tế |
| job | 0,005 | khách hàng |
| housing, loan, default, education | ≈ 0 | khách hàng |

`previous` và `euribor3m` có điểm âm (xáo trộn lại làm AUC tăng), dấu hiệu chúng không ổn định qua thời gian.

**Tỷ lệ đăng ký theo poutcome (toàn bộ dữ liệu):** khách thành công ở chiến dịch trước đăng ký 65%, thất bại 14%, chưa từng được gọi 9%.

**Trôi dạt thời gian:** tỷ lệ đăng ký tăng từ 3% (khối sớm nhất) lên 46% (khối cuối). Train chỉ có 5,6% đăng ký, test có 38,5%. Mô hình phải ngoại suy sang giai đoạn chưa từng thấy trong train.

**Kiểm tra theo nhóm tuổi (chỉ để audit, tuổi không phải đầu vào):** AUC trong test: <30 là 0,60; 30–39 là 0,59; 40–49 là 0,60; 50–59 là 0,57; 60+ là 0,47. Nhóm 60+ có tỷ lệ đăng ký thực tế cao nhất (46%), mô hình đánh dấu 28% nhóm này vào top 20%, nhưng không phân biệt được ai đăng ký trong nhóm này.

## Phương pháp

- **Dữ liệu:** `data/bank-additional/bank-additional-full.csv`, 41.188 dòng, 20 biến đầu vào và biến `y`. Tôi chọn bản này vì có đủ nhất thông tin (khách hàng, chiến dịch, chỉ số kinh tế). Giữ 12 dòng trùng lặp vì không có khóa khách hàng để xác định chúng là lỗi.
- **Kiểm tra thời điểm (timing audit):** loại `duration` (biết sau cuộc gọi) và `campaign` (đếm cả cuộc gọi hiện tại) khỏi mô hình chính. Giữ 5 chỉ số kinh tế vì được công bố tại thời điểm gọi, nhưng xem caveat bên dưới.
- **Chia dữ liệu theo thời gian:** dữ liệu được sắp theo ngày (theo tài liệu UCI). 70% đầu train, 15% kế validation (chọn mô hình), 15% cuối test (chạm một lần).
- **Thuộc tính nhạy cảm:** `age` và `marital` không dùng làm đầu vào.
- **Mô hình:** Logistic regression (one-hot + chuẩn hóa), so với GBM. Chọn theo AUC validation.
- **Chỉ số:** AUC, PR-AUC, tỷ lệ đăng ký và recall trong 20% danh sách đầu. Khoảng tin cậy bootstrap 500 lần cho chênh lệch AUC.
- **Mục tiêu/ràng buộc:** câu hỏi không nêu hạn mức số cuộc gọi hay mục tiêu recall. Tôi giả định đơn vị lập kế hoạch là **20% danh sách đầu**. Không có mục tiêu nào được đặt ra, nên không có gì để xác nhận đạt hay không.

## Giả định và hạn chế

- **Mô hình không vượt baseline trên giai đoạn test.** Đây là kết quả quan trọng nhất. Giai đoạn test có tỷ lệ đăng ký cao gấp ~7 lần giai đoạn train, nên kết quả phản ánh một sự thay đổi lớn, không chỉ là nhiễu.
- **Chỉ số kinh tế là biến thời gian.** `nr.employed` giảm đều theo thời gian và gần như định danh giai đoạn. Điểm số của nó có thể không áp dụng cho chiến dịch sắp tới trừ khi có giá trị mới nhất được công bố; khi dùng cho chiến dịch thực, cần dữ liệu kinh tế hiện tại hoặc dự báo của nó.
- **Dữ liệu từ 2008–2010**, một ngân hàng Bồ Đào Nha, gọi điện. Không chắc đại diện cho khách hiện tại.
- **Kết quả là liên quan, không phải nhân quả.** Ví dụ, poutcome liên quan đến đăng ký nhưng không chứng minh việc gọi lại sẽ tăng đăng ký.
- Một số ô `unknown` (nghề nghiệp, học vấn, vay) được giữ như một mức riêng.

## Gợi ý (không phải kết luận từ dữ liệu)

- Không nên dùng mô hình này làm quy tắc ưu tiên gọi điện. Trong thực tế, ưu tiên khách có kết quả thành công ở chiến dịch trước (poutcome = success) là cách đơn giản và vượt trội trên giai đoạn test.
- Nếu muốn mô hình, cần huấn luyện lại trên dữ liệu gần nhất và theo dõi tỷ lệ đăng ký thực tế theo tháng; không dùng chỉ số kinh tế làm biến chính khi không có dự báo đáng tin.

## Tệp đầu ra

- Mã: `analysis.py`. Nhật ký chạy: `run_log.txt`.
- Kết quả: `ket_qua_test.csv`, `chon_mo_hinh_validation.csv`, `top_k_test.csv`, `quan_trong_bien_permutation.csv`, `do_nhay_kich_ban.csv`, `kiem_tra_bank_full.csv`, `kiem_tra_nhom_tuoi.csv`, `chenh_lech_auc_bootstrap.csv`, `troi_dat_theo_thoi_gian.csv`, `ty_le_dang_ky_theo_bien.csv`, `diem_test.csv`.
- Biểu đồ: [đường tích lũy](bieu_do_1_duong_tich_luy.png), [yếu tố quan trọng](bieu_do_2_yeu_to_quan_trong.png), [độ nhạy](bieu_do_3_do_nhay.png), [poutcome](bieu_do_4_poutcome.png), [trôi dạt thời gian](bieu_do_5_troi_dat.png).
