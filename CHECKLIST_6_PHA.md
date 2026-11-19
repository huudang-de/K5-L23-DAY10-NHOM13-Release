# Checklist 6 Pha — Day 10 Lab: Bàn giao dataset & Truy vết

> Tài liệu tham khảo nhanh cho nhóm (tổng hợp từ `GUIDE.md`, `CHECKPOINTS.md`, `SUBMISSION.md`, `RULES.md`, `RUBRIC.md`).
> *Lưu ý: File ghi chú cá nhân/nhóm — nhớ xóa hoặc không commit nếu không cần đưa vào repo nộp bài.*

---

## Pha 0 — Chuẩn bị (~15 phút | Mốc 0:15)
- [ ] Kiểm tra Python 3.10+ (`py --version` trên Windows; chạy từng lệnh riêng, dùng `-X utf8` nếu lỗi font).
- [ ] Tải dữ liệu công khai (~1 GB, chạy 1 lần):
  ```powershell
  py -X utf8 scripts/download_public.py
  ```
- [ ] Tạo lô luyện tập theo seed của nhóm (chỉ chạy `run_lab.py` **1 lần** để gắn `R-021` vào lineage):
  ```powershell
  py -X utf8 scripts/run_lab.py --seeds <seed>
  ```
- [ ] Tạo lô sạch để đo nhiễu tự nhiên:
  ```powershell
  py -X utf8 scripts/inject_release.py --seed 5 --no-faults --out runs/clean
  ```
- [ ] Đọc `docs/DELIVERY.md` và mở thử `runs/r<seed>/delivery/`.
- [ ] Chia việc trong `submission/TEAM.md` (1–2 người viết validator luật, 2 người viết đối chiếu + tool xem ảnh, 1–2 người làm bàn giao + truy vết; **mọi thành viên đều phải xem ảnh ở Pha 2**).
- [ ] Commit khởi tạo (`git add -A` → `git commit -m "P0: chia viec"`).

---

## Pha 1 — Bắt lỗi luật (~40 phút | Mốc 0:55)
- [ ] Viết `validator/validate.py` (chỉ thư viện chuẩn + được `import scripts/pngutil.py`, không dùng mạng, chỉ đọc thư mục `delivery/` được truyền vào):
  ```powershell
  py -X utf8 validator/validate.py <delivery> --out <errors.json> [--candidates <candidates.json>]
  ```
- [ ] Bắt đủ **9 loại lỗi luật**:
  - **File:** `missing_image`, `wrong_hash` (tính lại sha256 theo bytes `rb`).
  - **Nhãn detection:** `invalid_class`, `bbox_out_of_bounds`, `duplicate_box` (cùng lớp, cùng kích thước, chỉ lệch 1–2 px).
  - **Metadata:** `scene_leak` (target là `scene_id`), `guideline_mismatch` (so với guideline của job trong `jobs.csv`).
  - **Panoptic:** `invalid_category_id`, `thing_overlap` (đếm pixel theo `id = R + G*256 + B*256^2` so với `area`, bỏ qua id 0).
- [ ] Kiểm thử trên seed của nhóm, thêm ít nhất 1 seed tạo bằng `inject_release.py`, và `runs/clean` (lô sạch phải ra 0 lỗi luật).
- [ ] Đo bằng `py -X utf8 scripts/score_findings.py --run runs/r<seed>` → mục tiêu lỗi luật **F1 ≈ 1.0**.

---

## Pha 2 — Đối chiếu detection ↔ panoptic & Xem ảnh (~55 phút | Mốc 1:50)
- [ ] Bổ sung phần đối chiếu vào `validator/validate.py` để xuất `candidates.json` (4 lỗi gán nhãn: `class_swap`/`category_swap`, `bbox_drift`, `missing_box`, `instance_merge`).
  - Ghép box YOLO (đổi sang pixel) với segment thing theo IoU & tên lớp; ưu tiên dùng **pixel mask** và bỏ `iscrowd`.
- [ ] Đo nhiễu tự nhiên trên `runs/clean`, chọn ngưỡng sao cho hàng đợi đủ nhỏ để xem hết mà không sót lỗi; ghi số liệu & lý do vào `submission/REPORT.md`.
- [ ] Chuẩn bị công cụ nhỏ vẽ box + viền segment lên ảnh (được phép dùng Pillow cho tool xem ảnh này) để sẵn sàng cho đề ẩn.
- [ ] Chia hàng đợi cho **tất cả thành viên** xem ảnh và ghi `runs/r<seed>/review_log.csv` (`image,type,verdict,note`):
  - Ghi chú ≥ 20 ký tự, nêu rõ **thấy gì trong ảnh** và ai xem.
  - Phân biệt `confirmed` (lỗi thật) vs `rejected` (lệch tự nhiên của COCO: vật bị che, crowd...).
- [ ] Gộp lỗi luật + lỗi gán nhãn đã `confirmed` thành `errors.json`:
  ```powershell
  py -X utf8 scripts/merge_review.py --rules runs/r<seed>/rules.json --review runs/r<seed>/review_log.csv --out runs/r<seed>/errors.json
  py -X utf8 scripts/score_findings.py --run runs/r<seed>
  ```
- [ ] Trả lời câu hỏi trong `submission/REPORT.md`: *Vì sao báo hết ứng viên lại làm F1 giảm?*

---

