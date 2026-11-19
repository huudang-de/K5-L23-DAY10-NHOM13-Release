# Dùng AI

| # | Ai dùng | Công cụ | Prompt (tóm tắt) | AI sai ở đâu | Nhóm kiểm lại thế nào |
|---|---|---|---|---|---|
| 1 | Thành viên 4, nhóm 13, seed 13007 | Codex | Đọc bốn tài liệu lab; viết tool Python/Pillow review ảnh YOLO/Panoptic, chia sáu người, ghi CSV, hỗ trợ luyện tập/đề ẩn; kiểm thử và ghi prompt. Toàn văn bên dưới. | Rà soát phát hiện bản đầu chưa hỗ trợ xuất CSV chỉ có header khi phần được chia không có ảnh; đã bổ sung thao tác lưu phần rỗng và kiểm thử hồi quy. | AI đã chạy 19 kiểm thử tự động bằng fixture tổng hợp, gồm GUI Tkinter và tương thích merge_review.py; render 250 ảnh delivery và so SHA-256 của 758 file trước/sau. Thành viên thật vẫn phải trực tiếp xem ảnh và tự kết luận; chưa có review thật trong phiên này. |
| 2 | Thành viên 4, nhóm 13, seed 13007 | Codex | Đọc PHAN_CONG_8_NGUOI.md; đổi mặc định sang tám người, thêm --members, cập nhật hướng dẫn và kiểm thử. Toàn văn bên dưới. | Chưa phát hiện lỗi trong lần chạy 24 kiểm thử; đã đối chiếu để bỏ các giới hạn sáu người trong code và hướng dẫn hiện hành. | Kiểm tra mặc định tám phần, tùy chỉnh 1/2/3/6/8/10/12 phần, tính đủ/không trùng/cân bằng, biên CLI, GUI theo số thành viên và gộp CSV của 6/8/10 người. |
| 3 | Thành viên 4, nhóm 13, seed 999 | Codex | Đổi seed mặc định từ 13007 sang 999, giữ tám người, cập nhật đường dẫn, hướng dẫn và kiểm thử. Toàn văn bên dưới. | Chưa phát hiện lỗi qua 26 kiểm thử; đã kiểm tra đường dẫn đầu vào/đầu ra theo seed mới và không dùng dữ liệu seed cũ khi thiếu candidates. | 26/26 kiểm thử đạt; render 250 ảnh r999, so SHA-256 của 758 file delivery trước/sau đều không đổi. |
| 4 | Nguyễn Văn Nhất | Codex | Rà soát phân công, viết và kiểm tra validator cho 5 lỗi File & Detection trước khi commit. Chi tiết ở Prompt 4. | Lần đầu chạy `run_lab.py`, `-X utf8` chỉ áp dụng cho tiến trình cha. Tiến trình con báo lỗi mã hóa khi in tiếng Việt sau khi tạo lô. | Đã kiểm 16 ca giả lập và chạy CLI trên seed 999, seed bổ sung 11 và lô sạch 50 ảnh. Validator báo lần lượt 6, 7 và 0 phát hiện File & Detection. |
| 5 | Trần Anh Tùng (TV5) | Claude Code | Viết script dựng lô v2 từ `errors.json` theo GUIDE Pha 4, kiểm bằng `check_handover.py`. Chi tiết ở Prompt 5. | Bản đầu ghi sẵn "đã mở kiểm" cho ảnh `wrong_hash` khi chưa ai mở ảnh; đã sửa. | Chạy thử trên seed phụ trong thư mục tạm: PASS H1–H15. |
| 6 | Thành viên 4, nhóm 13, seed 999 | Codex | Cập nhật đường dẫn/import/test/hướng dẫn sau khi người dùng chuyển tool sang tools/review_tool.py; không sửa file gốc scripts/. | Sau khi di chuyển, test còn nạp đường dẫn cũ và suy ra merge_review.py từ thư mục tool. Đã đổi import sang tools/ và tách đường dẫn script gộp từ gốc repo. | 27/27 kiểm thử đạt; chạy CLI từ ngoài repo và kiểm tra tương thích scripts/merge_review.py. SHA-256 của 12 file gốc trong scripts/ không đổi. |
| 7 | Thành viên 4, nhóm 13, seed 999 | Codex | Gộp ba file xung đột rebase, giữ công việc hai phía, tool trong tools/, seed 999 và tám người; không sửa script gốc hoặc force push. | Hai phía cùng dùng số Prompt 4 cho hai công việc khác nhau; đã giữ mục validator của Nguyễn Văn Nhất là 4 và đánh lại mục chuyển tool là 5, bảo toàn nội dung cả hai. | 27/27 kiểm thử review đạt; đối chiếu nội dung và AST xác nhận giữ mã thực thi/test của phía nhóm trưởng và test CLI mới; so hash script gốc trước/sau. |
| 8 | Thành viên 4, nhóm 13, seed 999 | Codex | Kiểm toán tám review log, gộp CSV, tạo errors.json và chạy bộ chấm học viên một lần; chưa commit/push. | Chưa phát hiện lỗi gộp; kiểm toán đầu vào thấy chỉ bảy reviewer khác nhau, tám giả thuyết chưa có verdict riêng và bốn ảnh có cả lỗi luật lẫn review confirmed. Không tự sửa các dòng này. | Đối chiếu đủ 18 ảnh, 20 dòng không trùng cặp; 15 confirmed, 5 rejected; CSV gộp giữ nguyên toàn bộ trường nguồn; 26 lỗi sau merge. F1 làm tròn: tổng 0.8, luật 1.0, gán nhãn 0.6. |
| 9 | Bạch Đăng Ngọc Tuấn (TV3) | Antigravity | Viết module đối chiếu chéo Detection ↔ Panoptic (Pha 2), thuật toán Greedy Bipartite Matching bắt 5 lỗi gán nhãn xuất candidates.json. Chi tiết ở Prompt 9. | Bản đầu tiên so sánh toàn bộ các cặp khiến lô sạch bị báo động giả 32 ca (chủ yếu là instance_merge do người đứng cạnh nhau) và bỏ sót bbox_drift do tên lớp có dấu cách bị split sai. | Sửa tách tên lớp với maxsplit=1, dùng Greedy Matching theo IoU giảm dần. Đã kiểm thử trên lô sạch (0 ứng viên) và seed 999 (bắt đúng 9/9 lỗi gán nhãn, hàng đợi 18 ảnh). |

