# Câu chuyện dữ liệu: Cảnh báo sớm ở ngày 28

**Thông điệp chính:** Chỉ sau 4 tuần, hành vi học tập đã tách người hoàn thành và không hoàn thành, nhưng nguồn lực 200 người/module-kỳ chỉ chạm được khoảng một phần tư số sinh viên cần hỗ trợ, và mục tiêu bắt 70% là chưa thực tế.

1. **Bối cảnh.** 13.020 sinh viên BBB/FFF còn theo học ở ngày 28; 43% cuối cùng Fail hoặc Withdrawn.
2. **Tín hiệu có sớm.** Ngay tuần 1, trung vị click của Pass là 59 so với 20 của Fail; 27% sinh viên Fail không click nào, so với 12% của Pass (biểu đồ `q1_tuong_tac_theo_nhom.png`). 26/30 chỉ báo khác biệt rõ; mạnh nhất là số ngày vào học và nộp TMA1 đúng hạn (`q2_chi_bao_khac_biet.png`).
3. **Căng thẳng.** Dự báo chỉ ở mức vừa (AUC 0,705 trên kỳ 2014J). Gắn cờ ~50% sinh viên mới bắt được ~68% người không hoàn thành, và chỉ một nửa số cờ là đúng (`q3_hieu_nang_mo_hinh.png`).
4. **Hành động.** Với 200 người mỗi module-kỳ, ưu tiên theo điểm rủi ro (hoặc quy tắc đơn giản "chưa nộp TMA1 rồi ít click"): trúng 127/200 ở BBB và 180/200 ở FFF, gấp 1,8–2,3 lần ngẫu nhiên, nhưng chỉ phủ 20–24% người không hoàn thành (`q4_danh_sach_uu_tien_k200.png`). Cần hoặc tăng nhân lực (~840–1.050 người/module-kỳ cho mục tiêu 70%) hoặc hạ kỳ vọng. Mỗi sinh viên kèm 2–3 câu lý do cho cố vấn (`q5_priority_list_with_explanations.csv`).
5. **Lưu ý.** Chỉ một kỳ test; tỷ lệ 14% hỗ trợ thành công là giả định; mối liên quan không phải nhân quả.
