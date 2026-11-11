# Dự đoán khách hàng đăng ký tiền gửi có kỳ hạn (trước khi gọi)

**Dữ liệu:** `bank-additional-full.csv` (41.188 khách, 20 biến, tỷ lệ đăng ký 11,3%) – phiên bản đầy đủ nhất. Có 12 dòng trùng, giữ nguyên.
**Quyết định chính:** loại `duration` (thời lượng cuộc gọi, chỉ biết sau khi gọi → rò rỉ thông tin). Các biến còn lại đều biết trước cuộc gọi, riêng `campaign` bao gồm cả lần gọi hiện tại (loại bỏ nó hầu như không đổi kết quả).
**Mô hình:** gradient boosting (HistGradientBoosting) và hồi quy logistic.

## Kết quả (CV phân tầng ngẫu nhiên 5 fold, toàn bộ dữ liệu)
| Mô hình | AUC | PR-AUC | Lift top 10% | Lift top 20% |
|---|---|---|---|---|
| Ngẫu nhiên / đa số | 0,50 | 0,11 | 1,0 | 1,0 |
| Quy tắc đơn giản (kết quả chiến dịch trước = success / từng được liên hệ) | 0,60 | 0,23 | 2,3 | 1,3 |
| Baseline mạnh: chỉ dùng euribor3m | 0,74 | 0,34 | 4,1 | 2,7 |
| Hồi quy logistic | 0,79 | 0,45 | 4,4 | 3,1 |
| **Gradient boosting** | **0,80** | **0,47** | **4,6** | **3,2** |

- Gọi 10% khách có điểm cao nhất: tỷ lệ đăng ký **51%** (gấp 4,6 lần trung bình), bắt được **46%** số người đăng ký; top 20% bắt được 64%; top 30% bắt được 72%. Nhóm điểm thấp nhất chỉ 2,9%.
- Hơn baseline “đa số/ngẫu nhiên”: AUC +0,30. Hơn quy tắc đơn giản: +0,20 AUC. Hơn baseline chỉ-euribor: chỉ +0,06 AUC (+0,13 PR-AUC) – phần lớn sức mạnh đến từ bối cảnh kinh tế/thời điểm, không phải từ hồ sơ khách.

## Yếu tố quan trọng nhất (permutation importance, giảm AUC trên tập giữ lại 25%)
1. **Bối cảnh kinh tế**: `nr.employed` (0,043), `emp.var.rate`, `euribor3m` – lãi suất thấp (euribor ≤1%) → 46% đăng ký; >4% → 4,8%.
2. **Tháng liên hệ** `month` (0,035): tháng 3/9/10/12 đạt 44–51%, tháng 5 chỉ 6,4%.
3. **Kênh liên hệ** `contact` (0,021): di động 14,7% so với điện thoại bàn 5,2%.
4. Yếu hơn: `pdays`, `campaign`, `day_of_week`, `job`, `poutcome`. Về mặt mô tả: kết quả chiến dịch trước “success” → 65% đăng ký (tuy chỉ 1.373 khách); sinh viên 31%, người nghỉ hưu 25%, tuổi >60 45,5%, ≤25 tuổi 21%. Học vấn, hôn nhân, khoản vay gần như không đóng góp.

## Cảnh báo quan trọng – độ tin cậy khi dùng cho chiến dịch *sắp tới*
Dữ liệu được sắp xếp theo thời gian (5/2008–11/2010) và tỷ lệ đăng ký thay đổi rất mạnh theo thời kỳ (5,6% giai đoạn đầu → 25–31% giai đoạn cuối). Khi kiểm tra đúng kiểu “huấn luyện trên quá khứ, dự đoán tương lai”:
- Train 70% đầu → test 30% cuối: AUC chỉ **0,66** (lift top 10% ≈ 1,8); baseline chỉ-euribor lại đạt 0,71, tốt hơn mô hình.
- Các khối thời gian sớm hơn: AUC 0,46–0,51 (không tốt hơn ngẫu nhiên).
Nghĩa là con số 0,80 ở CV ngẫu nhiên là **lạc quan**: nó học cả “giai đoạn nào thì tỷ lệ đăng ký cao” từ các khách cùng thời điểm. Với chiến dịch mới, hãy kỳ vọng mức giữa 0,66 và 0,80; mô hình xếp hạng khách *trong cùng một giai đoạn* tốt hơn là dự báo mức đăng ký tuyệt đối (mô hình huấn luyện ở giai đoạn tỷ lệ thấp dự báo thấp hơn thực tế rất nhiều ở giai đoạn sau). Nên huấn luyện lại bằng dữ liệu gần nhất và đo lại bằng một đợt gọi thử có nhóm đối chứng.

Các phép đo khác: bản tham chiếu **có** `duration` đạt AUC 0,95 (CV) – không thể dùng thực tế. Dữ liệu chỉ là một quan sát từ một quốc gia ~10 triệu dân; “unknown” được giữ làm một nhóm riêng.

Tệp: `outputs/model.py`, `outputs/model2.py` (mã), `importance_random_holdout.csv`, `decile_gain_cv.csv`, `chart.png`.
