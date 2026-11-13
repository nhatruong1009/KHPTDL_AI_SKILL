# Ưu tiên khách hàng gọi trong chiến dịch tiền gửi có kỳ hạn

## Kết luận
- **Với dữ liệu hiện có, chưa thể khẳng định mô hình tốt hơn baseline đơn giản khi dự báo giai đoạn sau.** Khi huấn luyện trên giai đoạn trước và kiểm tra trên giai đoạn sau (cách kiểm tra đúng với việc dùng cho chiến dịch sắp tới), mô hình không thắng luật đơn giản "ưu tiên khách có kết quả chiến dịch trước là success, rồi ưu tiên lãi suất euribor thấp":
  - Test (20% cuối theo thời gian), mô hình chính LogReg: ROC-AUC **0,49**, PR-AUC 0,37.
  - Sau khi huấn luyện lại trên train+valid: ROC-AUC 0,64 (mô hình tốt nhất 0,69 khi bỏ biến vĩ mô).
  - Baseline luật đơn giản: ROC-AUC **0,745**, lift@20% = 2,05.
  - Gọi ngẫu nhiên: ROC-AUC 0,50, lift = 1.
- **Nếu kiểm tra trong cùng giai đoạn** (CV theo khối thời gian liên tục, 5 fold) thì mô hình có giá trị: HistGB ROC-AUC **0,79**, lift@20% = **3,1** (gọi 20% khách điểm cao nhất bắt được 62% người đăng ký, tỷ lệ đăng ký 35% so với 11,3% trung bình), baseline luật 0,75 / 2,8. Mô hình hơn baseline +0,04 AUC và +0,3 lift, và hơn gọi ngẫu nhiên 3,1 lần. Đây là mức tốt hơn trong điều kiện thuận lợi, không phải bằng chứng cho dự báo tương lai.
- **Yếu tố quan trọng nhất** (CV theo khối, permutation importance, giảm ROC-AUC): `emp.var.rate` (0,049), `nr.employed` (0,045), `euribor3m` (0,019), `cons.price.idx` (0,012), `contact` (0,011; điện thoại di động tốt hơn), rồi `cons.conf.idx`, `poutcome`, `pdays`. Các biến hồ sơ khách (nghề, học vấn, hôn nhân, vay nợ...) gần như không đóng góp (≈0). Tức là mô hình chủ yếu học "thời điểm kinh tế", không phải "loại khách hàng".

## Vì sao kết quả không ổn định giữa các giai đoạn
Dữ liệu dùng: `bank-additional-full.csv` (41.188 dòng, 20 biến, sắp theo ngày 05/2008–11/2010, có biến vĩ mô; đây là bản đầy đủ nhất về biến và có thứ tự thời gian. `bank-full.csv` nhiều dòng hơn nhưng không có năm, không có biến vĩ mô). Sau khi bỏ 12 dòng trùng còn 41.176.

| Tập | Dòng | Tỷ lệ đăng ký | euribor TB | Tỷ lệ poutcome=success |
|---|---|---|---|---|
| train (60% đầu) | 24.705 | 4,8% | 4,90 | 0,02% |
| valid | 8.235 | 11,1% | 2,36 | 2,0% |
| test (20% cuối) | 8.236 | 30,8% | 1,03 | 14,6% |

Chiến dịch thay đổi hẳn: 2008 gọi đại trà, lãi suất cao, hầu như không có khách từng được liên hệ; 2009–2010 gọi ít hơn, tập trung, lãi suất thấp, tỷ lệ đăng ký 30–57%. Mô hình học trên 2008 gần như chưa thấy các điều kiện của test, nên các biến vĩ mô (thực chất là "đồng hồ thời gian") không ngoại suy được và còn đảo chiều xếp hạng (AUC valid 0,41–0,47 dưới mức ngẫu nhiên).

