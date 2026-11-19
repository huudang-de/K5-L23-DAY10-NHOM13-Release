Release: lab250_96113fd7fec7_v2
Parent: lab250_96113fd7fec7
Số ảnh: 237
Số nhãn: 1645
Guideline: v1.2 (J01-J04), v1.3 (J05-J10)
QC v1: 22/250 = 8,8%
Kết luận v1: Hold — 8.8% ảnh/cảnh có lỗi, vượt ngưỡng 2%
Kết luận v2: Release — còn 0/237 ảnh có lỗi nhãn detection đã biết (đã tách 13 ảnh sang rework, sửa split/hash/guideline); 4/237 ảnh chỉ lỗi panoptic, không ảnh hưởng nhãn detection
Ghi chú: Đã tách 13 ảnh sang rework_queue.csv (giao lại đúng người gán/kiểm theo jobs.csv); nhãn các ảnh còn lại chép nguyên từ v1, không sửa tay. Split: đưa cả cảnh về một split (theo split đa số của cảnh) để ảnh gần giống nhau không vừa ở train vừa ở val làm điểm val ảo, cho 1 cảnh rò train/val: scene_124. Hash: 2 ảnh wrong_hash đã được Nguyen Huu Dang mở xem, ảnh còn nguyên (chỉ manifest v1 ghi sai) nên manifest.csv ghi sha256 mới (000000015956, 000000022705); 0 ảnh hỏng đưa vào rework (không có). Guideline: truyvet.csv lấy guideline theo job trong jobs.csv, vì job quyết định quy tắc người gán đã dùng; sửa 2 ảnh ghi sai guideline (000000001584, 000000003255). Lỗi chỉ ở panoptic (nhãn detection vẫn đúng nên ảnh ở lại v2), báo team panoptic: 000000002685 (instance_merge), 000000005477 (thing_overlap), 000000008211 (thing_overlap), 000000010707 (category_swap).
