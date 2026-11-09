# Đội hình (deck) ổn định nhất - dữ liệu pokemon/

**Câu hỏi:** Xây dựng đội hình ổn định nhất.
**Cách hiểu:** "ổn định" = thắng nhiều hơn 50% một cách đáng tin (khoảng tin cậy dưới > 50%), với nhiều người chơi khác nhau, và không đổi theo thời gian. Dữ liệu chỉ cho phép **chọn trong các bộ bài (60 lá) đã thực sự được thi đấu**, không tạo ra bộ bài mới chưa từng chạy.

## Trả lời
**Chọn bộ bài D02 (lõi Dragapult ex: Dreepy / Drakloak / Dragapult ex).**
- Thắng **58.4%** trong 449 ván (khoảng tin cậy 95%: 53.7%-62.8%) - bộ bài lớn duy nhất có cận dưới trên 50%.
- Ổn định theo người chơi: 5 người dùng; 3 người có nhiều ván đều 55-58% (Darren Sheehan 55.2%/181, Dipam Chakraborty 56.8%/169, Deep Deck 58.3%/48); tyr1218 77.6%/49.
- Ổn định theo thời gian: chia 3 phần theo thứ tự trận, tỷ lệ thắng 57.3% / 60.4% / 57.3%.
- Danh sách 60 lá: `decklists.json` (khóa "D02"). Lõi: 4 Dreepy, 4 Drakloak, 2 Dragapult ex, 2 Blaziken ex, 4 Buddy-Buddy Poffin, 4 Ultra Ball, 4 Lillie's Determination, 3 Boss's Orders, 3 Pokémon Pad (xem file để đủ 60 lá).

**Điểm yếu cần biết (D02):** thắng 72.9% khi gặp D01 (Beldum/Metang, bộ bài phổ biến nhất, chiếm 29.6% đối thủ của D02) và ép tỷ lệ chung lên; còn gặp D04 (Dreepy/Drakloak khác) chỉ 44.7%/94 ván, và gặp D05 chỉ 25.0%/28 ván. Nếu đối thủ không phải D01, lợi thế mỏng hơn nhiều.

**Các lựa chọn khác:** D01 (914 ván) là bộ bài được kiểm chứng nhiều nhất nhưng chỉ 50.4% - ổn định nhưng không mạnh. D14 (62.8%) và D08 (56.9%) cao nhưng chỉ có 78 và 116 ván, 1-2 người chơi nên chưa đáng tin bằng D02.

## Biểu đồ
- [deck_winrate.png](deck_winrate.png) - tỷ lệ thắng và khoảng tin cậy của 18 bộ bài có >= 30 ván

## Cách làm
- 1,670 trận BO3 (game "cabt" - Limited Card Battle), 3,332 lượt (hai phía mỗi trận; bỏ 4 trận không có kết quả). Bộ bài đọc từ lúc bắt đầu mỗi file, gom theo đúng danh sách 60 lá (32 danh sách khác nhau).
- Tỷ lệ thắng tính theo từng trận (reward +1 / -1), khoảng tin cậy Wilson. Ổn định: tách theo người chơi, theo đối thủ (>= 10 ván), theo 3 khoảng thời gian.
- Code: [extract.py](extract.py), [analysis.py](analysis.py); bảng: `deck_stability.csv`, `deck_games.csv`, `decklists.json`.

## Lưu ý
- **Tỷ lệ thắng của bộ bài lẫn với trình độ bot/người chơi**: mỗi người dùng gần như chỉ một bộ bài, nên không tách riêng được "bộ bài tốt" và "người chơi giỏi". Đây là mối liên hệ, chưa chứng minh bộ bài mạnh hơn.
- Các trận được ghép giữa những người có điểm gần nhau (~1560-1580) nên mọi tỷ lệ thắng gần 50% là bình thường. Chênh lệch chung chỉ 3-8 điểm phần trăm.
- Chưa phân tích kỹ năng đánh bài trong ván (từng lượt, lá bài trên tay); chỉ dùng bộ bài và kết quả.
- Tỷ lệ thắng của D02 phụ thuộc vào mức độ phổ biến của D01 trong lượng đối thủ hiện tại; nếu "meta" đổi, kết quả có thể đổi.
