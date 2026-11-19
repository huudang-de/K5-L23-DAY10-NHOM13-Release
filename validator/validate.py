"""Validator của Nhóm 13:
- Tích hợp kiểm tra File & Detection (Nguyễn Văn Nhất - TV1)
- Tích hợp đối chiếu Detection ↔ Panoptic xuất candidates (Bạch Đăng Ngọc Tuấn - TV3)

Sử dụng:
  py -X utf8 validator/validate.py <delivery> --out <errors.json> [--candidates <candidates.json>]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

# Đảm bảo import được module nội bộ trong validator/
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

if __package__:
    from .file_detection import check_file_detection
    from .cross_check import find_candidates
else:
    from file_detection import check_file_detection
    from cross_check import find_candidates


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("delivery", type=Path, help="Đường dẫn đến thư mục delivery của lô bàn giao")
    parser.add_argument("--out", type=Path, required=True, help="Đường dẫn file JSON xuất lỗi (ví dụ: errors.json hoặc rules.json)")
    parser.add_argument("--candidates", type=Path, help="Đường dẫn file JSON xuất danh sách ứng viên đối chiếu (candidates.json)")
    args = parser.parse_args()

    delivery = args.delivery.resolve()
    if not delivery.is_dir():
        parser.error(f"Thư mục delivery không tồn tại: {delivery}")

    # 1. Chạy kiểm tra lỗi luật File & Detection (TV1)
    errors = check_file_detection(delivery)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({"errors": errors}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[Validator] Đã phát hiện {len(errors)} lỗi luật -> {args.out}")

    # 2. Chạy đối chiếu Detection ↔ Panoptic tìm ứng viên (TV3 - Ngọc Tuấn)
    if args.candidates:
        cand_result = find_candidates(delivery)
        args.candidates.parent.mkdir(parents=True, exist_ok=True)
        args.candidates.write_text(json.dumps(cand_result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        total_candidates = len(cand_result.get("candidates", []))
        print(f"[CrossCheck] Đã sinh {total_candidates} ứng viên nghi vấn -> {args.candidates}")


if __name__ == "__main__":
    main()
