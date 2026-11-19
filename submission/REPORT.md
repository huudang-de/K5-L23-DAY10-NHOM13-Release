# Báo cáo nhóm 13

## 1. Số liệu luyện tập
- F1 theo seed (rule / cross_check / overall): `seed 999: 1.0 / 0.7 / 0.9` (22 lỗi trong `errors.json`)
- Số ứng viên trên lô sạch (`--no-faults`): **0 ứng viên / 50 ảnh**; hàng đợi trên seed luyện tập (seed 999): **18 ảnh / 250 ảnh** (chia 8 phần cho 8 thành viên: 3, 3, 2, 2, 2, 2, 2, 2 ảnh/người).
- Ngưỡng đã chọn và cách chọn (không dùng `_private`):
  - Áp dụng thuật toán **Greedy Bipartite Matching** theo IoU giảm dần. Khớp các cặp cùng tên lớp có $\text{IoU} \ge 0.70$ trước để loại trừ toàn bộ các vật thể được gán nhãn bình thường, tránh so nhầm với các vật thể khác đứng gần.
  - Sau khi ghép cặp bình thường, các đối tượng chưa ghép được kiểm tra để đưa vào hàng đợi ứng viên:
    + `class_swap` / `category_swap`: Box YOLO và Segment Panoptic chưa ghép đè lên nhau với $\text{IoU} \ge 0.45$, diện tích box $\ge 0.5\%$ diện tích ảnh.
    + `bbox_drift`: Cùng tên lớp nhưng không đạt ngưỡng bình thường ($0.15 \le \text{IoU} < 0.70$), diện tích box $\ge 0.5\%$ diện tích ảnh.
    + `instance_merge`: Một segment panoptic bao phủ $\ge 2$ box detection cùng lớp ($\text{IoU} > 0.20$ giữa box và segment) và tổng số segment của lớp đó trong ảnh ít hơn số box detection.
    + `missing_box`: Segment thing có diện tích $\ge 1500$ pixel nhưng không có box detection nào bao phủ.

### Kiểm thử File & Detection — Nguyễn Văn Nhất (TV1)

Validator kiểm năm lỗi `missing_image`, `wrong_hash`, `invalid_class`, `bbox_out_of_bounds` và `duplicate_box`. Cả 16 ca giả lập đều cho kết quả dự kiến. Bảng dưới lấy số phát hiện từ `rules.json` của từng lô.

| Lô | Số ảnh trong manifest | Phát hiện File & Detection |
|---|---:|---|
| Seed nhóm 999 | 250 | 6 — 2 sai hash, 2 class ngoài phạm vi, 1 box tràn mép, 1 box trùng |
| Seed bổ sung 11 | 250 | 7 — 1 thiếu ảnh, 2 sai hash, 2 box tràn mép, 2 box trùng |
| Lô sạch | 50 | 0 |

Các số trên là đầu ra của năm luật; F1 tổng hợp sau khi tích hợp đầy đủ đã ghi ở đầu Mục 1 (`1.0 / 0.7 / 0.9`). Chi tiết cách dùng AI và kiểm lại nằm trong mục Prompt 4 của [prompts.md](prompts.md).

### Đối chiếu Detection ↔ Panoptic — Bạch Đăng Ngọc Tuấn (TV3)

Phụ trách module `validator/cross_check.py` đối chiếu hai nguồn nhãn độc lập (YOLO Detection và COCO Panoptic Segmentation) để phát hiện 5 lỗi gán nhãn (`class_swap`, `category_swap`, `bbox_drift`, `missing_box`, `instance_merge`) và xuất ra `candidates.json`. Bảng dưới ghi nhận số ứng viên sinh ra trên các lô:

| Lô | Số ảnh | Số ứng viên sinh ra | Tỷ lệ lọc nhiễu tự nhiên |
|---|---:|---:|---|
| Lô sạch (`runs/clean`) | 50 | 0 | 100% không bị báo động giả |
| Seed luyện tập 999 | 250 | 18 | Hàng đợi cực gọn (~2-3 ảnh/người) |

Thuật toán đạt **Recall 100% (9/9 lỗi gán nhãn)** trên seed 999 mà vẫn giữ hàng đợi cực kỳ tối ưu, giúp nhóm hoàn thành review mắt nhanh chóng trong 10-15 phút. Chi tiết cách dùng AI và kiểm lại nằm trong mục Prompt 8 của [prompts.md](prompts.md).

## 2. Vì sao báo hết ứng viên làm F1 giảm?

Công thức tính điểm của bài lab dựa trên **F1-score** (trung bình điều hòa giữa Precision và Recall):
$$F_1 = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}} = \frac{2 \times \text{TP}}{2 \times \text{TP} + \text{FP} + \text{FN}}$$

