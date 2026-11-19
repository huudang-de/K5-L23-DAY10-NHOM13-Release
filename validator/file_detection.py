"""Kiểm tra file ảnh và nhãn YOLO trong một lô bàn giao."""

import hashlib
import json
import math
from pathlib import Path


# Nhãn YOLO ghi 6 chữ số thập phân. Sai số ở mép gồm sai số tâm
# (0.5e-6) và một nửa sai số chiều rộng/cao (0.25e-6).
EDGE_ROUNDING = 0.75e-6 + 1e-12
CENTER_ROUNDING = 1e-6 + 1e-12


def _delivery_path(delivery: Path, relative: str) -> Path:
    path = (delivery / relative).resolve()
    if not path.is_relative_to(delivery):
        raise ValueError(f"Đường dẫn nằm ngoài delivery: {relative}")
    return path


def _out_of_bounds(x: float, y: float, w: float, h: float) -> bool:
    return (
        not all(math.isfinite(value) for value in (x, y, w, h))
        or w <= 0
        or h <= 0
        or min(x - w / 2, y - h / 2) < -EDGE_ROUNDING
        or max(x + w / 2, y + h / 2) > 1 + EDGE_ROUNDING
    )


def check_file_detection(delivery: Path) -> list[dict[str, str]]:
    """Trả về các cặp type/target duy nhất để ghép vào validator chung."""
    delivery = delivery.resolve()
    manifest = json.loads(_delivery_path(delivery, "manifest.json").read_text(encoding="utf-8"))
    panoptic = json.loads(_delivery_path(delivery, "panoptic.json").read_text(encoding="utf-8"))
    dimensions = {
        Path(image["file_name"]).name: (image["width"], image["height"])
        for image in panoptic["images"]
    }
    findings = set()

    for target, item in manifest["items"].items():
        image = _delivery_path(delivery, item["image"])
        if not image.is_file():
            findings.add(("missing_image", target))
            continue
        if hashlib.sha256(image.read_bytes()).hexdigest() != item["image_sha256"].lower():
            findings.add(("wrong_hash", target))

        image_width, image_height = dimensions[Path(item["image"]).name]
        max_dx = 2 / image_width + CENTER_ROUNDING
        max_dy = 2 / image_height + CENTER_ROUNDING
        centers = {}
        labels = _delivery_path(delivery, item["label"]).read_text(encoding="utf-8")
        for line in labels.splitlines():
            if not line.strip():
                continue
            class_id, x, y, w, h = map(float, line.split())
            valid_class = class_id.is_integer() and 0 <= class_id < 80
            invalid_box = _out_of_bounds(x, y, w, h)
            if not valid_class:
                findings.add(("invalid_class", target))
            if invalid_box:
                findings.add(("bbox_out_of_bounds", target))
            if not valid_class or invalid_box:
                continue

            same_size = centers.setdefault((class_id, w, h), [])
            if any(abs(x - px) <= max_dx and abs(y - py) <= max_dy for px, py in same_size):
                findings.add(("duplicate_box", target))
            same_size.append((x, y))

    return [{"type": kind, "target": target} for kind, target in sorted(findings)]
