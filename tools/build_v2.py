#!/usr/bin/env python3
"""TV5 — Dựng lô bàn giao v2 từ lô v1 + errors.json (KHÔNG sửa delivery/ của v1).

  python3 tools/build_v2.py --run runs/r999                       # macOS/Linux
  py -X utf8 tools/build_v2.py --run runs/r999                    # Windows PowerShell
  python3 tools/build_v2.py --run runs/r999 --broken-hash 000000001234   # ảnh wrong_hash đã mở xem và thấy hỏng

Đọc:  <run>/delivery/ (v1, chỉ đọc) và <run>/errors.json (lỗi đã chốt của nhóm).
Ghi:  <run>/handover/<release_id>_v2/ gồm images/, labels/, rework_queue.csv, manifest.csv,
      label_summary.csv, truyvet.csv, README.txt.

Quy tắc (GUIDE Pha 4):
- Lỗi nhãn detection hoặc thiếu file -> rework_queue.csv, ảnh rời v2.
- wrong_hash -> mở ảnh kiểm: còn nguyên thì giữ, manifest ghi hash mới; hỏng thì rework.
- guideline_mismatch -> sửa trong truyvet.csv: guideline lấy theo job (jobs.csv).
- scene_leak -> đưa cả cảnh về một split (split chiếm đa số trong cảnh; hoà thì train).
- Lỗi chỉ ở panoptic -> ảnh ở lại v2, liệt kê trong README để báo team panoptic.
Nhãn được chép nguyên byte, không sửa tay.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from collections import Counter, defaultdict
from pathlib import Path

DET_REWORK = {"missing_image", "invalid_class", "bbox_out_of_bounds", "duplicate_box",
              "class_swap", "bbox_drift", "missing_box"}
PANOPTIC_ONLY = {"invalid_category_id", "thing_overlap", "category_swap", "instance_merge"}
THRESHOLD = 0.02  # Day 7: > 2% ảnh lỗi thì không Release

ACTION = {
    "missing_image": "giao lại file ảnh còn thiếu rồi kiểm lại nhãn",
    "invalid_class": "gán lại class_id hợp lệ (0-79)",
    "bbox_out_of_bounds": "vẽ lại box nằm trong ảnh",
    "duplicate_box": "xoá box lặp",
    "class_swap": "sửa lớp của box theo vật thật trong ảnh",
    "bbox_drift": "vẽ lại box khít vật",
    "missing_box": "gán box cho vật còn thiếu",
    "wrong_hash": "file ảnh hỏng: giao lại ảnh gốc và kiểm nhãn",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jpeg_intact(path: Path) -> bool:
    """Kiểm cấu trúc tối thiểu của JPEG (SOI ở đầu, EOI ở cuối). Vẫn phải MỞ ẢNH XEM bằng mắt."""
    data = path.read_bytes()
    return len(data) > 4 and data[:2] == b"\xff\xd8" and data.rstrip(b"\x00")[-2:] == b"\xff\xd9"


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, header: list[str], rows: list[list]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def job_ranges(jobs: dict) -> str:
    by_ver = defaultdict(list)
    for jid in sorted(jobs):
        by_ver[jobs[jid]["guideline"]].append(jid)
    parts = []
    for ver in sorted(by_ver):
        ids = by_ver[ver]
        parts.append(f"{ver} ({ids[0]}-{ids[-1]})" if len(ids) > 1 else f"{ver} ({ids[0]})")
    return ", ".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser(description="Dựng lô bàn giao v2")
    ap.add_argument("--run", required=True, help="thư mục run, ví dụ runs/r999")
    ap.add_argument("--errors", help="mặc định <run>/errors.json")
    ap.add_argument("--broken-hash", default="", help="tên ảnh wrong_hash đã mở xem và thấy hỏng, cách nhau dấu phẩy")
    ap.add_argument("--v2-decision", default="Release", choices=["Release", "Hold", "Rework"],
                    help="kết luận v2 do nhóm chốt (mặc định Release)")
    ap.add_argument("--hash-checked-by", default="", help="tên người đã MỞ XEM các ảnh wrong_hash (ghi vào README)")
    args = ap.parse_args()

    run = Path(args.run)
    d = run / "delivery"
    rid = json.loads((d / "release.json").read_text(encoding="utf-8"))["release_id"]
    man = json.loads((d / "manifest.json").read_text(encoding="utf-8"))["items"]
    meta = {m["image"]: m for m in json.loads((d / "metadata.json").read_text(encoding="utf-8"))["items"]}
    jobs = {row["job_id"]: row for row in read_csv(d / "jobs.csv")}
    names80 = [ln.split(" ", 1)[1].strip() for ln in (d / "classes.txt").read_text(encoding="utf-8").splitlines() if ln.strip()]
    errors = json.loads(Path(args.errors or run / "errors.json").read_text(encoding="utf-8"))["errors"]
    err_by_img = {e["target"]: e["type"] for e in errors if e["target"] in man}
    leak_scenes = {e["target"] for e in errors if e["type"] == "scene_leak"}
    broken = {s.strip() for s in args.broken_hash.split(",") if s.strip()}

    # 1. Phân loại ảnh
    rework, hash_ok, hash_bad, panoptic_only = [], [], [], []
    for name in sorted(man):
        t = err_by_img.get(name)
        if t in DET_REWORK:
            rework.append((name, t))
        elif t == "wrong_hash":
            img = d / man[name]["image"]
            if name in broken or not img.is_file() or not jpeg_intact(img):
                hash_bad.append(name)
                rework.append((name, t))
            else:
                hash_ok.append(name)
        elif t in PANOPTIC_ONLY:
            panoptic_only.append((name, t))
    rq = {n for n, _ in rework}
    keep = [n for n in sorted(man) if n not in rq and (d / man[n]["image"]).is_file()]

    # 2. Sửa split theo cảnh: đa số trong cảnh, hoà thì train
    by_scene = defaultdict(list)
    for name in man:
        by_scene[meta[name]["scene_id"]].append(meta[name]["split"])
    scene_split = {}
    for sc, splits in by_scene.items():
        c = Counter(splits)
        scene_split[sc] = "train" if c["train"] >= c["val"] else "val"
    leak_found = sorted(sc for sc, s in by_scene.items() if len(set(s)) > 1)

    # 3. Ghi thư mục v2 (xoá bản v2 cũ nếu chạy lại; KHÔNG đụng delivery/)
    v2 = run / "handover" / f"{rid}_v2"
    if v2.exists():
        shutil.rmtree(v2)
    (v2 / "images").mkdir(parents=True)
    (v2 / "labels").mkdir()
    for n in keep:
        shutil.copyfile(d / man[n]["image"], v2 / "images" / f"{n}.jpg")
        shutil.copyfile(d / man[n]["label"], v2 / "labels" / f"{n}.txt")

    write_csv(v2 / "rework_queue.csv", ["image", "type", "annotator", "reviewer", "action"],
              [[n, t, jobs[meta[n]["job_id"]]["annotator"], jobs[meta[n]["job_id"]]["reviewer"], ACTION[t]] for n, t in rework])

    files = sorted(p for sub in ("images", "labels") for p in (v2 / sub).iterdir() if p.is_file())
    write_csv(v2 / "manifest.csv", ["file", "sha256"], [[p.relative_to(v2).as_posix(), sha(p)] for p in files])

    counts = Counter()
    for n in keep:
        for ln in (v2 / "labels" / f"{n}.txt").read_text(encoding="utf-8").splitlines():
            if ln.strip():
                counts[int(float(ln.split()[0]))] += 1
    n_labels = sum(counts.values())
    write_csv(v2 / "label_summary.csv", ["class", "count"],
              [[names80[c], counts[c]] for c in sorted(counts)] + [["TOTAL", n_labels]])

    write_csv(v2 / "truyvet.csv", ["image", "scene_id", "split", "job_id", "annotator", "reviewer", "guideline"],
              [[n, meta[n]["scene_id"], scene_split[meta[n]["scene_id"]], meta[n]["job_id"],
                jobs[meta[n]["job_id"]]["annotator"], jobs[meta[n]["job_id"]]["reviewer"], jobs[meta[n]["job_id"]]["guideline"]]
               for n in keep])

    # 4. README.txt
    n_err = len({e["target"] for e in errors})
    rate = n_err / len(man)
    v1 = (f"Hold — {rate:.1%} ảnh/cảnh có lỗi, vượt ngưỡng 2%" if rate > THRESHOLD
          else f"Release — {rate:.1%} ảnh/cảnh có lỗi, không vượt ngưỡng 2%")
    gm = sorted(n for n, t in err_by_img.items() if t == "guideline_mismatch")
    notes = [
        f"Đã tách {len(rework)} ảnh sang rework_queue.csv (giao lại đúng người gán/kiểm theo jobs.csv); nhãn các ảnh còn lại chép nguyên từ v1, không sửa tay.",
        f"Split: đưa cả cảnh về một split (theo split đa số của cảnh) để ảnh gần giống nhau không vừa ở train vừa ở val làm điểm val ảo, cho {len(leak_found)} cảnh rò train/val: {', '.join(leak_found) or 'không có'}.",
        (f"Hash: {len(hash_ok)} ảnh wrong_hash đã được {args.hash_checked_by} mở xem, ảnh còn nguyên (chỉ manifest v1 ghi sai) nên manifest.csv ghi sha256 mới "
         if args.hash_checked_by or not hash_ok else
         f"Hash: <<CHƯA MỞ XEM — chạy lại với --hash-checked-by>> {len(hash_ok)} ảnh wrong_hash, manifest.csv ghi sha256 mới ")
        + f"({', '.join(hash_ok) or 'không có'}); "
        f"{len(hash_bad)} ảnh hỏng đưa vào rework ({', '.join(hash_bad) or 'không có'}).",
        f"Guideline: truyvet.csv lấy guideline theo job trong jobs.csv, vì job quyết định quy tắc người gán đã dùng; sửa {len(gm)} ảnh ghi sai guideline ({', '.join(gm) or 'không có'}).",
        f"Lỗi chỉ ở panoptic (nhãn detection vẫn đúng nên ảnh ở lại v2), báo team panoptic: "
        + (", ".join(f"{n} ({t})" for n, t in panoptic_only) or "không có") + ".",
    ]
    readme = [
        f"Release: {rid}_v2",
        f"Parent: {rid}",
        f"Số ảnh: {len(keep)}",
        f"Số nhãn: {n_labels}",
        f"Guideline: {job_ranges(jobs)}",
        f"QC v1: {n_err}/{len(man)} = {rate * 100:.1f}%".replace(".", ","),
        f"Kết luận v1: {v1}",
        f"Kết luận v2: {args.v2_decision} — còn 0/{len(keep)} ảnh có lỗi nhãn detection đã biết "
        f"(đã tách {len(rework)} ảnh sang rework, sửa split/hash/guideline); "
        f"{len(panoptic_only)}/{len(keep)} ảnh chỉ lỗi panoptic, không ảnh hưởng nhãn detection",
        "Ghi chú: " + " ".join(notes),
    ]
    (v2 / "README.txt").write_text("\n".join(readme) + "\n", encoding="utf-8")

    print(f"v2: {v2}")
    print(f"  ảnh v2: {len(keep)}  nhãn: {n_labels}  rework: {len(rework)}  panoptic-only: {len(panoptic_only)}")
    print(f"  QC v1: {n_err}/{len(man)} = {rate:.1%} -> {v1.split(' ')[0]}")
    if hash_ok or hash_bad:
        print(f"  NHỚ MỞ XEM ảnh wrong_hash: còn nguyên {hash_ok}, hỏng {hash_bad}. "
              "Ảnh nào xem thấy hỏng thì chạy lại với --broken-hash <tên>.")
    print("Tiếp theo: python3 scripts/pack_release.py", v2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