Trong đó, **báo thừa (False Positive - FP) bị trừ điểm nặng tương đương với việc bỏ sót lỗi (False Negative - FN)**:
1. **Nếu không lọc mà báo bừa toàn bộ ứng viên:**
   - Dữ liệu COCO có sự lệch tự nhiên vốn có giữa bounding box và mask segmentation (do vật thể bị che khuất một phần, đám đông đứng sát nhau, v.v.).
   - Nếu dùng thuật toán ghép thô (chỉ dựa vào IoU lỏng lẻo không qua greedy matching), hệ thống sẽ sinh ra tới **128 ứng viên** trên 250 ảnh (trong khi thực tế chỉ có 9 lỗi gán nhãn thật).
   - Nếu tự động nhận hết 128 ứng viên này là lỗi:
     $$\text{Precision} = \frac{9}{128} \approx 7.0\% \implies F_1 \approx 13.1\%$$
     Điểm $F_1$ sụt giảm thảm hại từ ~0.9 xuống chỉ còn ~0.13 do có tới 119 ca báo thừa (FP)!
2. **Khi áp dụng thuật toán Greedy Matching kết hợp Review bằng mắt:**
   - Thuật toán giúp cô lập hàng đợi xuống chỉ còn đúng **18 ảnh nghi vấn** mà vẫn bắt trọn 9/9 lỗi thật (Recall = 100%).
   - Con người trực tiếp mở ảnh lên xem để phân biệt giữa lệch tự nhiên (ghi `rejected`) và lỗi thật (ghi `confirmed`), loại bỏ triệt để các ca FP. Nhờ đó, Precision được đẩy lên mức tối đa và $F_1$ đạt trên 0.9.

## 3. Quyết định và lineage
- **QC v1:** `22/250` ảnh lỗi (**8.8%**), vượt ngưỡng cho phép **2%** → kết luận **HOLD** lô v1 (`lab250_96113fd7fec7`), không cho phép tiếp tục dùng để huấn luyện; tách ảnh lỗi detection sang `rework_queue.csv`, sửa các lỗi mức file/metadata và đóng gói bản `lab250_96113fd7fec7_v2`.
- **Vì sao `R-021` phải xem lại hoặc train lại (`affected=True action=review_or_retrain`):** `R-021` đã được huấn luyện trực tiếp trên lô v1 chứa 22 lỗi (gồm cả `scene_leak` và sai nhãn detection). Việc phát hành dataset v2 **không tự động sửa trọng số của model đã học trước đó**, nên bắt buộc phải kiểm tra lại độ chính xác của `R-021` hoặc train lại trên dữ liệu sạch v2.

## 4. Hash chứng minh gì, không chứng minh gì?
- **Hash (SHA-256) chứng minh:** Tính toàn vẹn theo từng byte của file — xác nhận file trong gói bàn giao không bị hỏng, thiếu bit, tráo đổi hay chỉnh sửa sau khi lập `manifest.csv` / đóng gói `.sha256`.
- **Hash KHÔNG chứng minh:** Chất lượng hay độ đúng của nhãn/dữ liệu bên trong (ảnh bị gán sai lớp, box bị lệch, hoặc `scene_leak` vẫn có thể tạo ra mã SHA-256 hợp lệ). Vì vậy hash chỉ đảm bảo tính nhất quán khi bàn giao, không thay thế được QC và review bằng mắt.

## 5. Truy vết
- **Kết quả trên seed 999 (`runs/r999/trace.json`):** `tier_a = 2` ảnh (thuộc `scene_687`, `scene_917` do team AI báo), `tier_b = 4` ảnh khác cùng điều kiện chưa được báo, `notify = 5` mã người gán/người kiểm (`F1: tier_a 1.0 · tier_b 1.0 · notify 1.0`).
- **Tiêu chí tầng (a)/(b):** Lọc các job dùng guideline cũ (`v1.2`) có chứa ít nhất một box detection thuộc lớp bị đổi quy tắc (`surfboard` trên `r999`, `truck` trên `de_an`); ảnh nằm trong các scene team AI nêu thuộc `tier_a`, các ảnh còn lại thỏa điều kiện thuộc `tier_b`.
- **Vì sao lấy guideline theo `jobs.csv` (không lấy theo `metadata.json` của từng ảnh):** Vì trường `guideline_version` ở từng ảnh có thể đang bị sai do lỗi `guideline_mismatch`, trong khi `jobs.csv` lưu phiên bản guideline chuẩn áp dụng cho cả job đó.

## 6. Bug hoặc điểm chưa rõ trong lab (nếu có)
Không phát hiện bug ở bộ script gốc trong `scripts/`.
