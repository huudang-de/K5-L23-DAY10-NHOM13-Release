#!/usr/bin/env python3
"""Truy vết ticket của team AI (Pha 5): xuất trace.json gồm tier_a, tier_b, notify.

Tiêu chí lấy phiên bản guideline theo jobs.csv (không lấy theo metadata.json của ảnh).
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def build_trace(
    delivery: Path,
    scenes: set[str],
    class_name: str,
    old_guideline: str = "v1.2",
) -> dict:
    class_ids = {}
    for line in (delivery / "classes.txt").read_text(encoding="utf-8").splitlines():
        if line.strip():
            cid, cname = line.strip().split(None, 1)
            class_ids[cname.strip()] = int(cid)

    if class_name not in class_ids:
        raise SystemExit(f"Không tìm thấy lớp '{class_name}' trong {delivery / 'classes.txt'}")
    target_cid = class_ids[class_name]

    jobs = {}
    with (delivery / "jobs.csv").open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            jobs[row["job_id"].strip()] = {
                "annotator": row["annotator"].strip(),
                "reviewer": row["reviewer"].strip(),
                "guideline": row["guideline"].strip(),
            }

    meta_doc = json.loads((delivery / "metadata.json").read_text(encoding="utf-8"))
    tier_a: list[str] = []
    tier_b: list[str] = []
    notify: set[str] = set()

    for item in meta_doc.get("items", []):
        img = item["image"].strip()
        job_id = item["job_id"].strip()
        scene_id = item["scene_id"].strip()
        job = jobs.get(job_id)
        if not job or job["guideline"] != old_guideline:
            continue

        label_path = delivery / "labels" / f"{img}.txt"
        if not label_path.is_file():
            continue

        has_class = False
        for line in label_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            cid = int(float(line.split()[0]))
            if cid == target_cid:
                has_class = True
                break

        if not has_class:
            continue

        if scene_id in scenes:
            tier_a.append(img)
        else:
            tier_b.append(img)
        notify.add(job["annotator"])
        notify.add(job["reviewer"])

    return {
        "tier_a": sorted(tier_a),
        "tier_b": sorted(tier_b),
        "notify": sorted(notify),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--delivery", type=Path, required=True)
    ap.add_argument("--scenes", required=True, help="Danh sách scene_id cách nhau dấu phẩy")
    ap.add_argument("--class-name", required=True)
    ap.add_argument("--old-guideline", default="v1.2")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    scenes = {s.strip() for s in args.scenes.split(",") if s.strip()}
    trace = build_trace(args.delivery, scenes, args.class_name, args.old_guideline)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(trace, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {args.out}: tier_a={len(trace['tier_a'])}, tier_b={len(trace['tier_b'])}, notify={len(trace['notify'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
