# Bảo mật khi làm việc

> Áp dụng cho lô `lab250_96113fd7fec7` (seed `999`).

## 1. Ca USB: hết giờ, muốn chép lô về nhà làm tiếp
- **Không** chép dữ liệu lô (`images/`, `labels/`, `masks/`) ra USB, **không** gửi qua email cá nhân/Zalo/Drive cá nhân và **không** nhờ người ngoài làm hộ, vì dữ liệu dự án thuộc quyền kiểm soát nội bộ — mang ra ngoài thiết bị công ty làm mất kiểm soát truy cập, lộ dữ liệu và mất dấu audit.
- **Cách làm đúng:** Dừng công việc tại thời điểm hết giờ, lưu tiến độ trên hệ thống nội bộ / máy trạm được cấp quyền (như `review_log` trên workspace quản lý), hoặc xin gia hạn / làm qua kết nối bảo mật (VPN/VDI) được công ty phê duyệt.

## 2. Năm việc: được hay không
1. **Mở job được giao trên máy công ty:** **ĐƯỢC** — đúng phạm vi công việc và môi trường kiểm soát.
2. **Chụp màn hình gửi người quen:** **KHÔNG** — rò rỉ dữ liệu hình ảnh nội bộ ra ngoài, có thể chứa PII (khuôn mặt, biển số).
3. **Chép lô ra USB:** **KHÔNG** — sao chép dữ liệu ra thiết bị lưu trữ cá nhân không kiểm soát, dễ thất lạc/lộ lọt.
4. **Dán nhãn/ảnh thật lên chatbot AI công cộng:** **KHÔNG** — dữ liệu dự án thật gửi lên dịch vụ bên thứ ba có thể bị lưu/huấn luyện ngoài tầm kiểm soát (chỉ ảnh COCO công khai trong lab này mới được dùng minh họa và phải ghi vào `prompts.md`).
5. **Đưa tài khoản CVAT cho đồng nghiệp:** **KHÔNG** — vi phạm nguyên tắc định danh cá nhân; mọi thao tác gán/kiểm nhãn phải gắn đúng người làm để còn truy vết (`notify`, audit).

## 3. Ca khuôn mặt: thấy mặt người rõ trong lô, guideline yêu cầu làm mờ
- **Hành động & trạng thái lô:** Lập tức **Hold** lô (không bàn giao/train tiếp) và **báo ngay cho người phụ trách dữ liệu / PM / Data Steward** (kèm mã lô `lab250_96113fd7fec7` và danh sách ảnh).
- **Vì sao không tự làm mờ hay xoá ảnh:** Tự ý sửa pixel ảnh sẽ làm sai lệch dữ liệu gốc, đổi `sha256` trong `manifest.json` (gây `wrong_hash`), và tự ý xoá ảnh sẽ làm mất đồng bộ với `manifest.json` / `panoptic.json` / `rework_queue.csv`. Mọi bước làm mờ PII phải do pipeline tiền xử lý có kiểm soát thực hiện trước khi phát hành lại lô mới.
- **Ví dụ ảnh có người trong lô `r999`:** Trong lô có `139/250` ảnh chứa lớp `person`, ví dụ `000000000139.jpg`, `000000000785.jpg`, `000000000872.jpg`.
