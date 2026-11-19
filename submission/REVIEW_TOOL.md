# Công cụ review — nhóm 13, seed 999

Theo `PHAN_CONG_8_NGUOI.md`, nhóm gồm **Lead + 7 thành viên**. Tool mặc định chia **8 phần**, có thể đổi bằng `--members`.

Chạy từ thư mục gốc repo bằng Python 3.10+ trên Windows. Cài Python bản có Tcl/Tk (bản cài chuẩn từ python.org) và Pillow:

```powershell
py -m pip install "Pillow>=11"
```

## Luyện tập: thành viên 4

Sau khi thành viên phụ trách validator đã xuất `runs/r999/candidates.json`:

```powershell
py -X utf8 scripts/review_tool.py --members 8 --member 4 --reviewer "leminhthang96"
```

Mặc định đọc `runs/r999/delivery/`, ghi riêng `runs/r999/review_log_m4.csv`. Thay tên người xem bằng họ tên hoặc mã thành viên thực tế. Không có candidates thì tool báo thiếu file, không tự sinh danh sách lỗi.

Tool tự tìm candidates ở `runs/r999/candidates.json`. Đường dẫn mặc định tính từ vị trí repo, giữ seed **999** và tổng **8 người**; `--delivery`, `--candidates`, `--out` vẫn cho phép chỉ định một lô khác hoặc đề ẩn. Giữ log của các seed khác ở thư mục riêng khi chuyển lô.

Các phần được đánh số **1–8**, chia vòng tròn theo tên ảnh đã sắp xếp. Số ảnh giữa hai phần chênh tối đa một; mọi giả thuyết cho cùng một ảnh thuộc cùng một phần. Nhóm có thể thống nhất **TV1–TV7 dùng phần 1–7, Lead dùng phần 8**. Nếu nhóm dùng cách đánh số khác, chỉ đổi `--member` tương ứng. Ví dụ Lead:

```powershell
py -X utf8 scripts/review_tool.py --members 8 --member 8 --reviewer "huudang-de"
```

Cả tám người phải dùng **cùng một phiên bản candidates.json và cùng giá trị --members**. Không đổi danh sách hoặc số thành viên giữa chừng vì phần được chia sẽ thay đổi. Mỗi người dùng CSV riêng, không cùng ghi một file qua ổ mạng.

## Tùy chỉnh số thành viên

`--members N` là tổng số phần/người, phải là số nguyên **>=1** (mặc định **8**). `--member M` là phần đang mở, phải từ **1 đến N** (mặc định **4**). Hai tham số áp dụng cho cả GUI, `--check` và `--preview`; tiêu đề và thanh trạng thái GUI hiển thị đúng `M/N`. Đầu ra mặc định vẫn là `review_log_mM.csv`.

Ví dụ giữ cách chia cũ cho 6 người, hoặc chia cho 10 người:

```powershell
py -X utf8 scripts/review_tool.py --members 6 --member 4 --reviewer "leminhthang96"
py -X utf8 scripts/review_tool.py --members 10 --member 10 --reviewer "Nguoi10"
```

Nếu nhóm đã bắt đầu review với 6 phần, dùng `--members 6` để tiếp tục đúng cách chia cũ. Khi chuyển sang 8 phần, giữ các log cũ để đối chiếu, thống nhất lại phân công và dùng file mới (ví dụ `--out runs/r999/review_log_8_m4.csv`); tool không tự phân lại các kết luận đã lưu. Lệnh gộp phải dùng đúng bộ file mà nhóm đã thống nhất.

## Cách dùng giao diện

1. Ba khung lần lượt là ảnh gốc, box YOLO màu vàng có tên lớp, và viền pixel segment panoptic. Chọn một khung trong hộp chọn để xem lớn hơn. Danh sách bên dưới ghi đầy đủ class, segment id, category id, crowd/stuff và cảnh báo file thiếu/hỏng. Viền không phải bbox của segment và không tô kín vật.
2. Dùng `+`, `-`, cuộn chuột, `100%` hoặc `Vua khung` để phóng ảnh. Kéo chuột trái hoặc dùng thanh cuộn để xem vùng ngoài khung. `Truoc`/`Sau` chuyển ảnh trong phần được chia.
3. Xem vật trong ảnh trước khi chọn `confirmed`/`rejected`. Ban đầu không chọn kết luận nào. Trường `Loai dang review` cho chọn một trong năm lỗi gán nhãn.
4. Nếu có nhiều loại nghi ngờ, xem và lưu từng loại. Nếu phát hiện nguồn sai khác giả thuyết ban đầu (ví dụ nghi `class_swap` nhưng ảnh cho thấy panoptic sai), lưu `rejected` cho giả thuyết ban đầu với lý do, rồi chọn `category_swap` và lưu `confirmed` với quan sát phù hợp. Tool không tự quyết định hoặc tự đổi các dòng còn lại.
5. Ghi chú phải có **ít nhất 20 ký tự mô tả**, chưa tính tên người xem. Tool thêm `[reviewer=...]` vào đầu note để giữ đúng bốn cột yêu cầu. Không dùng lại ghi chú chung cho mọi ảnh.
6. `Luu dong` hoặc `Ctrl+S` ghi ngay vào CSV; `Luu va anh sau` ghi rồi chuyển tiếp. Mở lại cùng lệnh sẽ đọc các dòng đã lưu, cho sửa quyết định hoặc ghi chú. Tool hỏi xử lý phần nhập chưa lưu trước khi đổi ảnh, đổi loại hoặc đóng cửa sổ. Thanh trạng thái đếm **ảnh có dòng đã lưu**, không chứng nhận đã xem đủ mọi loại của ảnh.