Đường dẫn tool hiện hành: **`tools/review_tool.py`**. Các đường dẫn cũ trong Prompt 1–3 bên dưới được giữ lại để bảo toàn lịch sử; dùng lệnh hiện hành trong `submission/REVIEW_TOOL.md`.

## Prompt 1 — Thành viên 4: công cụ review

Ngày: 19/11/2026. Công cụ: Codex. Prompt người dùng (giữ nội dung, chuẩn hóa xuống dòng):

```text
Tôi là thành viên số 4, nhóm 13, bài lab Day 10 Dataset Release & Handover. Seed của nhóm là 13007.

Hãy đọc GUIDE.md, RULES.md, docs/DELIVERY.md và PHAN_CONG_6_NGUOI.md để hiểu yêu cầu bài lab.

Viết công cụ review ảnh vào file scripts/review_tool.py với các yêu cầu:

1. Sử dụng Python và Pillow.
2. Đọc dữ liệu từ runs/r13007/delivery/.
3. Đọc candidates.json để lấy danh sách ảnh nghi ngờ có lỗi.
4. Hiển thị ảnh gốc, bounding box YOLO, tên class và đường viền mask Panoptic để dễ đối chiếu.
5. Có chức năng phóng to, chuyển ảnh trước/sau.
6. Chia danh sách cần review thành 6 phần cho 6 thành viên.
7. Cho phép người dùng chọn confirmed hoặc rejected và nhập ghi chú.
8. Xuất review_log.csv đúng định dạng bài lab.
9. Hỗ trợ cả dataset luyện tập và đề ẩn.
10. Giao diện đơn giản, dễ sử dụng trên Windows.

Không đọc _private/, data_source/ hoặc đáp án gốc.
Không chỉnh sửa delivery/ hoặc các script có sẵn.
Không tự động kết luận ảnh đúng hay sai thay người review.

Hãy kiểm thử công cụ và cung cấp lệnh chạy cụ thể.
Ghi lại prompt sử dụng AI vào submission/prompts.md.
```

### Phạm vi AI đã làm và cách kiểm lại

