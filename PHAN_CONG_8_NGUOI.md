# Phân công công việc — Nhóm 13 (8 người: 1 Lead + 7 Thành viên)

> **Nguyên tắc bắt buộc (theo `RULES.md` & `RUBRIC.md`):**
> 1. **Cả 8 người (Lead + 7 thành viên)** đều phải trực tiếp **xem ảnh** ở Pha 2 (và Đề ẩn 40 phút) để tự ghi `review_log.csv` (ghi chú ≥ 20 ký tự, nêu rõ **thấy gì trong ảnh**).
> 2. **Mỗi người ≥ 2 commit có nội dung** (dùng đúng tên & email Git của mình).
> 3. **Quy tắc Validator (vi phạm = 0 điểm mục 1):** `validator/validate.py` **chỉ dùng thư viện chuẩn** (+ `scripts/pngutil.py`), cấm Pillow, cấm mạng, cấm đọc `_private/`, `data_source/`, annotation COCO. Định dạng `target` trong `errors.json`: `scene_leak` dùng `scene_id`, mọi lỗi khác dùng **tên ảnh không đuôi**.
> 4. **Ai cũng phải nắm để vấn đáp (3 phút/người):** giải thích + sửa được 1 đoạn `validator/validate.py`, giải thích 1 dòng `confirmed`/`rejected` trong `review_log.csv`, và giải thích 1 con số trong `README.txt` của lô v2.

---

## Bảng phân công tổng quan (8 người)

