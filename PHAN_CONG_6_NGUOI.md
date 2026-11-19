# Phân công công việc — Nhóm 6 người (1 Lead + 5 Thành viên)

> **Nguyên tắc bắt buộc (theo `RULES.md` & `RUBRIC.md`):**
> 1. **Cả 6 người (Lead + 5 thành viên)** đều phải trực tiếp **xem ảnh** ở Pha 2 (và Đề ẩn 40 phút) để tự ghi `review_log.csv`.
> 2. **Mỗi người ≥ 2 commit có nội dung** (dùng đúng tên & email Git của mình).
> 3. **Ai cũng phải nắm để vấn đáp (3 phút/người):** giải thích + sửa được 1 đoạn `validator/validate.py`, giải thích 1 dòng `confirmed`/`rejected` trong `review_log.csv`, và giải thích 1 con số trong `README.txt` của lô v2.

---

## Bảng phân công tổng quan

| Vai trò | Phụ trách chính | Công việc theo từng Pha | Commit tối thiểu (gợi ý) |
|---|---|---|---|
| **Lead (Nhóm trưởng)** | **Điều phối, Tích hợp, Bảo mật & Nộp bài** | - **P0:** Tạo repo, cập nhật `README.md`, `submission/TEAM.md`, chạy `run_lab.py` (seed nhóm) & `inject_release.py` (lô sạch).<br>- **P1–P2:** Review code `validator/validate.py`, chốt ngưỡng trên lô sạch, tham gia xem ảnh phần của mình, tổng hợp `submission/REPORT.md` & `submission/prompts.md`.<br>- **P6:** Hoàn thiện `security.md` (đủ 3 mục, ví dụ ảnh có người từ lô), chạy `export_submission.py`, kiểm tra `check_handover.py` = 0 FAIL, quản lý merge & nộp bài. | 1. `P0: setup repo, TEAM.md & lab batches`<br>2. `P6: complete security.md, REPORT.md & final submission` |
| **Thành viên 1** | **Validator Luật (File & Detection)** | - **P1:** Code 5 lỗi luật trong `validator/validate.py`: `missing_image`, `wrong_hash` (tính lại sha256 `rb`), `invalid_class`, `bbox_out_of_bounds`, `duplicate_box`.<br>- **P2 & Đề ẩn:** Xem ảnh phần được chia, ghi `review_log.csv`. | 1. `P1: implement file & detection rule checks`<br>2. `P2: review assigned images in review_log.csv` |
| **Thành viên 2** | **Validator Luật (Metadata & Panoptic)** | - **P1:** Code 4 lỗi luật: `scene_leak`, `guideline_mismatch` (`jobs.csv`), `invalid_category_id`, `thing_overlap` (dùng `scripts/pngutil.py`); ghép CLI `--out`, test đa seed & `runs/clean` đạt F1 ≈ 1.0.<br>- **P2 & Đề ẩn:** Xem ảnh phần được chia, ghi `review_log.csv`. | 1. `P1: implement metadata & panoptic rule checks`<br>2. `P1: verify rule validator on multiple seeds & clean batch` |
| **Thành viên 3** | **Đối chiếu Detection ↔ Panoptic** | - **P2:** Code phần đối chiếu trong `validator/validate.py` xuất `candidates.json` (`class_swap`/`category_swap`, `bbox_drift`, `missing_box`, `instance_merge`), dùng pixel mask & bỏ `iscrowd`; đo nhiễu trên `runs/clean` để tinh chỉnh ngưỡng.<br>- **P2 & Đề ẩn:** Xem ảnh phần được chia, ghi `review_log.csv`. | 1. `P2: implement det-panoptic matching & candidates`<br>2. `P2: tune thresholds using clean batch` |
| **Thành viên 4** | **Tool xem ảnh & Tổng hợp Review** | - **P2:** Viết script phụ trợ vẽ box + viền segment lên ảnh (được dùng Pillow) cho cả nhóm xem ảnh nhỏ; gộp `review_log.csv` của cả 6 người bằng `merge_review.py` và chạy `score_findings.py`.<br>- **P2 & Đề ẩn:** Xem ảnh phần được chia, ghi `review_log.csv`. | 1. `P2: add visual review helper tool`<br>2. `P2: merge review_log.csv & score findings` |
| **Thành viên 5** | **Lineage, Bàn giao v2 & Truy vết** | - **P3:** Tính tỉ lệ lỗi v1 (>2% → `HOLD`), chạy `lineage.py record/impact` (`R-021`).<br>- **P4:** Dựng `<release_id>_v2` (sửa `wrong_hash`/`guideline_mismatch`/`scene_leak`, lập `rework_queue.csv`, `manifest.csv`, `label_summary.csv`, `truyvet.csv`, `README.txt`), chạy `pack_release.py` & `check_handover.py`.<br>- **P5:** Đọc `ticket.md` & `changelog.md`, xuất `trace.json` (`tier_a`, `tier_b`, `notify` theo `jobs.csv`).<br>- **P2 & Đề ẩn:** Xem ảnh phần được chia. | 1. `P3-P4: record lineage & build v2 handover`<br>2. `P5: generate trace.json & verify check_handover.py` |

---

## Phối hợp khi chạy Đề ẩn (40 phút cuối buổi)

Khi giảng viên phát `de_an.zip`, **Lead** điều phối cả 6 người chạy song song:
1. **Lead:** Giải nén `de_an.zip` vào gốc repo → tạo thư mục `delivery/` (**không commit `delivery/`**).
2. **Thành viên 2 & 3:** Chạy ngay `validator/validate.py delivery --out submission/de_an/errors.json --candidates submission/de_an/candidates.json`.
3. **Thành viên 4:** Dùng tool vẽ box/mask chia đều `candidates.json` thành **6 phần bằng nhau** cho **Lead + 5 thành viên** cùng xem ảnh và ghi `verdict` + `note` (≥ 20 ký tự, nêu rõ thấy gì) vào `submission/de_an/review_log.csv`.
4. **Thành viên 5:** Trong lúc cả nhóm xem ảnh, đọc `delivery/incoming/ticket.md` và `delivery/guideline/changelog.md` để làm `submission/de_an/trace.json`.
5. **Thành viên 4 + Lead:** Chạy `merge_review.py` chốt `submission/de_an/errors.json`, rà soát lại format tất cả file trong `submission/de_an/`, rồi **Lead** kiểm tra commit của đủ 6 người và push lên Git.

---

## Nhắc nhở trước khi push
- Điền đầy đủ Họ tên, MSHV, GitHub username và Seed luyện tập vào `submission/TEAM.md`.
- Đổi dòng tiêu đề `README.md` thành `# Day 10 Lab — Nhóm <XX>`.
- Kiểm tra `git log --format="%an <%ae> - %s"` đảm bảo **đủ 6 người, mỗi người ≥ 2 commit có nội dung**.