- Đã đọc bốn tài liệu được yêu cầu, mẫu CSV, script `merge_review.py` và dữ liệu công khai trong `runs/r13007/delivery/`. `scripts/review_tool.py` lúc bắt đầu là file trống chưa được Git theo dõi. Không sửa script lab có sẵn.
- Viết tool mới và `tests/test_review_tool.py`; hướng dẫn tại `submission/REVIEW_TOOL.md`. Tool dùng Pillow cho ảnh/box/viền segment và Tkinter cho GUI. Chia theo ảnh duy nhất để tránh hai người xử lý hai giả thuyết khác nhau của cùng ảnh.
- Kiểm thử bằng `py -X utf8 -m unittest discover -s tests -p test_review_tool.py -v`: **19/19 đạt**, Python 3.12.9, Pillow 11.3.0, Tk 8.6. Fixture tự tạo, chạy trong thư mục tạm; các verdict giả chỉ phục vụ kiểm thử, không vào log bài làm. Có kiểm tra RGB id nhiều byte, viền mép ảnh, tọa độ YOLO, ảnh thiếu, CSV Unicode, gộp sáu phần, dừng khi xung đột, GUI zoom/chuyển ảnh/lưu/đọc lại và xử lý phần rỗng.
- Kiểm tra kỹ thuật riêng trên **250 ảnh** trong delivery của r13007: render **4.424 mục nhãn** ở hai nguồn, không gặp cảnh báo đọc/render; so SHA-256 trước/sau cho **758 file**, tất cả không đổi. Đây là kiểm tra khả năng hiển thị, không phải kết luận chất lượng nhãn, số lỗi hay F1.
- Chưa có `runs/r13007/candidates.json` tại thời điểm thực hiện. Lệnh mặc định đã được kiểm tra là báo thiếu file rõ ràng. Cần thành viên phụ trách validator xuất candidates thật trước khi nhóm bắt đầu review.
- Không đọc `_private/`, `data_source/`, đáp án gốc; không dùng mạng, không chạy bộ chấm để dò kết quả. AI không ghi dòng `confirmed`/`rejected` nào cho ảnh thật, không chốt `errors.json` và không giả danh người đã xem ảnh.
- Nhóm cần trực tiếp chạy giao diện, xem vật trong từng ảnh, tự chọn verdict và ghi quan sát cụ thể kèm người xem. Kết quả kiểm thử do AI chạy ở trên chưa thay thế việc nhóm tự kiểm lại hoặc giải thích khi vấn đáp.

## Prompt 2 — Cập nhật nhóm tám người và tham số --members

Ngày: 19/11/2026. Công cụ: Codex. Prompt người dùng:

```text
Đọc PHAN_CONG_8_NGUOI.md và cập nhật review_tool.py cho nhóm 8 người thay vì 6 người. Cho phép tùy chỉnh số thành viên bằng --members, cập nhật hướng dẫn sử dụng và chạy lại kiểm thử.
```

- Đã đọc `PHAN_CONG_8_NGUOI.md`. Theo phân công mới, nhóm có Lead + 7 thành viên; TV4 phụ trách tool và tổng hợp review, TV7 hỗ trợ kiểm toán log. Seed mặc định vẫn là 13007 theo yêu cầu ban đầu.
- `--members` mặc định 8, nhận số nguyên >=1; `--member` vẫn mặc định 4, phải nằm trong 1..members. Chia vòng tròn trên tên ảnh duy nhất và giữ mọi giả thuyết của một ảnh cùng một phần; GUI và thống kê CLI dùng tổng số phần được cấu hình.
- Cập nhật `submission/REVIEW_TOOL.md`: TV1–TV7 dùng phần 1–7, Lead dùng phần 8; thêm ví dụ tùy chỉnh số người, gộp tám file và hướng dẫn chuyển từ sáu sang tám phần khi đã có log cũ. Prompt 1 và số liệu kiểm thử cũ được giữ nguyên như lịch sử.
- Đã chạy `py -X utf8 -m unittest discover -s tests -p test_review_tool.py -v`: **24/24 đạt**, gồm chia cân bằng/ổn định/không thiếu hoặc trùng cho 1/2/3/6/8/10/12 phần; từ chối members <=0, số không nguyên, member ngoài phạm vi; GUI mặc định 8 và tùy chỉnh 3 người; gộp 6/8/10 log. Đã kiểm tra `--help` hiển thị tham số mới và mặc định 8.
- Toàn bộ test của lần cập nhật dùng fixture tổng hợp trong thư mục tạm; không ghi review thật, không sửa delivery hoặc script lab có sẵn, không đọc nguồn bị cấm hay đáp án. Không chạy lại kiểm tra 250 ảnh vì phần đọc/render không thay đổi.

## Prompt 3 — Chuyển seed mặc định sang 999, giữ tám thành viên

Ngày: 19/11/2026. Công cụ: Codex. Prompt người dùng:

```text
Nhóm đổi seed từ 13007 sang 999 và có 8 thành viên. Hãy cập nhật tool, đường dẫn mặc định, hướng dẫn sử dụng và kiểm thử tương ứng.
```

