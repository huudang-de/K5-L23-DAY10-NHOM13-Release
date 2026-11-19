# Dùng AI

| # | Ai dùng | Công cụ | Prompt (tóm tắt) | AI sai ở đâu | Nhóm kiểm lại thế nào |
|---|---|---|---|---|---|
| 1 | Thành viên 4, nhóm 13, seed 13007 | Codex | Đọc bốn tài liệu lab; viết tool Python/Pillow review ảnh YOLO/Panoptic, chia sáu người, ghi CSV, hỗ trợ luyện tập/đề ẩn; kiểm thử và ghi prompt. Toàn văn bên dưới. | Rà soát phát hiện bản đầu chưa hỗ trợ xuất CSV chỉ có header khi phần được chia không có ảnh; đã bổ sung thao tác lưu phần rỗng và kiểm thử hồi quy. | AI đã chạy 19 kiểm thử tự động bằng fixture tổng hợp, gồm GUI Tkinter và tương thích merge_review.py; render 250 ảnh delivery và so SHA-256 của 758 file trước/sau. Thành viên thật vẫn phải trực tiếp xem ảnh và tự kết luận; chưa có review thật trong phiên này. |
| 2 | Thành viên 4, nhóm 13, seed 13007 | Codex | Đọc PHAN_CONG_8_NGUOI.md; đổi mặc định sang tám người, thêm --members, cập nhật hướng dẫn và kiểm thử. Toàn văn bên dưới. | Chưa phát hiện lỗi trong lần chạy 24 kiểm thử; đã đối chiếu để bỏ các giới hạn sáu người trong code và hướng dẫn hiện hành. | Kiểm tra mặc định tám phần, tùy chỉnh 1/2/3/6/8/10/12 phần, tính đủ/không trùng/cân bằng, biên CLI, GUI theo số thành viên và gộp CSV của 6/8/10 người. |
| 3 | Thành viên 4, nhóm 13, seed 999 | Codex | Đổi seed mặc định từ 13007 sang 999, giữ tám người, cập nhật đường dẫn, hướng dẫn và kiểm thử. Toàn văn bên dưới. | Chưa phát hiện lỗi qua 26 kiểm thử; đã kiểm tra đường dẫn đầu vào/đầu ra theo seed mới và không dùng dữ liệu seed cũ khi thiếu candidates. | 26/26 kiểm thử đạt; render 250 ảnh r999, so SHA-256 của 758 file delivery trước/sau đều không đổi. |
| 4 | Nguyễn Văn Nhất | Codex | Rà soát phân công, viết và kiểm tra validator cho 5 lỗi File & Detection trước khi commit. Chi tiết ở Prompt 4. | Lần đầu chạy `run_lab.py`, `-X utf8` chỉ áp dụng cho tiến trình cha. Tiến trình con báo lỗi mã hóa khi in tiếng Việt sau khi tạo lô. | Đã kiểm 16 ca giả lập và chạy CLI trên seed 999, seed bổ sung 11 và lô sạch 50 ảnh. Validator báo lần lượt 6, 7 và 0 phát hiện File & Detection. |

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