| Vai trò | Phụ trách chính | Công việc theo từng Pha | Commit tối thiểu (gợi ý) |
|---|---|---|---|
| **Lead — Nguyễn Hữu Đăng** (`huudang-de`) | **Điều phối, Tích hợp, `REPORT.md` & Nộp bài** | - **P0:** Tải dữ liệu (`download_public.py`), tạo lô (`run_lab.py --seeds 999`, `runs/clean`), cập nhật `README.md` (`# Day 10 Lab — Nhóm 13`), `submission/TEAM.md`, kiểm tra tên repo đúng mẫu `K5-L23-DAY10-NHOM13-Release` (nếu lớp yêu cầu).<br>- **P1–P2:** Review code `validator/validate.py` (đảm bảo chỉ dùng thư viện chuẩn), chốt ngưỡng trên lô sạch, xem ảnh phần của mình.<br>- **P6:** Tổng hợp `submission/REPORT.md` (từ số liệu TV3, TV5, TV6), chạy `export_submission.py`, `check_handover.py` = 0 FAIL, tổ chức 5–10 phút **sync vấn đáp chéo** cho cả 8 người, rà soát commit & nộp bài. | 1. `P0: setup repo, TEAM.md & lab batches`<br>2. `P6: complete REPORT.md & final submission` |
| **TV1 — Nguyễn Văn Nhất** (`Edelzz`) | **Validator Luật (File & Detection)** | - **P1:** Code 5 lỗi luật trong `validator/validate.py`: `missing_image`, `wrong_hash` (tính lại sha256 `rb`), `invalid_class`, `bbox_out_of_bounds`, `duplicate_box` (cùng lớp, cùng kích thước, lệch 1–2 px).<br>- **P2 & Đề ẩn:** Xem ảnh phần được chia, ghi `review_log.csv`; gửi log prompt AI + chỗ AI sai cho TV7/Lead. | 1. `P1: implement file & detection rule checks`<br>2. `P2: review assigned images in review_log.csv` |
| **TV2 — Vũ Hữu Hưng** (`hungvu208`) | **Validator Luật (Metadata & Panoptic)** | - **P1:** Code 4 lỗi luật: `scene_leak` (target `scene_id`), `guideline_mismatch` (`jobs.csv`), `invalid_category_id`, `thing_overlap` (dùng `scripts/pngutil.py`, bỏ id 0); ghép CLI `--out` (hỗ trợ xuất riêng `rules.json`), test trên `runs/r999` & `runs/clean` đạt F1 ≈ 1.0.<br>- **P2 & Đề ẩn:** Xem ảnh phần được chia, ghi `review_log.csv`; gửi log prompt AI cho TV7/Lead. | 1. `P1: implement metadata & panoptic rule checks`<br>2. `P1: verify rule validator on r13007 & clean batch` |
| **TV3 — Bạch Đăng Ngọc Tuấn** (`Tuan-Bach`) | **Đối chiếu Detection ↔ Panoptic** | - **P2:** Code phần đối chiếu trong `validator/validate.py` xuất `candidates.json` (`class_swap`/`category_swap`, `bbox_drift`, `missing_box`, `instance_merge`), dùng pixel mask & bỏ `iscrowd`.<br>- **Báo cáo P2:** Đo số ứng viên trên `runs/clean` để tinh chỉnh ngưỡng; cung cấp số liệu `runs/clean` + lý do chọn ngưỡng + trả lời *"Vì sao báo hết ứng viên lại làm F1 giảm?"* cho `REPORT.md`.<br>- **P2 & Đề ẩn:** Xem ảnh phần được chia; gửi log prompt AI cho TV7/Lead. | 1. `P2: implement det-panoptic matching & candidates`<br>2. `P2: tune thresholds using clean batch` |
| **TV4 — leminhthang** (`leminhthang96`) | **Tool xem ảnh & Tổng hợp Review** | - **P2:** Viết script phụ trợ vẽ box + viền segment lên ảnh (được dùng Pillow) cho cả 8 người xem ảnh nhỏ; chia đều hàng đợi `candidates.json` cho 8 người; gộp `review_log.csv` bằng `merge_review.py` và chạy `score_findings.py`.<br>- **P2 & Đề ẩn:** Xem ảnh phần được chia; gửi log prompt AI cho TV7/Lead. | 1. `P2: add visual review helper tool`<br>2. `P2: merge review_log.csv & score findings` |
| **TV5** *(chưa điền)* | **Lineage & Bàn giao v2 (P3–P4)** | - **P3:** Tính tỉ lệ lỗi v1 (>2% → `HOLD`), chạy `lineage.py record/impact` (`R-021`).<br>- **P4:** Dựng `<release_id>_v2` (với `wrong_hash` phải **mở ảnh kiểm trước**; sửa `guideline_mismatch`/`scene_leak`; lập `rework_queue.csv`, `manifest.csv`, `label_summary.csv`, `truyvet.csv`, `README.txt` ghi rõ mục Ghi chú đã sửa gì & các ảnh chỉ lỗi panoptic); chạy `pack_release.py`, `lineage.py record --event release --release-id <release_id>_v2 --parent <release_id_v1>`, và `check_handover.py` (**không commit `.zip`**).<br>- **Báo cáo P3–P4:** Giải thích `R-021` & ý nghĩa hash cho `REPORT.md`.<br>- **P2 & Đề ẩn:** Xem ảnh phần được chia; gửi log prompt AI cho TV7/Lead. | 1. `P3-P4: record lineage & build v2 handover`<br>2. `P4: verify pack_release & check_handover` |
| **TV6** *(mới)* | **Truy vết Ticket (P5) & Test đa seed** | - **P1:** Tạo thêm 1–2 seed phụ bằng `inject_release.py` để test chéo validator (đạt F1 ≈ 1.0 trên nhiều seed khác nhau).<br>- **P5:** Đọc `incoming/ticket.md` & `guideline/changelog.md`, viết script/logic xuất `trace.json` (`tier_a`, `tier_b`, `notify` lấy guideline theo `jobs.csv`, không lấy theo ảnh) cho cả seed luyện tập & đề ẩn.<br>- **Báo cáo P5:** Cung cấp F1 luyện tập (`rule_detectable`, `cross_check_review`, `trace`) và tiêu chí `jobs.csv` cho `REPORT.md`.<br>- **P2 & Đề ẩn:** Xem ảnh phần được chia; gửi log prompt AI cho TV7/Lead. | 1. `P1: test validator across extra injected seeds`<br>2. `P5: generate & verify trace.json` |
| **TV7** *(mới)* | **Bảo mật, Minh bạch AI & Kiểm toán Review** | - **P6 (`security.md`):** Điền đủ 3 mục trong `security.md` (ca USB, 5 việc được/không, ca khuôn mặt kết luận **Hold + báo người phụ trách**), tìm ví dụ ảnh có người thật ngay trong `runs/r999/delivery/images/`.<br>- **P6 (`prompts.md`):** Thu thập & tổng hợp prompt AI + chỗ AI sai + cách nhóm kiểm lại của cả 8 người vào `submission/prompts.md`.<br>- **Kiểm toán Review:** Phụ TV4 rà soát chất lượng `review_log.csv` của cả 8 người (note ≥ 20 ký tự, nêu rõ thấy gì, có `rejected` kèm lý do, phân biệt đúng `class_swap` vs `category_swap`) trước khi merge.<br>- **P2 & Đề ẩn:** Xem ảnh phần được chia. | 1. `P6: complete security.md with batch examples`<br>2. `P6: audit review_log & compile prompts.md` |

