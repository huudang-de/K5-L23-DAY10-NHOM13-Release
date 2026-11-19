#!/usr/bin/env python3
"""Chạy toàn bộ các kiểm tra lỗi luật Pha 1 (File & Detection + Metadata & Panoptic) và xuất lỗi theo định dạng của lab."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import pngutil  # noqa: E402

if __package__:
    from .file_detection import check_file_detection
else:
    from file_detection import check_file_detection


def check_metadata(delivery_dir: Path) -> list[dict[str, str]]:
    """Kiểm tra lỗi luật phần Metadata:
    1. scene_leak: một cảnh (scene_id) có ảnh ở cả train và val (target là scene_id).
    2. guideline_mismatch: guideline_version của ảnh khác với guideline của job trong jobs.csv (target là tên ảnh).
    """
    errors: list[dict[str, str]] = []

    jobs_path = delivery_dir / "jobs.csv"
    metadata_path = delivery_dir / "metadata.json"

    if not jobs_path.is_file() or not metadata_path.is_file():
        return errors

    # Đọc guideline chuẩn của từng job từ jobs.csv
    job_guidelines: dict[str, str] = {}
    with jobs_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            job_id = row.get("job_id", "").strip()
            guideline = row.get("guideline", "").strip()
            if job_id:
                job_guidelines[job_id] = guideline

    # Đọc metadata.json
    meta_doc = json.loads(metadata_path.read_text(encoding="utf-8"))
    items = meta_doc.get("items", [])

    scene_splits: dict[str, set[str]] = defaultdict(set)

    for item in items:
        img_name = item.get("image", "").strip()
        scene_id = item.get("scene_id", "").strip()
        split = item.get("split", "").strip()
        job_id = item.get("job_id", "").strip()
        img_guideline = item.get("guideline_version", "").strip()

        if scene_id and split:
            scene_splits[scene_id].add(split)

        # Kiểm tra guideline_mismatch: so với guideline của job trong jobs.csv
        expected_guideline = job_guidelines.get(job_id)
        if expected_guideline is not None and img_guideline != expected_guideline:
            errors.append({"type": "guideline_mismatch", "target": img_name})

    # Kiểm tra scene_leak: một scene_id xuất hiện ở nhiều hơn 1 split (cả train và val)
    for scene_id, splits in sorted(scene_splits.items()):
        if len(splits) > 1:
            errors.append({"type": "scene_leak", "target": scene_id})

    return errors


def _count_mask_segments(mask_path: Path) -> Counter[int]:
    """Đếm số pixel thực tế của từng segment_id (> 0) trong file mask PNG."""
    _, _, pixels = pngutil.read_rgb(mask_path)
    # Tối ưu tốc độ đếm trên pure Python bằng cách gom bộ 3 byte (R, G, B)
    rgb_triplets = zip(pixels[0::3], pixels[1::3], pixels[2::3])
    triplet_counts = Counter(rgb_triplets)

    seg_counts: Counter[int] = Counter()
    for (r, g, b), count in triplet_counts.items():
        sid = r + (g << 8) + (b << 16)
        if sid != 0:
            seg_counts[sid] = count
    return seg_counts


def check_panoptic(delivery_dir: Path) -> list[dict[str, str]]:
    """Kiểm tra lỗi luật phần Panoptic:
    1. invalid_category_id: category_id trong segments_info không tồn tại trong danh sách categories.
    2. thing_overlap: area khai báo trong segments_info lớn hơn số pixel thực tế của segment trong mask PNG.
    """
    errors: list[dict[str, str]] = []

    panoptic_path = delivery_dir / "panoptic.json"
    if not panoptic_path.is_file():
        return errors

    pan_doc = json.loads(panoptic_path.read_text(encoding="utf-8"))
    categories = pan_doc.get("categories", [])
    valid_cat_ids = {c["id"] for c in categories if "id" in c}

    # Map image_id -> tên ảnh (stem không có đuôi)
    id_to_stem: dict[int, str] = {}
    for img in pan_doc.get("images", []):
        if "id" in img and "file_name" in img:
            id_to_stem[img["id"]] = Path(img["file_name"]).stem

    masks_dir = delivery_dir / "masks"

    for ann in pan_doc.get("annotations", []):
        file_name = ann.get("file_name", "")
        img_id = ann.get("image_id")
        target = Path(file_name).stem if file_name else id_to_stem.get(img_id, str(img_id))

        segments_info = ann.get("segments_info", [])

        # 1. Kiểm tra invalid_category_id
        has_invalid_cat = any(seg.get("category_id") not in valid_cat_ids for seg in segments_info)
        if has_invalid_cat:
            errors.append({"type": "invalid_category_id", "target": target})
            continue

        # 2. Kiểm tra thing_overlap (đếm pixel thực tế trong mask PNG rồi so với area)
        mask_path = masks_dir / Path(file_name).name if file_name else masks_dir / f"{target}.png"
        if not mask_path.is_file():
            continue

        actual_counts = _count_mask_segments(mask_path)
        has_overlap = False
        for seg in segments_info:
            sid = seg.get("id", 0)
            if sid == 0:
                continue
            declared_area = seg.get("area", 0)
            actual_area = actual_counts.get(sid, 0)
            if declared_area != actual_area:
                has_overlap = True
                break

        if has_overlap:
            errors.append({"type": "thing_overlap", "target": target})

    return errors


def validate(delivery_dir: Path) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Chạy toàn bộ kiểm tra lỗi luật Pha 1 trên thư mục delivery."""
    errors: list[dict[str, str]] = []
    errors.extend(check_file_detection(delivery_dir))
    errors.extend(check_metadata(delivery_dir))
    errors.extend(check_panoptic(delivery_dir))

    candidates: list[dict[str, str]] = []
    return errors, candidates


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("delivery", type=Path, help="Đường dẫn tới thư mục delivery")
    parser.add_argument("--out", type=Path, required=True, help="Đường dẫn file xuất errors.json")
    parser.add_argument("--candidates", type=Path, required=False, help="Đường dẫn file xuất candidates.json")
    args = parser.parse_args()

    if not args.delivery.is_dir():
        raise SystemExit(f"Thư mục delivery không tồn tại: {args.delivery}")

    errors, candidates = validate(args.delivery)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({"errors": errors}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if args.candidates is not None:
        args.candidates.parent.mkdir(parents=True, exist_ok=True)
        args.candidates.write_text(
            json.dumps({"candidates": candidates}, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