## Pha 3 — Quyết định & Lineage (~15 phút | Mốc 2:05)
- [ ] Tính tỉ lệ lỗi v1 = `số mục errors.json / 250`. Theo ngưỡng **> 2% thì HOLD** (không Release).
- [ ] Ghi quyết định và kiểm tra ảnh hưởng lên training run:
  ```powershell
  py -X utf8 scripts/lineage.py record --event decision --release-id <release_id_v1> --decision HOLD
  py -X utf8 scripts/lineage.py impact --release-id <release_id_v1>
  ```
- [ ] Xác nhận đầu ra có `R-021: affected=True action=review_or_retrain` và giải thích trong `submission/REPORT.md`.

---

## Pha 4 — Bàn giao lô v2 (~40 phút | Mốc 2:45)
- [ ] Tạo `runs/r<seed>/handover/<release_id>_v2/` (**không sửa gì trong `delivery/` của v1**):
  - **Sửa ngay trong v2:** `wrong_hash` (mở ảnh kiểm tra còn nguyên mới ghi hash mới, ảnh hỏng đưa vào rework), `guideline_mismatch`, `scene_leak` (gom cả cảnh về 1 split).
  - **Đưa vào `rework_queue.csv` & bỏ khỏi v2:** `missing_image`, `invalid_class`, `bbox_out_of_bounds`, `duplicate_box`, `class_swap`, `bbox_drift`, `missing_box`.
  - **Giữ lại v2 & ghi chú báo team panoptic trong `README.txt`:** `invalid_category_id`, `thing_overlap`, `category_swap`, `instance_merge`.
- [ ] Đủ các file trong `<release_id>_v2/`: `images/`, `labels/`, `manifest.csv`, `label_summary.csv`, `truyvet.csv`, `rework_queue.csv`, `README.txt` (theo `templates/README.txt`).
- [ ] Đóng gói, ghi lineage v2 và kiểm tra bàn giao:
  ```powershell
  py -X utf8 scripts/pack_release.py runs/r<seed>/handover/<release_id>_v2
  py -X utf8 scripts/lineage.py record --event release --release-id <release_id>_v2 --parent <release_id_v1>
  py -X utf8 scripts/check_handover.py --run runs/r<seed>
  ```
- [ ] Nếu sửa bất kỳ file nào trong v2 sau khi đóng gói, phải lập lại manifest (nếu cần) và chạy lại `pack_release.py`.

---

## Pha 5 — Truy vết ticket (~20 phút | Mốc 3:05)
- [ ] Đọc `incoming/ticket.md` và `guideline/changelog.md`.
- [ ] Tạo `runs/r<seed>/trace.json` (theo `templates/trace.json`) với 3 khoá:
  - `tier_a`: ảnh trong các cảnh team AI nêu, thuộc job guideline cũ, có ít nhất 1 box detection thuộc lớp bị đổi quy tắc.
  - `tier_b`: các ảnh khác cùng điều kiện (job guideline cũ, có lớp đó) chưa được báo.
  - `notify`: mã người gán và người kiểm của các job chứa ảnh `tier_a` và `tier_b` (lấy guideline theo `jobs.csv`, không lấy theo ảnh).
- [ ] Kiểm tra lại điểm truy vết bằng `score_findings.py`.

---

## Pha 6 — Bảo mật (10 phút) & Đề ẩn (40 phút) | Mốc 3:15 – 3:55
- [ ] Điền `runs/r<seed>/security.md` theo `templates/security.md` (đủ 3 mục; ca khuôn mặt kết luận **Hold + báo người phụ trách**, nêu ví dụ ảnh có người từ lô của nhóm).
- [ ] Chạy `py -X utf8 scripts/check_handover.py --run runs/r<seed>` đảm bảo **0 FAIL**.
- [ ] Xuất bài luyện tập sang `submission/`:
  ```powershell
  py -X utf8 scripts/export_submission.py --run runs/r<seed>
  ```
- [ ] **Đề ẩn (40 phút):**
  - Tải & giải nén `de_an.zip` vào gốc repo (tạo ra `delivery/`, **không commit thư mục này**).
  - Chạy validator:
    ```powershell
    py -X utf8 validator/validate.py delivery --out submission/de_an/errors.json --candidates submission/de_an/candidates.json
    ```
  - Cả nhóm xem ảnh ứng viên, ghi `submission/de_an/review_log.csv`.
  - Chốt `submission/de_an/errors.json` và làm `submission/de_an/trace.json`.

---

## Checklist trước khi nộp bài
- [ ] Đổi tiêu đề `README.md` thành `# Day 10 Lab — Nhóm <XX>`.
- [ ] Hoàn thiện `submission/TEAM.md`, `submission/REPORT.md`, `submission/prompts.md` (ghi rõ prompt AI đã dùng, chỗ AI sai, cách kiểm lại).
- [ ] Mỗi thành viên có **ít nhất 2 commit có nội dung** (đúng tên & email) và chuẩn bị vấn đáp (~3 phút/người: giải thích + sửa validator, giải thích 1 dòng `review_log.csv`, giải thích 1 số trong `README.txt` v2).
- [ ] Không commit `runs/`, `data_source/`, `*.zip`, hay `delivery/` của đề ẩn.
- [ ] Push lên repo `K5-L23-DAY10-NHOM[XX]-Release` và nộp link lên LMS.
