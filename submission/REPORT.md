# Báo cáo nhóm <<XX>>

## 1. Số liệu luyện tập
- F1 theo seed (rule / cross_check / overall): <<seed: ... / ... / ...>>
- Số ứng viên trên lô sạch (`--no-faults`): <<...>>; hàng đợi trên seed luyện tập: <<... ảnh>>
- Ngưỡng đã chọn và cách chọn (không dùng `_private`): <<...>>

### Kiểm thử File & Detection — Nguyễn Văn Nhất (TV1)

Validator kiểm năm lỗi `missing_image`, `wrong_hash`, `invalid_class`, `bbox_out_of_bounds` và `duplicate_box`. Cả 16 ca giả lập đều cho kết quả dự kiến. Bảng dưới lấy số phát hiện từ `rules.json` của từng lô.

| Lô | Số ảnh trong manifest | Phát hiện File & Detection |
|---|---:|---|
| Seed nhóm 999 | 250 | 6 — 2 sai hash, 2 class ngoài phạm vi, 1 box tràn mép, 1 box trùng |
| Seed bổ sung 11 | 250 | 7 — 1 thiếu ảnh, 2 sai hash, 2 box tràn mép, 2 box trùng |
| Lô sạch | 50 | 0 |

Các số trên là đầu ra của năm luật. F1 chung sẽ được ghi sau khi nhóm tích hợp và chấm validator đầy đủ. Chi tiết cách dùng AI và kiểm lại nằm trong mục Prompt 4 của [prompts.md](prompts.md).

## 2. Vì sao báo hết ứng viên làm F1 giảm?
<<Trả lời bằng số của nhóm.>>

## 3. Quyết định và lineage
<<QC v1 a/b, kết luận, vì sao R-021 phải xem lại hoặc train lại.>>

## 4. Hash chứng minh gì, không chứng minh gì?
<<>>

## 5. Truy vết
<<Tiêu chí tầng a/b, vì sao lấy guideline theo job.>>

## 6. Bug hoặc điểm chưa rõ trong lab (nếu có)
<<>>