CSV UTF-8 không BOM, header chính xác `image,type,verdict,note`; image không có đuôi. CSV quoting bảo toàn dấu phẩy, dấu nháy, tiếng Việt và ghi chú nhiều dòng. Chỉ thao tác lưu có verdict, mô tả hợp lệ và người xem mới tạo một dòng. Tool không chốt `errors.json`.

## Gộp kết quả của tám người

Sau khi mọi người review xong, tập hợp tám file về cùng máy:

```powershell
py -X utf8 scripts/review_tool.py --merge runs/r999/review_log_m1.csv runs/r999/review_log_m2.csv runs/r999/review_log_m3.csv runs/r999/review_log_m4.csv runs/r999/review_log_m5.csv runs/r999/review_log_m6.csv runs/r999/review_log_m7.csv runs/r999/review_log_m8.csv --out runs/r999/review_log.csv
```

Phần không có ảnh vẫn có thể xuất file CSV chỉ có header bằng nút lưu khi mở phần rỗng. Không thêm verdict giả để lấp phần rỗng. File trùng hoàn toàn được khử trùng theo `(image,type)`; cùng khóa nhưng khác verdict/note thì dừng, không ghi đè file tổng. Nhóm phải đối chiếu và thống nhất trước khi gộp lại. Không tự chọn đa số hoặc ưu tiên `confirmed`.

`--merge` nhận danh sách CSV bất kỳ, không giới hạn tám file; với nhóm N người, truyền đủ bộ log của N phần, kể cả file chỉ có header. Theo phân công mới, TV4 + TV7 + Lead rà soát ghi chú trước khi chốt.

Sau đó dùng script có sẵn, khi `rules.json` đã được validator tạo:

```powershell
py -X utf8 scripts/merge_review.py --rules runs/r999/rules.json --review runs/r999/review_log.csv --out runs/r999/errors.json
```

## Đề ẩn

Đề ẩn cần truyền rõ đường dẫn candidates và nơi lưu kết quả:

```powershell
py -X utf8 scripts/review_tool.py --delivery delivery --candidates submission/de_an/candidates.json --members 8 --member 4 --reviewer "leminhthang96" --out submission/de_an/review_log_m4.csv
```

Mỗi người thay số phần và tên file. Gộp tương tự lô luyện tập, với các file `submission/de_an/review_log_m1.csv` đến `review_log_m8.csv`, đầu ra `submission/de_an/review_log.csv`. Tên ảnh như `img_0001` được giữ nguyên, không suy luận từ số COCO hoặc seed.

## Hợp đồng với người viết candidates

Chấp nhận list trực tiếp, `{"candidates": [...]}` hoặc `{"errors": [...]}`. Mỗi phần tử có `image` hoặc `target` là chuỗi tên ảnh; `type` là một loại lỗi, hoặc `types` là danh sách các loại. Các trường bổ sung được bỏ qua. Ví dụ minh họa **không phải kết quả review**:

```json
{"candidates": [{"target": "img_0001", "types": ["class_swap", "category_swap"]}]}
```

Chỉ nhận `class_swap`, `category_swap`, `bbox_drift`, `missing_box`, `instance_merge`. Giữ số 0 đầu của tên ảnh bằng chuỗi JSON. Candidate phải có ảnh trong manifest. Không có danh sách tên ảnh hoặc đáp án theo seed trong code.

## Kiểm thử

```powershell
py -X utf8 -m unittest discover -s tests -p test_review_tool.py -v
py -X utf8 scripts/review_tool.py --members 8 --check --member 4
py -X utf8 scripts/review_tool.py --members 8 --member 4 --preview runs/r999/review_preview_m4.png
```

Hai lệnh cuối cần candidates thật đã được xuất. `--check` render toàn bộ phần được chia và in cảnh báo kỹ thuật; `--preview` xuất ba khung của ảnh đầu tiên. Chúng không ghi review hoặc kết luận đúng/sai.

Test tự động chỉ tạo dữ liệu tổng hợp trong thư mục tạm, gồm tên ảnh đề ẩn, mask RGB có nhiều byte id, ảnh thiếu, mask sai kích thước, CSV tiếng Việt, chia mặc định tám phần và tùy chỉnh 1/2/3/6/8/10/12 phần, gộp xung đột, tương thích `merge_review.py`, và thao tác Tkinter. Có kiểm tra tham số ngoài phạm vi, phần rỗng, tiêu đề/trạng thái GUI theo số thành viên, đường dẫn mặc định seed 999 và báo thiếu candidates không tự tìm sang seed cũ. **26/26 kiểm thử đạt** khi cập nhật seed 999, nhóm tám người. Các verdict trong test là dữ liệu giả cho kiểm thử, không được chép vào bài nộp.

Đường dẫn đầu vào được chặn nếu chứa `_private`/`data_source` hoặc trỏ ra ngoài delivery qua manifest. Đầu ra CSV/preview bị chặn trong delivery; các lần lưu CSV dùng file tạm và thay thế nguyên tử. Tool không truy cập mạng, nguồn COCO hay bộ chấm đáp án.