---

## Phối hợp khi chạy Đề ẩn (40 phút cuối buổi — 8 người)

Khi giảng viên phát `de_an.zip`, **Lead** điều phối cả 8 người chạy song song:
1. **Lead:** Giải nén `de_an.zip` vào gốc repo → tạo thư mục `delivery/` (**không commit `delivery/`**).
2. **TV2 & TV3:** Chạy ngay validator xuất lỗi luật ra `rules.json` riêng để tránh xung đột khi merge:
   ```powershell
   py -X utf8 validator/validate.py delivery --out submission/de_an/rules.json --candidates submission/de_an/candidates.json
   ```
3. **TV4:** Dùng tool vẽ box/mask chia đều `candidates.json` thành **8 phần bằng nhau** cho **8 người** cùng xem ảnh và ghi `verdict` + `note` (≥ 20 ký tự, nêu rõ thấy gì, phân biệt `class_swap` vs `category_swap`, ghi `rejected` kèm lý do nếu lệch tự nhiên) vào `submission/de_an/review_log.csv`.
4. **TV6 (+ TV5 hỗ trợ):** Trong lúc cả nhóm xem ảnh, đọc `delivery/incoming/ticket.md` và `delivery/guideline/changelog.md` để xuất `submission/de_an/trace.json`.
5. **TV4 + TV7 + Lead:** Rà soát nhanh `note` của cả 8 người trong `review_log.csv`, chạy `merge_review.py --rules submission/de_an/rules.json --review submission/de_an/review_log.csv --out submission/de_an/errors.json`, kiểm tra lại format tất cả file trong `submission/de_an/`, rồi **Lead** kiểm tra commit của đủ **8 người** và push lên Git.

---

## Checklist đồng bộ trước khi nộp bài
- [ ] `submission/TEAM.md` đã điền đủ Họ tên, MSHV, GitHub username của cả **8 người** (Lead + 7 thành viên).
- [ ] `submission/REPORT.md` đủ 5 nhóm nội dung/số liệu thật (từ TV3, TV5, TV6, Lead).
- [ ] `submission/prompts.md` đã tổng hợp prompt AI + chỗ AI sai + cách kiểm lại từ cả 8 người (TV7 phụ trách chính).
- [ ] Đã sync nhóm 5–10 phút để **cả 8 người** đều giải thích được validator, `review_log.csv`, và `README.txt` v2 khi vấn đáp.
- [ ] Không commit `runs/`, `data_source/`, `*.zip`, hay `delivery/` của đề ẩn.
- [ ] `git log --format="%an <%ae> - %s"` có **đủ 8 người, mỗi người ≥ 2 commit có nội dung**.
