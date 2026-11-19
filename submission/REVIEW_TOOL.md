# Công cụ review — nhóm 13, seed 13007

Chạy từ thư mục gốc repo bằng Python 3.10+ trên Windows. Cài Python bản có Tcl/Tk (bản cài chuẩn từ python.org) và Pillow:

```powershell
py -m pip install "Pillow>=11"
```

## Luyện tập: thành viên 4

Sau khi thành viên phụ trách validator đã xuất `runs/r13007/candidates.json`:

```powershell
py -X utf8 scripts/review_tool.py --member 4 --reviewer "TV4"
```

Mặc định đọc `runs/r13007/delivery/`, ghi riêng `runs/r13007/review_log_m4.csv`. Thay `TV4` bằng họ tên hoặc mã thành viên thực tế. Không có candidates thì tool báo thiếu file, không tự sinh danh sách lỗi.

Các phần được đánh số **1–6**, chia vòng tròn theo tên ảnh đã sắp xếp. Số ảnh giữa hai phần chênh tối đa một; mọi giả thuyết cho cùng một ảnh thuộc cùng một phần. Nhóm có thể thống nhất **TV1–TV5 dùng phần 1–5, Lead dùng phần 6**. Nếu nhóm dùng cách đánh số khác, chỉ đổi `--member` tương ứng.

Sáu người phải dùng **cùng một phiên bản candidates.json**. Không đổi danh sách giữa chừng vì phần được chia có thể thay đổi. Mỗi người dùng CSV riêng, không cùng ghi một file qua ổ mạng.

## Cách dùng giao diện

1. Ba khung lần lượt là ảnh gốc, box YOLO màu vàng có tên lớp, và viền pixel segment panoptic. Chọn một khung trong hộp chọn để xem lớn hơn. Danh sách bên dưới ghi đầy đủ class, segment id, category id, crowd/stuff và cảnh báo file thiếu/hỏng. Viền không phải bbox của segment và không tô kín vật.
2. Dùng `+`, `-`, cuộn chuột, `100%` hoặc `Vua khung` để phóng ảnh. Kéo chuột trái hoặc dùng thanh cuộn để xem vùng ngoài khung. `Truoc`/`Sau` chuyển ảnh trong phần được chia.
3. Xem vật trong ảnh trước khi chọn `confirmed`/`rejected`. Ban đầu không chọn kết luận nào. Trường `Loai dang review` cho chọn một trong năm lỗi gán nhãn.
4. Nếu có nhiều loại nghi ngờ, xem và lưu từng loại. Nếu phát hiện nguồn sai khác giả thuyết ban đầu (ví dụ nghi `class_swap` nhưng ảnh cho thấy panoptic sai), lưu `rejected` cho giả thuyết ban đầu với lý do, rồi chọn `category_swap` và lưu `confirmed` với quan sát phù hợp. Tool không tự quyết định hoặc tự đổi các dòng còn lại.
5. Ghi chú phải có **ít nhất 20 ký tự mô tả**, chưa tính tên người xem. Tool thêm `[reviewer=...]` vào đầu note để giữ đúng bốn cột yêu cầu. Không dùng lại ghi chú chung cho mọi ảnh.
6. `Luu dong` hoặc `Ctrl+S` ghi ngay vào CSV; `Luu va anh sau` ghi rồi chuyển tiếp. Mở lại cùng lệnh sẽ đọc các dòng đã lưu, cho sửa quyết định hoặc ghi chú. Tool hỏi xử lý phần nhập chưa lưu trước khi đổi ảnh, đổi loại hoặc đóng cửa sổ. Thanh trạng thái đếm **ảnh có dòng đã lưu**, không chứng nhận đã xem đủ mọi loại của ảnh.

CSV UTF-8 không BOM, header chính xác `image,type,verdict,note`; image không có đuôi. CSV quoting bảo toàn dấu phẩy, dấu nháy, tiếng Việt và ghi chú nhiều dòng. Chỉ thao tác lưu có verdict, mô tả hợp lệ và người xem mới tạo một dòng. Tool không chốt `errors.json`.

