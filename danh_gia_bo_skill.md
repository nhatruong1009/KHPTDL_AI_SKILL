# Đánh giá bộ skill phân tích dữ liệu (KHPTDL_AI_SKILL)

Bộ được đánh giá là `/analyze` (orchestrator) cùng 15 sub-skill trong `KHPTDL_AI_SKILL/.claude/skills/`.

## 1. Đã đo những gì

| Lượt | Nội dung | Số lượt chạy |
|---|---|---|
| `ab-vi` | 7 task dữ liệu công khai (bán lẻ, giáo dục, năng lượng, y tế, leo núi, rượu vang, ngân hàng). So sánh có skill và không skill trên Haiku và Sonnet, mỗi cấu hình chạy 1 lần. | 28 |
| `full-1` | 7 task như trên, chỉ chạy bản có skill. | 14 |
| `oulad-1` | Dữ liệu đã chuẩn bị của project OULAD early warning (`P3/data/processed`), hỏi trực tiếp 5 câu AQ1–AQ5. So sánh có skill và không skill, mỗi cấu hình chạy 2 lần. | 8 |

Giám khảo là Claude Opus 5.5. Giám khảo được xem ground truth do reference solution tính sẵn, còn agent thì không. Điểm overall = 0.6 × accuracy (tỉ lệ tiêu chí trong checklist đạt) + 0.4 × quality (rubric 1–5), sau đó trừ điểm phạt nếu có.

Báo cáo chi tiết nằm trong `KHPTDL_AI_SKILL/benchmark/results/<run>/report.md`.

## 2. Kết quả chính

### ab-vi (7 task)
| Cấu hình | Overall | Accuracy | Quality | Chi phí/task |
|---|---|---|---|---|
| Haiku, không skill | 76.0 | 78.6 | 72.1 | $0.031 |
| Haiku, có skill | **87.5** | **91.4** | **81.6** | $0.034 |
| Sonnet, không skill | 95.1 | 100.0 | 87.8 | $0.291 |
| Sonnet, có skill | 94.4 | 97.6 | 89.6 | $0.371 |

### oulad-1 (task OULAD, trung bình 2 lần chạy)
| Cấu hình | Overall (lần 1 / lần 2) | Accuracy | Chi phí/lượt |
|---|---|---|---|
| Haiku, không skill | 53.0 (56 / 50) | 50.0 | $0.089 |
| Haiku, có skill | **66.2** (69 / 63.5) | **68.8** | $0.208 |
| Sonnet, không skill | 62.5 (61.5 / 63.5) | 62.5 | $0.427 |
| Sonnet, có skill | 66.2 (61.5 / 71) | 68.8 | $0.810 |

## 3. Phát hiện quan trọng nhất: các sub-skill gần như không được dùng

Trong 32 lượt chạy có skill (ab-vi, full-1, oulad-1), Skill tool chỉ được gọi **1 lần** (`data-eda`). Không lượt nào đọc file `SKILL.md` của sub-skill. Chỉ số `skill_hit_pct` trong report gần như bằng 0 là phản ánh đúng thực tế này, không phải lỗi đo.

Nguyên nhân: `/analyze` chỉ nhắc tên skill (ví dụ "dùng `/data-predict`"), và model hiểu đó là gợi ý chứ không thực sự nạp skill. Vì vậy:

- **Mọi mức tăng đo được đều đến từ khoảng 56 dòng của `analyze/SKILL.md`**, tức một quy trình dạng checklist gồm EDA, kiểm tra tính liên quan, lập kế hoạch, phân tích, vẽ chart, viết câu trả lời và QA.
- **15 sub-skill (khoảng 500 dòng) chưa được kiểm chứng.** Các quy tắc chỉ nằm trong sub-skill thì không đến được model. Ví dụ, `data-predict` có dặn "chỉ dùng feature có trước thời điểm dự báo", nhưng cả 8/8 lượt OULAD vẫn đưa `tma1_score` vào mô hình chính mà không kiểm tra thời điểm biến này có sẵn.

## 4. Đánh giá

