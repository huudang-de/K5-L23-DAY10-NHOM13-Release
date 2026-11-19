# Validator của nhóm

Viết `validate.py` ở đây. Giao diện cố định:

```
python validator/validate.py <thư_mục_delivery> --out <errors.json> [--candidates <candidates.json>]
```

Chỉ đọc thư mục delivery được truyền vào; chỉ thư viện chuẩn; không mạng. Xem [GUIDE.md](../GUIDE.md) Pha 1–2 và [RULES.md](../RULES.md).

## Bàn giao File & Detection

- **TV2:** Gọi `check_file_detection(delivery: Path)` trong `file_detection.py` từ CLI chung. Hàm trả về danh sách `{"type": ..., "target": ...}`, với `target` là tên ảnh bỏ đuôi. Gộp với 4 luật Metadata & Panoptic, rồi xuất một đối tượng `{"errors": [...]}` qua `--out`.
- **TV3:** Bổ sung `--candidates` vào CLI chung. Xuất các ứng viên đối chiếu ra file riêng để TV4 chia ảnh và tổng hợp review.
- **TV4:** Dùng `rules.json` đủ 9 luật từ CLI đã tích hợp và `review_log.csv` để tạo `errors.json` cuối bằng `scripts/merge_review.py`.

CLI hiện tại chạy riêng 5 luật File & Detection. Có thể kiểm tra lại trên seed nhóm bằng:

```powershell
python -X utf8 validator/validate.py runs/r999/delivery --out runs/r999/rules.json
```

Kết quả kiểm tra phần này: 6 phát hiện trên seed 999, 7 trên seed bổ sung 11 và 0 trên lô sạch 50 ảnh. Đây là số phát hiện, chưa phải F1 của validator tích hợp.