## Kiểm toán thời điểm biến (dự đoán trước cuộc gọi)
| Biến | Biết khi nào | Quyết định |
|---|---|---|
| job, marital, education, default, housing, loan | trước cuộc gọi (hồ sơ) | giữ |
| contact, day_of_week | kế hoạch cuộc gọi | giữ |
| previous, pdays, poutcome | từ chiến dịch trước | giữ |
| 5 biến vĩ mô | công bố theo ngày/quý, có trước cuộc gọi | giữ (nhưng xem cảnh báo drift; có chạy bản bỏ) |
| **duration** | chỉ biết sau cuộc gọi (tài liệu dữ liệu cũng khuyến cáo bỏ) | **loại** |
| **campaign** | đếm cả lần gọi hiện tại/cuối, không xác minh được lúc gọi | loại; chỉ chạy nhạy cảm (không cải thiện: AUC test 0,51) |
| month | lịch chiến dịch, không tổng quát hoá qua thời gian | loại |
| age | thuộc tính nhạy cảm | không dùng để dự đoán; chỉ kiểm toán lỗi |

Kiểm toán theo nhóm tuổi (test, top 20% theo điểm): tỷ lệ được chọn 17–24% ở mọi nhóm; nhóm 60+ có tỷ lệ đăng ký thật cao nhất (46%) và precision 50%. AUC từng nhóm 0,47–0,52, nhất quán với việc mô hình kém ở test nói chung, không phải sai lệch riêng một nhóm.

## Phương pháp
- Mục tiêu: `y` (yes = đăng ký, 11,3% toàn bộ). Một dòng = một cuộc gọi/khách (giả định mỗi khách một dòng, không có ID để kiểm tra).
- Split theo thời gian 60/20/20 (không xáo trộn); chọn mô hình bằng PR-AUC trên valid; test chạm một lần. Pipeline (one-hot + chuẩn hoá) fit trên train. Mô hình: Dummy (ngẫu nhiên), luật đơn giản, LogReg cân bằng lớp, HistGradientBoosting.
- Kiểm tra độ nhạy: (A) huấn luyện lại trên train+valid; (B) CV theo khối 300 dòng liên tục. Bootstrap cho chênh ROC-AUC mô hình chính so với baseline luật trên test: −0,26 (KTC 95% −0,28 đến −0,24), tức baseline tốt hơn rõ rệt.
- Không có ngưỡng/công suất gọi được nêu trong câu hỏi, nên báo cáo precision/recall/lift ở top 10/20/30% (xem `metrics.csv`).

## Khuyến nghị và hạn chế
- Dùng tạm luật đơn giản (ưu tiên khách từng đăng ký ở chiến dịch trước, `poutcome = success`, và gọi khi lãi suất thấp, ưu tiên điện thoại di động) cho chiến dịch sắp tới; nó vượt gọi ngẫu nhiên ~2 lần ở lift@20%.
- Mô hình chỉ nên dùng sau khi huấn luyện lại bằng dữ liệu chiến dịch gần nhất, rồi kiểm tra tiếp trên đợt gọi kế tiếp.
- Hạn chế: dữ liệu chỉ ở một nước, 2008–2010 (khủng hoảng tài chính); tỷ lệ test 30,8% không đại diện cho chiến dịch bình thường; dữ liệu quan sát nên đây là liên quan chứ không phải nhân quả; test gồm một giai đoạn duy nhất; biến vĩ mô cộng tuyến (quan trọng riêng lẻ không đáng tin tuyệt đối); `pdays_val` và `pdays_contacted` cộng tuyến, nên đọc chung là "đã liên hệ trước đó".

## Tệp
`model.py`, `model_sensitivity.py`, `ve_bieu_do.py`; `metrics.csv`, `metrics_sensitivity.csv`, `feature_importance_blockCV.csv`, `decile_blockCV.csv`, `split_drift.csv`, `theo_thang.csv`, `audit_nhom_tuoi.csv`; `so_sanh_kiem_tra.png`, `feature_importance.png`. (`feature_importance.csv` và `decile_test.csv` là của mô hình LogReg trên test, không dùng cho kết luận.)