| Tiêu chí | Đánh giá |
|---|---|
| Với model nhỏ (Haiku) | **Tốt, nhất quán.** Tăng +11.5 điểm (ab-vi) và +13.2 điểm (oulad-1). Có skill, Haiku đạt ngang hoặc gần Sonnet với chi phí bằng khoảng 1/4 đến 1/10. |
| Với model vừa (Sonnet) | **Chưa thấy lợi ích rõ.** Thay đổi −0.7 (ab-vi) và +3.75 (oulad-1), cả hai đều nằm trong biên nhiễu. |
| Chi phí | **Khó lường.** Ở ab-vi gần như không đổi với Haiku và tăng khoảng 27% với Sonnet. Ở OULAD tăng khoảng gấp đôi cho cả hai model và chậm thêm 80–140 giây mỗi lượt. |
| Điểm mạnh | Câu trả lời có cấu trúc. Biết từ chối khi dữ liệu không trả lời được câu hỏi (task wine_quality đạt 97–100 điểm). Có nhiều chart hơn. Dùng effect size và hiệu chỉnh đa kiểm định. Nói thẳng khi chưa đạt mục tiêu (ví dụ recall dưới 70% ở OULAD). |
| Điểm yếu lặp lại | (1) Không xét feature có sẵn tại thời điểm dự báo hay không, gây rò rỉ dữ liệu hoặc lệch phân phối. (2) Tiêu đề chart chỉ mô tả, không nêu thông điệp. (3) Có làm kiểm tra độ nhạy nhưng không đưa kết quả vào kết luận chính (ví dụ retail_uk, himalaya). |

**Kết luận:** orchestrator `/analyze` là phần đang tạo ra giá trị, và nên giữ nó cho các model nhỏ. Bộ sub-skill hiện chưa phát huy tác dụng vì không được nạp. Cần sửa orchestrator để sub-skill thực sự được gọi, rồi đo lại để biết chúng có giá trị hay không.

## 5. Giới hạn của phép đo
- Mỗi cấu hình chỉ chạy 1–2 lần, nên chênh lệch dưới khoảng 5–8 điểm có thể chỉ là nhiễu.
- Giám khảo là một LLM. Mỗi nhận định đều kèm bằng chứng trích dẫn trong `grade.json`.
- Checklist của OULAD được viết sau khi đã đọc plan và kết quả P4 của project, nên phần nào đo "agent làm giống cách của nhóm N05 đến đâu".
  - Riêng lựa chọn dùng `tma1_score` làm trượt cùng lúc 3/8 tiêu chí.
  - Reference tự tính lại khớp P4 về PR-AUC (0.665 so với 0.662). Recall thì nhạy với tiền xử lý: 0.62 nếu không lấy log1p, 0.69 nếu có.

## 6. Cải thiện đã thực hiện
1. **`analyze/SKILL.md`:**
   - Mỗi bước giờ bắt buộc phải nạp sub-skill tương ứng bằng Skill tool trước khi làm.
   - Thêm mục "Non-negotiables" chép thẳng các quy tắc then chốt vào orchestrator, phòng khi sub-skill vẫn không được nạp: kiểm tra thời điểm có của từng feature, giữ đúng cách chia dữ liệu có sẵn, biến nhạy cảm, ràng buộc theo nhóm, tiêu đề chart nêu thông điệp, và đưa kết quả kiểm tra độ nhạy vào kết luận chính.
2. **`data-predict/SKILL.md`:**
   - Thêm bước kiểm tra thời điểm có dữ liệu của từng feature. Feature nào không rõ thời điểm thì không đưa vào mô hình chính, chỉ dùng trong phân tích độ nhạy.
   - Ưu tiên dùng cột split hoặc cách chia theo thời gian có sẵn trong dữ liệu.
   - Ngưỡng quyết định phải chọn trên tập validation.
   - Kiểm tra drift của các feature quan trọng.
   - Không dùng thuộc tính nhạy cảm làm predictor.
3. **`answer-qa/SKILL.md`:** thêm các bước kiểm tra kiểm toán feature, kết quả độ nhạy có được đưa vào kết luận chính chưa, và đọc lại tiêu đề từng chart.

Các quy tắc này được viết tổng quát, không nhắc tên cột hay dữ liệu cụ thể nào của benchmark, để tránh "học tủ" theo đề.