- Đổi mặc định sang `runs/r999/delivery/`; candidates tự lấy từ `runs/r999/candidates.json`, log riêng TV4 mặc định là `runs/r999/review_log_m4.csv`. Vẫn mặc định `--members 8`, `--member 4` và hỗ trợ đường dẫn đề ẩn/tùy chỉnh.
- Cập nhật mọi đường dẫn luyện tập hiện hành trong `submission/REVIEW_TOOL.md` sang r999, gồm log tám người, lệnh gộp, rules/errors và preview. Nội dung Prompt 1/2 được giữ nguyên như lịch sử của các yêu cầu trước.
- Đã chạy `py -X utf8 -m unittest discover -s tests -p test_review_tool.py -v`: **26/26 đạt**. Hai kiểm thử mới dùng repo tạm có `runs/r999/` để xác minh lựa chọn delivery/candidates/log mặc định, tám phần và phần thứ tư; kiểm tra báo thiếu candidates ở r999 thay vì tự chuyển sang seed khác. Kiểm thử đường dẫn tùy chỉnh, GUI, CSV và gộp log vẫn đạt.
- Đã kiểm tra `--help` hiển thị đường dẫn r999 và mặc định tám người. Kiểm tra kỹ thuật trực tiếp `runs/r999/delivery/`: render **250 ảnh**, **4.422 mục nhãn**, không có cảnh báo đọc/render. So SHA-256 trước/sau của **758 file**, toàn bộ không đổi. Đây chỉ là kiểm tra hiển thị, không kết luận nhãn đúng/sai hoặc số lỗi.
- Chưa có `runs/r999/candidates.json` lúc thực hiện. Nhóm cần thành viên phụ trách validator xuất file trước khi review thật. Không tạo review thật hoặc tự chuyển log giữa các seed; không sửa delivery/script lab có sẵn, không đọc `_private/`, `data_source/` hay đáp án gốc.

## Prompt 4 — Nguyễn Văn Nhất: validator File & Detection

Công cụ Codex. Yêu cầu của người dùng được trích từ cuộc trao đổi:

```text
hãy kiểm tra phần Validator luật (File & Detection) & review ảnh của tôi, hệ thống chi tiết những việc tôi cần thao tác và chúng ta sẽ bắt đầu làm
hãy đảm bảo kết quả của tôi đạt trước khi commit phần công việc
```

### Phạm vi AI đã làm và cách kiểm lại

- Viết năm kiểm tra `missing_image`, `wrong_hash`, `invalid_class`, `bbox_out_of_bounds` và `duplicate_box` bằng thư viện chuẩn. Hàm `check_file_detection()` trả về các cặp `type` và `target` để TV2 ghép vào validator chung.
- Chạy 16 ca giả lập, gồm SHA-256 trên bytes, class ngoài phạm vi, box tràn ở cả bốn mép, làm tròn sát mép, cặp box gần nhau và đường dẫn nằm ngoài `delivery/`. Tất cả cho kết quả dự kiến.
- Chạy validator trên dữ liệu COCO thật. Seed 999 có 6 phát hiện, seed 11 có 7 phát hiện và lô sạch 50 ảnh có 0 phát hiện. Số liệu lấy từ `rules.json` của từng lô và chỉ phản ánh năm luật File & Detection. F1 của validator chung chưa được đo ở bước này.
- Lần chạy `run_lab.py` đã tạo lô seed 999 trước khi tiến trình con gặp lỗi mã hóa. Có thể đặt `$env:PYTHONUTF8 = "1"` trong PowerShell để các tiến trình Python con kế thừa chế độ UTF-8. Lô đã tạo chạy được qua CLI validator.
- Nguyễn Văn Nhất sẽ tự xem ảnh do TV4 phân công và ghi kết luận vào `review_log.csv` ở pha luyện tập và đề ẩn.

## Prompt 5 — Trần Anh Tùng: bàn giao v2

Ngày 19/11/2026, Claude Code. Yêu cầu (tóm tắt):

```text
Tôi phụ trách TV5 (lineage và bàn giao v2). Đọc GUIDE Pha 3–4, RULES, RUBRIC mục 3 và check_handover.py.
Viết script chỉ dùng thư viện chuẩn, dựng lô v2 từ errors.json mà không sửa delivery/ hay scripts/.
Không đọc _private/, data_source/, không chạy score_findings.py. Không tự kết luận thay người xem ảnh.
Chạy thử trên seed phụ, không ghi lineage của seed nhóm.
```

- AI viết `tools/build_v2.py` và chạy thử trên seed 4242 với `errors.json` giả lập (chỉ để thử, không nộp).
- Tôi tự mở xem ảnh `wrong_hash`, ghi HOLD, dựng v2 thật và chạy `check_handover.py` trên `runs/r999`.

## Prompt 6 — Cập nhật sau khi chuyển tool sang tools/

Ngày: 19/11/2026. Công cụ: Codex. Prompt người dùng (chuẩn hóa xuống dòng):