## Gộp kết quả của sáu người

Sau khi mọi người review xong, tập hợp sáu file về cùng máy:

```powershell
py -X utf8 scripts/review_tool.py --merge runs/r13007/review_log_m1.csv runs/r13007/review_log_m2.csv runs/r13007/review_log_m3.csv runs/r13007/review_log_m4.csv runs/r13007/review_log_m5.csv runs/r13007/review_log_m6.csv --out runs/r13007/review_log.csv
```

Phần không có ảnh vẫn có thể xuất file CSV chỉ có header bằng nút lưu khi mở phần rỗng. Không thêm verdict giả để lấp phần rỗng. File trùng hoàn toàn được khử trùng theo `(image,type)`; cùng khóa nhưng khác verdict/note thì dừng, không ghi đè file tổng. Nhóm phải đối chiếu và thống nhất trước khi gộp lại. Không tự chọn đa số hoặc ưu tiên `confirmed`.

Sau đó dùng script có sẵn, khi `rules.json` đã được validator tạo:

```powershell
py -X utf8 scripts/merge_review.py --rules runs/r13007/rules.json --review runs/r13007/review_log.csv --out runs/r13007/errors.json
```

## Đề ẩn

Đề ẩn cần truyền rõ đường dẫn candidates và nơi lưu kết quả:

```powershell
py -X utf8 scripts/review_tool.py --delivery delivery --candidates submission/de_an/candidates.json --member 4 --reviewer "TV4" --out submission/de_an/review_log_m4.csv
```

Mỗi người thay số phần và tên file. Gộp tương tự lô luyện tập, với các file `submission/de_an/review_log_m1.csv` đến `review_log_m6.csv`, đầu ra `submission/de_an/review_log.csv`. Tên ảnh như `img_0001` được giữ nguyên, không suy luận từ số COCO hoặc seed.

## Hợp đồng với người viết candidates

Chấp nhận list trực tiếp, `{"candidates": [...]}` hoặc `{"errors": [...]}`. Mỗi phần tử có `image` hoặc `target` là chuỗi tên ảnh; `type` là một loại lỗi, hoặc `types` là danh sách các loại. Các trường bổ sung được bỏ qua. Ví dụ minh họa **không phải kết quả review**:

```json
{"candidates": [{"target": "img_0001", "types": ["class_swap", "category_swap"]}]}
```

Chỉ nhận `class_swap`, `category_swap`, `bbox_drift`, `missing_box`, `instance_merge`. Giữ số 0 đầu của tên ảnh bằng chuỗi JSON. Candidate phải có ảnh trong manifest. Không có danh sách tên ảnh hoặc đáp án theo seed trong code.

## Kiểm thử

```powershell
py -X utf8 -m unittest discover -s tests -p test_review_tool.py -v
py -X utf8 scripts/review_tool.py --check --member 4
py -X utf8 scripts/review_tool.py --member 4 --preview runs/r13007/review_preview_m4.png
```

Hai lệnh cuối cần candidates thật đã được xuất. `--check` render toàn bộ phần được chia và in cảnh báo kỹ thuật; `--preview` xuất ba khung của ảnh đầu tiên. Chúng không ghi review hoặc kết luận đúng/sai.

Test tự động chỉ tạo dữ liệu tổng hợp trong thư mục tạm, gồm tên ảnh đề ẩn, mask RGB có nhiều byte id, ảnh thiếu, mask sai kích thước, CSV tiếng Việt, chia sáu phần, gộp xung đột, tương thích `merge_review.py`, và thao tác Tkinter. Các verdict trong test là dữ liệu giả cho kiểm thử, không được chép vào bài nộp.

Đường dẫn đầu vào được chặn nếu chứa `_private`/`data_source` hoặc trỏ ra ngoài delivery qua manifest. Đầu ra CSV/preview bị chặn trong delivery; các lần lưu CSV dùng file tạm và thay thế nguyên tử. Tool không truy cập mạng, nguồn COCO hay bộ chấm đáp án.