## 7. Kết quả sau cải thiện (lượt `v2-skills`)
Bản skill mới chạy trên 8 task × 2 model × 2 lần, tổng 32 lượt. Kết quả được so với:
- **không skill:** 7 task lấy từ ab-vi (1 lần chạy), task OULAD lấy từ oulad-1 (2 lần chạy);
- **skill cũ:** cùng nguồn như trên.

Report chi tiết nằm ở `benchmark/results/v2-skills/report.md`.

**Sub-skill giờ đã được nạp.**

| | Skill cũ | Skill mới |
|---|---|---|
| Lượt có nạp sub-skill | 1/32 | 32/32 |
| Tỉ lệ skill kỳ vọng được dùng (Haiku) | ~0% | 46% |
| Tỉ lệ skill kỳ vọng được dùng (Sonnet) | ~0% | 77% |

**Điểm overall trung bình trên 8 task:**

| Model | Không skill | Skill cũ | Skill mới | Chi phí/task (không skill → skill mới) |
|---|---|---|---|---|
| Haiku | 73.1 | 84.8 | **85.1** | $0.044 → $0.052 |
| Sonnet | 91.0 | 90.9 | **91.7** | $0.321 → $0.505 (+57%) |

**Chênh lệch theo task:**

| Task | Haiku (không skill / cũ / mới) | Sonnet (không skill / cũ / mới) | Nhận xét |
|---|---|---|---|
| oulad_early_warning | 53.0 / 66.2 / **80.5** | 62.5 / 66.2 / **94.2** | Lỗi `tma1_score` đã được sửa: feature không rõ thời điểm có chỉ còn dùng trong phân tích độ nhạy. |
| himalaya | 47.3 / 45.7 / 60.2 | 90.0 / 95.0 / 94.2 | Haiku tốt hơn nhưng dao động lớn (74.7 và 45.7). |
| bank_marketing | 54.0 / 94.0 / 83.0 | 98.0 / 88.0 / **77.0** | Sonnet loại các chỉ số vĩ mô khỏi mô hình chính chỉ vì chúng "trôi theo thời gian", dù chúng có sẵn tại thời điểm dự báo. Đây là tác dụng phụ của quy tắc drift mới. Ngoài ra, giá trị 'unknown' không được xử lý tường minh. |
| student_perf | 62.0 / 92.0 / 77.0 | 94.0 / 96.0 / **80.0** | Kết luận theo từng môn chưa nói rõ môn nào rõ nhất, và chưa nêu Toán yếu đi khi giữ G3=0. |
| Các task còn lại | Gần như không đổi (±5) | Gần như không đổi | |

**Nhận định:**
- Bản sửa đạt mục tiêu chính: sub-skill được dùng, và lỗi rò rỉ dữ liệu theo thời gian đã được khắc phục rõ rệt (OULAD tăng +14 với Haiku và +28 với Sonnet so với skill cũ).
- Điểm trung bình gần như không đổi vì có hai task bị giảm. Ít nhất một trong hai (bank_marketing) là do quy tắc mới quá chặt: drift giữa train và test **không phải** lý do để loại một feature có sẵn tại thời điểm dự báo.
- Với Haiku, skill vẫn là lựa chọn tốt nhất: khoảng +12 điểm so với không skill, gần như không tốn thêm tiền. Với Sonnet, skill chỉ đáng dùng cho các bài dự báo có bẫy về thời gian; ở các task khác điểm ngang nhau mà chi phí tăng 57%.
- Các con số "không skill" và "skill cũ" của 7 task công khai chỉ có 1 lần chạy, nên chênh lệch dưới khoảng 10 điểm ở từng task vẫn có thể là nhiễu.

## 8. Bước tiếp theo đề xuất
1. Sửa `data-predict`: drift chỉ là lý do để báo cáo và kiểm tra độ nhạy, không phải lý do để loại một feature có sẵn tại thời điểm dự báo. Đồng thời yêu cầu nêu rõ cách xử lý các giá trị đặc biệt như 'unknown' hay 999.
2. Tăng tỉ lệ nạp skill của Haiku (hiện 46%): Haiku hay bỏ qua bước nạp skill phân tích (ví dụ `data-predict`) sau khi đã nạp `data-eda`.
3. Chạy lại bản không skill cho 7 task với 2 lần chạy để mẫu so sánh cân bằng hơn.
