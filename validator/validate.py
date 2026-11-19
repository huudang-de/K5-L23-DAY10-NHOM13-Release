"""Chạy các kiểm tra File & Detection và xuất lỗi theo định dạng của lab."""

import argparse
import json
from pathlib import Path

if __package__:
    from .file_detection import check_file_detection
else:
    from file_detection import check_file_detection


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("delivery", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    errors = check_file_detection(args.delivery)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({"errors": errors}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