```text
Tôi đã chuyển scripts/review_tool.py sang tools/review_tool.py theo yêu cầu leader.

Hãy cập nhật các đường dẫn, import, file test và hướng dẫn sử dụng tương ứng. Không thay đổi bất kỳ file gốc nào trong scripts/. Chạy lại kiểm thử.
```

- Giữ nguyên thao tác di chuyển của người dùng. Cập nhật ví dụ chạy trong docstring của `tools/review_tool.py` và mọi lệnh hiện hành trong `submission/REVIEW_TOOL.md`. Gốc repo vẫn là `Path(__file__).resolve().parents[1]`; mặc định giữ seed 999, tám người, phần thứ tư.
- `tests/test_review_tool.py` nạp `tools/review_tool.py` bằng importlib. Đường dẫn script lab để kiểm tra tương thích được đặt riêng là `ROOT / "scripts/merge_review.py"`, không suy ra từ thư mục tool và không chuyển/sửa script gộp.
- Chạy `py -X utf8 -m unittest discover -s tests -p test_review_tool.py -v`: **27/27 đạt**. Test mới gọi CLI bằng đường dẫn tuyệt đối từ một thư mục tạm ngoài repo, kiểm tra `--help`, render fixture với `--check`, mặc định tám phần, gốc repo và không tạo verdict/log khi chỉ kiểm tra. Test tương thích script gộp có sẵn và GUI vẫn đạt.
- Đã chạy `py -X utf8 tools/review_tool.py --help`. So SHA-256 trước/sau của **12 file gốc còn hiện diện trong scripts/** (không tính cache Python), toàn bộ không đổi. Không khôi phục bản tool cũ trong scripts/; không ghi dữ liệu thật, không đọc nguồn bị cấm hoặc đáp án.

## Prompt 7 — Gộp xung đột rebase, bảo toàn công việc nhóm

Ngày: 19/11/2026. Công cụ: Codex. Prompt người dùng (chuẩn hóa xuống dòng):

```text
Git đang bị rebase conflict. Hãy giải quyết 3 file xung đột, giữ lại đầy đủ công việc của tôi và các thành viên khác.

Đảm bảo review_tool.py nằm trong tools/, sử dụng seed 999 và hỗ trợ 8 thành viên. Không sửa các script gốc của bài lab.

Chạy lại kiểm thử sau khi xử lý. Không force push.
```

- Đối chiếu bản gốc và cả hai phía của ba file `tools/review_tool.py`, `tests/test_review_tool.py`, `submission/prompts.md`; sao lưu file có conflict vào thư mục tạm trước khi gộp. Giữ phần hướng dẫn đã được Git gộp tự động, gồm đường dẫn tools/ và thông tin của nhóm trưởng.
- Tool giữ toàn bộ mã thực thi của hai phía, mặc định `runs/r999/delivery/`, tám người và phần thứ tư. Ví dụ đề ẩn dùng tên log `review_log_m4.csv`. Test giữ đường dẫn tool mới, đường dẫn `scripts/merge_review.py` tính từ gốc repo và test chạy CLI từ ngoài repo.
- Giữ nguyên nội dung nhật ký validator File & Detection của Nguyễn Văn Nhất ở Prompt 4; giữ nhật ký chuyển tool của TV4 và đánh số lại thành Prompt 5 để không trùng. Đã đối chiếu toàn văn hai mục với hai bản Git trước khi tiếp tục rebase.
- Chạy `py -X utf8 -m unittest discover -s tests -p test_review_tool.py -v`: **27/27 đạt**. Kiểm tra `--help` xác nhận mặc định r999 và tám người; so AST xác nhận không mất mã thực thi tool hoặc các test đã có của phía nhóm trưởng. Các test dùng dữ liệu tổng hợp và không ghi kết luận review thật.
- Không sửa file gốc trong scripts/, không đọc nguồn bị cấm/đáp án và không force push. Giữ nguyên tác giả commit khi tiếp tục rebase.

### Lần xử lý tiếp theo — gộp bổ sung nhật ký TV5

Prompt người dùng:

```text
Hãy giải quyết conflict trong submission/prompts.md, giữ đầy đủ nội dung của tôi và các thành viên khác, loại bỏ phần trùng lặp. Sau đó git add file đã xử lý và hoàn tất git rebase --continue. Không force push.
```

Giữ các mục chung 1–4 một lần, giữ mục bàn giao v2 của Trần Anh Tùng là Prompt 5; chuyển mục di dời tool thành Prompt 6 và lần gộp rebase trước thành Prompt 7. Nội dung riêng, người thực hiện và số liệu của cả hai phía được giữ nguyên; các số mục trong mô tả đợt xử lý trước phản ánh lịch sử lúc đó. Đã đối chiếu đầy đủ các phần và các dòng bảng với cả hai bản Git trước khi stage.

<<<<<<< HEAD
## Prompt 8 — Kiểm toán, gộp tám review log và tự đo F1

Ngày: 19/11/2026. Công cụ: Codex. Prompt người dùng (chuẩn hóa xuống dòng):

```text
Tôi đã nhận đủ 8 file review_log_m1.csv đến review_log_m8.csv trong runs/r999/.

Hãy thực hiện:

1. Kiểm tra đủ 18 ảnh đã review, không trùng hoặc bỏ sót.
2. Kiểm tra định dạng CSV, reviewer, verdict và ghi chú.
3. Gộp 8 file thành runs/r999/review_log.csv.
4. Chạy scripts/merge_review.py để tạo runs/r999/errors.json.
5. Chạy scripts/score_findings.py --run runs/r999.
6. Báo cáo số lượng confirmed, rejected và kết quả F1.

Không tự ý sửa kết luận review của thành viên, không đọc _private/ và không sửa các script gốc của bài lab.
Chưa commit hoặc push GitHub.
```

- Đối chiếu candidates.json, tám CSV, TEAM.md và rules.json. Có đủ 18/18 ảnh, không có ảnh ngoài danh sách hoặc ảnh thuộc hai file; không trùng cặp (image,type). Có 20 dòng do hai ảnh được review theo hai loại khác nhau. Header, type/verdict, mã reviewer trong TEAM và phần ghi chú >=20 ký tự sau tiền tố reviewer đều hợp lệ về hình thức; không có note trùng nguyên văn.
- Chỉ có bảy reviewer khác nhau: m6 và m7 cùng ghi TT1172001; chưa có trananhtung1. Có tám giả thuyết trong candidates chưa có verdict riêng, trong đó một số ảnh đã được review theo loại khác. Bốn ảnh có cả lỗi luật và lỗi gán nhãn confirmed. Đã ghi chi tiết vào runs/r999/review_audit.md và review_audit.json; không sửa người xem, loại lỗi, verdict hoặc note thay thành viên.
- Dùng tools/review_tool.py --merge để tạo review_log.csv; đối chiếu từng trường của cả 20 dòng với tám nguồn, kết quả giống hoàn toàn. Chạy script lab merge_review.py với rules.json, được 26 lỗi = 11 lỗi luật + 15 confirmed. Có 5 rejected; các dòng rejected không được đưa vào errors.json.
- Chạy đúng lệnh scripts/score_findings.py --run runs/r999 ở chế độ học viên một lần cho toàn bộ danh sách. Chỉ lấy báo cáo F1 làm tròn từ report.md: tổng ≈0.8, luật ≈1.0, gán nhãn ≈0.6. Không mở đáp án, không dùng --truth-dir, không dò điểm theo từng ảnh. Bộ chấm chuẩn tự xử lý đáp án nội bộ theo lệnh đã được yêu cầu.
- Không sửa tám log nguồn, candidates.json, rules.json hoặc script lab gốc. Chưa commit/push. Các điểm kiểm toán cần người review thật xác minh trước khi nhóm coi đây là kết quả chốt.

### Gộp lại sau khi nhận bản m6 cập nhật

Prompt người dùng:

```text
Tôi đã cập nhật review_log_m6.csv đúng người review.

Hãy gộp lại 8 file CSV, kiểm tra đủ 8 reviewer, tạo lại review_log.csv và errors.json, sau đó chạy chấm điểm F1.

Báo cáo các trường hợp còn thiếu hoặc bất thường. Không tự sửa kết luận review. Chưa commit hoặc push.
```

- Kiểm tra lại toàn bộ tám nguồn, xác nhận đủ tám reviewer khác nhau và khớp TEAM.md: m6 là trananhtung1, m7 là TT1172001. Đủ 18/18 ảnh, 20 dòng, không trùng cặp (image,type), không thiếu/thừa ảnh; ghi chú và định dạng hợp lệ về hình thức.
- Dùng nguyên bản m6 mới, gồm missing_box của 000000005477 là rejected và category_swap của 000000014831 là confirmed. Đây là các kết luận do thành viên cập nhật trong nguồn, AI không tự thay đổi. Tổng vẫn là 15 confirmed, 5 rejected.
- Gộp lại review_log.csv, đối chiếu toàn bộ trường của 20 dòng với nguồn; tạo lại errors.json gồm 26 lỗi (11 luật + 15 confirmed). Chạy bộ chấm học viên một lần sau cập nhật; F1 làm tròn từ report.md vẫn là tổng ≈0.8, luật ≈1.0, gán nhãn ≈0.6. Không dùng kết quả điểm để sửa verdict.
- Cập nhật review_audit.md và review_audit.json: còn tám cặp giả thuyết chưa có verdict riêng; ba ảnh có cả lỗi luật và confirmed review là 000000007818, 000000008211, 000000009772. Các điểm này cần người xem ảnh đối chiếu; không tự điền verdict còn thiếu hoặc bỏ lỗi. Vấn đề thiếu reviewer đã được giải quyết.
- Không sửa nguồn review, candidates, rules hoặc script lab gốc; chưa commit/push. Sao lưu các file tổng hợp cũ vào thư mục tạm trước khi ghi bản mới để giữ lịch sử.

### Gộp lại sau đợt kiểm tra bổ sung của các thành viên

Prompt người dùng:

```text
Các thành viên đã review lại và tôi đã cập nhật các file CSV trong runs/r999/.

Hãy gộp lại 8 file CSV, kiểm tra các trường hợp còn thiếu hoặc trùng lặp, tạo lại review_log.csv và errors.json, sau đó chạy score_findings.py để tính F1.

So sánh kết quả với lần trước. Không tự sửa kết luận review, không sửa scripts gốc và chưa commit hoặc push.
```

- Sao lưu các file tổng hợp trước khi ghi bản mới. Đủ tám reviewer và 18/18 ảnh, 20 dòng, không trùng cặp (image,type), không có ảnh bị chia cho hai file; ghi chú đủ độ dài.
- Phát hiện m1 dòng 3 (000000008211) có dấu phẩy trong note không được quote, CSV thành năm cột. Không sửa nguồn: chỉ ghép phần note bằng đúng dấu phẩy gốc và ghi bản sao tạm bằng csv.writer để gộp hợp lệ. Reviewer, type, verdict và toàn bộ nội dung ghi chú được giữ nguyên. Đã nêu rõ lỗi định dạng trong review_audit.md/json.
- Bản nguồn mới có missing_box của 000000008211 chuyển confirmed sang rejected. Ở m6, category_swap confirmed của 000000014831 bị thay bằng class_swap rejected; AI dùng đúng nguồn mới, không tự khôi phục dòng cũ hoặc suy ra category_swap từ ghi chú.
- CSV mới có 13 confirmed, 7 rejected (trước 15/5); errors.json có 24 lỗi = 11 luật + 13 confirmed (trước 26). Đối chiếu toàn bộ dòng gộp với các bản chuẩn hóa và tập errors với luật cộng confirmed đều khớp.
- Chạy bộ chấm học viên đúng một lần cho danh sách mới: F1 làm tròn tổng ≈0.8, luật ≈1.0, gán nhãn ≈0.6; các giá trị làm tròn chưa đổi so với lần trước. Không đọc đáp án hoặc dùng --truth-dir, không thay verdict theo điểm.
- Vẫn còn tám giả thuyết chưa có verdict riêng: class_swap của 000000014831 nay đã có rejected, nhưng category_swap của ảnh đó lại thiếu dòng riêng. Ảnh có cả lỗi luật và review confirmed giảm từ ba xuống hai: 000000007818, 000000009772. Chi tiết và so sánh trước/sau được lưu trong runs/r999/review_audit.md và review_audit.json.
- Không sửa tám CSV nguồn, rules, candidates hoặc script gốc; chưa commit/push. Cần người review xác minh các mục còn thiếu và việc thay thế dòng ở m6.

### Chạy lại cùng yêu cầu sau bản CSV bổ sung

Người dùng lặp lại cùng prompt gộp tám CSV, kiểm tra thiếu/trùng, tạo errors.json, chấm F1 và so sánh với lần trước ở mục ngay trên. Giữ nguyên yêu cầu không tự sửa kết luận, không sửa script gốc và chưa commit/push.

- Kiểm tra nguồn mới: đủ tám reviewer và 18/18 ảnh, 20 dòng có dữ liệu; không thiếu/thừa ảnh, không trùng cặp (image,type) hoặc ảnh giữa các file.
- Nguồn có ba dòng note chứa dấu phẩy chưa được quote (m1 dòng 3; m3 dòng 2 và 3) và hai bản ghi hoàn toàn trống ở m7 dòng 4–5. Chỉ chuẩn hóa quoting và bỏ bản ghi không có dữ liệu trên bản sao tạm; toàn bộ nội dung note, reviewer, type và verdict được giữ nguyên. Không sửa CSV nguồn.
- Tạo lại review_log.csv và errors.json, đối chiếu tất cả các trường dòng gộp với bản chuẩn hóa và tập lỗi với luật cộng confirmed. Kết quả mới: 11 confirmed, 9 rejected, 22 lỗi = 11 luật + 11 confirmed. Lần trước tương ứng là 13 confirmed, 7 rejected và 24 lỗi.
- Chạy bộ chấm học viên một lần sau thay đổi nguồn: F1 làm tròn tổng ≈0.9 (trước ≈0.8), luật ≈1.0 (trước ≈1.0), gán nhãn ≈0.7 (trước ≈0.6). Không dùng --truth-dir hoặc mở đáp án, không tự chỉnh verdict theo điểm.
- Các giả thuyết thiếu verdict riêng giảm từ tám xuống bảy, ảnh có cả lỗi luật và review confirmed giảm từ hai xuống không. missing_box của 000000001818 đã có confirmed. Ở 000000017178, nguồn đổi category_swap rejected thành class_swap rejected nên category_swap nay thiếu dòng; note vẫn nói YOLO ghi cow sai nên người review cần kiểm tra lại sự thống nhất.
- Chi tiết các mục còn thiếu, ghi chú chưa đủ quan sát và so sánh từng thay đổi được cập nhật trong runs/r999/review_audit.md/json. Sao lưu kết quả cũ trước khi ghi mới; không sửa scripts gốc và chưa commit/push.

## Prompt 9 — Bạch Đăng Ngọc Tuấn (TV3): Module đối chiếu chéo Detection ↔ Panoptic

Ngày: 19/11/2026. Công cụ: Antigravity. Prompt người dùng:

```text
Tôi là Bạch Đăng Ngọc Tuấn (TV3), nhóm 13, seed 999. Phụ trách Pha 2: Đối chiếu Detection ↔ Panoptic & Review ảnh.
Hãy đọc GUIDE.md, docs/DELIVERY.md, RUBRIC.md, submission/REVIEW_TOOL.md và PHAN_CONG_8_NGUOI.md.

Viết module validator/cross_check.py và tích hợp vào validator/validate.py để:
1. Đọc nhãn YOLO và mask Panoptic của cùng ảnh trong delivery/.
2. Bắt đủ 5 lỗi gán nhãn: class_swap, category_swap, bbox_drift, missing_box, instance_merge.
3. Xuất ra candidates.json đúng format yêu cầu của review_tool.py.
4. Tinh chỉnh ngưỡng trên lô sạch runs/clean để không bị báo động giả, giữ hàng đợi gọn nhẹ.
5. Kiểm thử trên seed 999 và lô sạch.
```

### Phạm vi AI đã làm và cách kiểm lại
- Đã đọc các tài liệu lab, định dạng lô bàn giao, và hợp đồng candidates trong `submission/REVIEW_TOOL.md`.
- Viết `validator/cross_check.py` và tích hợp cờ `--candidates` vào `validator/validate.py`.
- **Chỗ phát hiện sai sót & tinh chỉnh:**
  + Bản đầu dùng so sánh toàn bộ các cặp box-segment mà không qua ghép cặp, dẫn đến trên lô sạch bị báo động giả tới 32 ca (chủ yếu là `instance_merge` do người đứng gần nhau bị hiểu nhầm là gộp segment).
  + Bản đầu đọc `classes.txt` bằng `split()` thông thường khiến các lớp có dấu cách (như `potted plant`, `traffic light`, `wine glass`...) bị mất từ phía sau, dẫn đến việc không so khớp được với tên lớp trong Panoptic và bỏ sót lỗi `bbox_drift`.
  + Đã khắc phục: đọc tên lớp bằng `split(maxsplit=1)`, áp dụng thuật toán Greedy Bipartite Matching theo IoU giảm dần, chỉ gắn cờ `instance_merge` khi số lượng segment của lớp đó ít hơn số box detection.
- **Kết quả kiểm thử thực tế:**
  + Trên lô sạch (`runs/clean`, 50 ảnh): sinh đúng **0 ứng viên** (loại bỏ hoàn toàn nhiễu tự nhiên).
  + Trên lô luyện tập (`runs/r999`, 250 ảnh): sinh đúng **18 ứng viên**, bắt trọn vẹn **9/9 lỗi gán nhãn thật** (Recall = 100%).
  + Kiểm thử khớp nối với `tools/review_tool.py --check`: tool chia đều 18 ảnh cho 8 người (mỗi người 2-3 ảnh), TV3 nhận 2 ảnh (`000000001818` và `000000009772`), kết quả render 0 cảnh báo.
- Thành viên thật trực tiếp chạy tool xem 2 ảnh được chia và lưu vào `review_log_m3.csv`. Không dùng AI để thay việc xem ảnh thật.
