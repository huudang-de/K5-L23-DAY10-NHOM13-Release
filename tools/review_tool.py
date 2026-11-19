#!/usr/bin/env python3
"""Human-only Day 10 review. Python 3.10+, Pillow, Tkinter (Windows Python).

Defaults: runs/r999/delivery/, 8 members; reviewer slot 4.
Training: py -X utf8 tools/review_tool.py --members 8 --member 4 --reviewer "TV4"
Hidden:   py -X utf8 tools/review_tool.py --delivery delivery \
          --candidates submission/de_an/candidates.json --out submission/de_an/review_log_m4.csv
See submission/REVIEW_TOOL.md for the candidate contract and configurable team workflow.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
from pathlib import Path
import sys
import tempfile

try:
    from PIL import Image, ImageChops, ImageDraw, ImageFilter
except ImportError:
    raise SystemExit("Thieu Pillow. Chay: py -m pip install Pillow")

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MEMBERS = 8
TYPES = ("class_swap", "category_swap", "bbox_drift", "missing_box", "instance_merge")
FIELDS = ("image", "type", "verdict", "note")
FORBIDDEN = {"_private", "data_source"}


def allowed(path: Path) -> Path:
    """Reject forbidden paths before opening files, including resolved symlinks."""
    if FORBIDDEN.intersection(p.lower() for p in path.parts):
        raise ValueError(f"Khong duoc truy cap: {path}")
    result = path.resolve()
    if FORBIDDEN.intersection(p.lower() for p in result.parts):
        raise ValueError(f"Khong duoc truy cap: {result}")
    return result


def inside(root: Path, relative: str) -> Path:
    path = allowed(root / relative)
    if not path.is_relative_to(root):
        raise ValueError(f"Duong dan vuot ra ngoai delivery: {relative}")
    return path


def output_path(path: Path, delivery: Path | None = None, suffix: str = ".csv") -> Path:
    path = allowed(path)
    if path.suffix.lower() != suffix:
        raise ValueError(f"File dau ra phai co duoi {suffix}")
    # Protect both the selected dataset and conventional delivery/ trees.
    if "delivery" in (p.lower() for p in path.parts) or (
        delivery is not None and path.is_relative_to(delivery)
    ):
        raise ValueError("Khong ghi vao delivery/. Chon dau ra ben ngoai delivery.")
    return path


def read_json(path: Path):
    return json.loads(allowed(path).read_text(encoding="utf-8-sig"))


def image_key(value) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("image/target phai la chuoi ten anh, giu nguyen so 0 dau.")
    value = value.strip()
    if "/" in value or "\\" in value or ":" in value or value in (".", ".."):
        raise ValueError(f"Ten anh khong hop le: {value!r}")
    return Path(value).stem if Path(value).suffix.lower() in (".jpg", ".jpeg", ".png") else value


def load_candidates(path: Path) -> dict[str, list[str]]:
    """Accept a list, {candidates: [...]}, or {errors: [...]} of image/type rows."""
    data = read_json(path)
    if isinstance(data, dict):
        data = data.get("candidates", data.get("errors"))
    if not isinstance(data, list):
        raise ValueError("candidates.json: can list hoac {\"candidates\": [ ... ]}.")
    result: dict[str, set[str]] = {}
    for index, row in enumerate(data, 1):
        if not isinstance(row, dict):
            raise ValueError(f"Candidate {index}: can object image/target va type/types.")
        key = image_key(row.get("image", row.get("target")))
        kinds = row.get("types", [row.get("type")])
        if not isinstance(kinds, list) or not kinds or any(t not in TYPES for t in kinds):
            raise ValueError(f"Candidate {index}: type/types chi nhan {', '.join(TYPES)}")
        result.setdefault(key, set()).update(kinds)
    return {key: sorted(result[key]) for key in sorted(result)}


def partition(candidates: dict[str, list[str]], member: int, members: int = DEFAULT_MEMBERS) -> list[str]:
    """Round-robin sorted unique images; all hypotheses for one image stay together."""
    if members < 1:
        raise ValueError("members phai >= 1")
    if not 1 <= member <= members:
        raise ValueError(f"member phai tu 1 den {members}")
    return sorted(candidates)[member - 1::members]


def read_log(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    path = allowed(path)
    if not path.exists():
        return {}
    rows = {}
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != list(FIELDS):
            raise ValueError(f"{path}: header phai la {','.join(FIELDS)}")
        for number, row in enumerate(reader, 2):
            if None in row or any(row.get(f) is None for f in FIELDS):
                raise ValueError(f"{path}:{number}: sai so cot")
            row = {f: row[f].strip() for f in FIELDS}
            key = (image_key(row["image"]), row["type"])
            if row["type"] not in TYPES or row["verdict"] not in ("confirmed", "rejected"):
                raise ValueError(f"{path}:{number}: type/verdict khong hop le")
            if len(row["note"]) < 20:
                raise ValueError(f"{path}:{number}: note can >=20 ky tu")
            row["image"] = key[0]
            if key in rows and rows[key] != row:
                raise ValueError(f"Xung dot review {key} trong {path}")
            rows[key] = row
    return rows


def write_log(path: Path, rows: dict, delivery: Path | None = None) -> None:
    """Atomic UTF-8 without BOM, compatible with the lab's merge_review.py."""
    path = output_path(path, delivery)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows[key] for key in sorted(rows))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def make_row(image: str, kind: str, verdict: str, note: str, reviewer: str) -> dict[str, str]:
    if kind not in TYPES or verdict not in ("confirmed", "rejected"):
        raise ValueError("Hay chon loai loi va confirmed/rejected.")
    reviewer, note = reviewer.strip(), note.strip()
    if not reviewer or any(c in reviewer for c in "[]\r\n"):
        raise ValueError("Nhap ten/ma nguoi review (khong dung dau ngoac vuong/xuong dong).")
    if len(note) < 20:
        raise ValueError("Ghi chu it nhat 20 ky tu: mo ta vat thay duoc va ly do ket luan.")
    return dict(image=image_key(image), type=kind, verdict=verdict,
                note=f"[reviewer={reviewer}] {note}")


def merge_logs(paths: list[Path], out: Path) -> int:
    out = output_path(out)
    merged = {}
    for path in paths:
        path = allowed(path)
        if not path.is_file():
            raise ValueError(f"Khong tim thay log: {path}")
        if path == out:
            raise ValueError("Dau ra gop phai khac cac file dau vao.")
        for key, row in read_log(path).items():
            if key in merged and merged[key] != row:
                raise ValueError(f"Xung dot {key}: nhom can doi chieu va tu chot; chua ghi file gop.")
            merged[key] = row
    write_log(out, merged)
    return len(merged)


def segment_color(sid: int) -> tuple[int, int, int]:
    return (80 + (sid * 37) % 176, 80 + (sid * 71) % 176, 80 + (sid * 113) % 176)


class Dataset:
    def __init__(self, delivery: Path):
        self.root = allowed(delivery)
        self.items = read_json(inside(self.root, "manifest.json"))["items"]
        panoptic = read_json(inside(self.root, "panoptic.json"))
        self.categories = {c["id"]: c for c in panoptic["categories"]}
        images = {im["id"]: im for im in panoptic["images"]}
        self.annotations = {}
        self.sizes = {}
        for ann in panoptic["annotations"]:
            im = images.get(ann["image_id"], {})
            name = Path(im.get("file_name", ann.get("file_name", str(ann["image_id"])))).stem
            self.annotations[name] = ann.get("segments_info", [])
            self.sizes[name] = (im.get("width", 640), im.get("height", 480))
        self.classes = {}
        for line in inside(self.root, "classes.txt").read_text(encoding="utf-8-sig").splitlines():
            if line.strip():
                cid, name = line.strip().split(maxsplit=1)
                self.classes[int(cid)] = name

    def views(self, key: str):
        """Return original, YOLO overlay, true pixel-boundary overlay, legend, warnings."""
        item = self.items.get(key)
        if item is None:
            raise ValueError(f"Anh {key} khong co trong manifest.json")
        warnings, legend = [], []
        image_path = inside(self.root, item["image"])
        try:
            with Image.open(image_path) as source:
                original = source.convert("RGB")
        except (OSError, ValueError) as exc:
            warnings.append(f"Khong mo duoc anh: {exc}")
            original = Image.new("RGB", self.sizes.get(key, (640, 480)), "#303030")
            ImageDraw.Draw(original).text((10, 10), "IMAGE MISSING / UNREADABLE", fill="white")
        width, height = original.size
        detection, panoptic = original.copy(), original.copy()
        draw = ImageDraw.Draw(detection)
        label_path = inside(self.root, item["label"])
        try:
            lines = label_path.read_text(encoding="utf-8-sig").splitlines()
        except OSError as exc:
            lines = []
            warnings.append(f"Khong doc duoc label: {exc}")
        for number, line in enumerate(lines, 1):
            if not line.strip():
                continue
            try:
                cls, xc, yc, bw, bh = line.split()
                cls = int(cls)
                xc, yc, bw, bh = map(float, (xc, yc, bw, bh))
                if not all(math.isfinite(v) for v in (xc, yc, bw, bh)) or bw < 0 or bh < 0:
                    raise ValueError("box khong huu han hoac kich thuoc am")
                box = ((xc - bw / 2) * width, (yc - bh / 2) * height,
                       (xc + bw / 2) * width, (yc + bh / 2) * height)
                name = self.classes.get(cls, f"INVALID_CLASS({cls})")
                tag = f"D{number}: {name} [{cls}]"
                draw.rectangle(box, outline="#ffb000", width=2)
                self.tag(draw, (max(0, min(width - 1, box[0])),
                                max(0, min(height - 13, box[1]))), tag, "#ffb000")
                legend.append(f"{tag} | xyxy=" + ",".join(f"{v:.1f}" for v in box))
            except (ValueError, OverflowError) as exc:
                warnings.append(f"Label dong {number}: {exc}")
        mask_path = inside(self.root, item["mask"])
        try:
            with Image.open(mask_path) as source:
                mask = source.convert("RGB")
            if mask.size != original.size:
                raise ValueError(f"Kich thuoc mask {mask.size} khac anh {original.size}; khong tu resize")
            # Pillow C-level lookup, no numpy. Decode EXACTLY R + G*256 + B*65536.
            red, green, blue = mask.split()
            from PIL import ImageMath, ImageOps
            ids = ImageMath.lambda_eval(lambda a: a["r"] + a["g"] * 256 + a["b"] * 65536,
                                       r=red.convert("I"), g=green.convert("I"), b=blue.convert("I"))
            for segment in self.annotations.get(key, []):
                sid = segment["id"]
                if sid == 0:
                    continue
                cat_id = segment["category_id"]
                category = self.categories.get(cat_id, {})
                color = segment_color(sid)
                # A binary mask per segment avoids grayscale-id contour errors.
                binary = ImageMath.lambda_eval(lambda a: (a["ids"] == a["sid"]) * 255,
                                               ids=ids, sid=sid).convert("L")
                # Zero padding preserves the outline even where a segment touches the image border.
                eroded = ImageOps.expand(binary, 1, fill=0).filter(ImageFilter.MinFilter(3))
                edge = ImageChops.subtract(binary, eroded.crop((1, 1, width + 1, height + 1)))
                panoptic.paste(color, (0, 0), edge)
                name = category.get("name", f"INVALID_CATEGORY({cat_id})")
                crowd = " crowd" if segment.get("iscrowd") else ""
                tag = f"P{sid}: {name}{crowd}"
                bounds = binary.getbbox()
                if bounds:
                    self.tag(ImageDraw.Draw(panoptic), (bounds[0], bounds[1]), tag, color)
                else:
                    warnings.append(f"Segment {sid}: khong co pixel trong mask")
                legend.append(f"{tag} | category_id={cat_id} | "
                              f"{'thing' if category.get('isthing') else 'stuff'} | color={color}")
        except (OSError, ValueError) as exc:
            warnings.append(f"Khong ve duoc mask: {exc}")
        return original, detection, panoptic, legend, warnings

    @staticmethod
    def tag(draw, point, text, color):
        x, y = point
        bounds = draw.textbbox((x, y), text)
        draw.rectangle(bounds, fill="black")
        draw.text((x, y), text, fill=color)


class ReviewApp:
    def __init__(self, root, dataset, candidates, member, reviewer, out, members=DEFAULT_MEMBERS):
        import tkinter as tk
        from tkinter import ttk
        self.tk, self.ttk, self.root = tk, ttk, root
        self.dataset, self.candidates, self.out = dataset, candidates, out
        self.member, self.members = member, members
        self.queue = partition(candidates, member, members)
        self.rows = read_log(out)
        self.index, self.zoom, self.photos, self.dirty = 0, 1.0, [], False
        root.title(f"Day 10 - Review thu cong - Phan {member}/{members}")
        root.geometry("1320x900")
        root.minsize(900, 650)
        self.status = tk.StringVar()
        ttk.Label(root, textvariable=self.status, font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=8, pady=5)
        bar = ttk.Frame(root)
        bar.pack(fill="x", padx=8)
        for label, callback in (("< Truoc", lambda: self.move(-1)), ("Sau >", lambda: self.move(1)),
                                ("-", lambda: self.scale(0.8)), ("+", lambda: self.scale(1.25)),
                                ("Vua khung", self.fit), ("100%", lambda: self.scale(absolute=1.0))):
            ttk.Button(bar, text=label, command=callback).pack(side="left", padx=2)
        self.layer = tk.StringVar(value="Ca ba")
        combo = ttk.Combobox(bar, textvariable=self.layer, values=("Ca ba", "Anh goc", "YOLO", "Panoptic"),
                             state="readonly", width=12)
        combo.pack(side="left", padx=8)
        combo.bind("<<ComboboxSelected>>", lambda _: self.draw())
        ttk.Label(bar, text="Cuon chuot: zoom | Keo chuot trai: di chuyen").pack(side="left")
        area = ttk.Frame(root)
        area.pack(fill="both", expand=True, padx=8, pady=6)
        area.rowconfigure(0, weight=1)
        area.columnconfigure(0, weight=1)
        self.canvas = tk.Canvas(area, background="#222222", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        horizontal = ttk.Scrollbar(area, orient="horizontal", command=self.canvas.xview)
        vertical = ttk.Scrollbar(area, orient="vertical", command=self.canvas.yview)
        horizontal.grid(row=1, column=0, sticky="ew")
        vertical.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(xscrollcommand=horizontal.set, yscrollcommand=vertical.set)
        self.canvas.bind("<MouseWheel>", lambda e: self.scale(1.25 if e.delta > 0 else 0.8))
        self.canvas.bind("<ButtonPress-1>", lambda e: self.canvas.scan_mark(e.x, e.y))
        self.canvas.bind("<B1-Motion>", lambda e: self.canvas.scan_dragto(e.x, e.y, gain=1))
        self.details = tk.Text(root, height=5, wrap="word", font=("Consolas", 9))
        self.details.pack(fill="x", padx=8)
        form = ttk.Frame(root)
        form.pack(fill="x", padx=8, pady=6)
        ttk.Label(form, text="Nguoi xem:").grid(row=0, column=0)
        self.reviewer = tk.StringVar(value=reviewer)
        ttk.Entry(form, textvariable=self.reviewer, width=20).grid(row=0, column=1, padx=5)
        ttk.Label(form, text="Loai dang review:").grid(row=0, column=2)
        self.kind = tk.StringVar()
        kind_box = ttk.Combobox(form, textvariable=self.kind, values=TYPES, state="readonly", width=19)
        kind_box.grid(row=0, column=3, padx=5)
        kind_box.bind("<<ComboboxSelected>>", self.select_kind)
        self.verdict = tk.StringVar(value="")
        for column, verdict in enumerate(("confirmed", "rejected"), 4):
            ttk.Radiobutton(form, text=verdict, variable=self.verdict, value=verdict,
                            command=self.mark_dirty).grid(row=0, column=column, padx=5)
        ttk.Label(root, text="Ghi chu >=20 ky tu: thay vat gi, nguon nhan nao hop ly, vi sao? "
                  "(Loai loi co the doi khi anh cho thay nguon con lai sai.)").pack(anchor="w", padx=8)
        self.note = tk.Text(root, height=3, wrap="word", font=("Segoe UI", 10))
        self.note.pack(fill="x", padx=8, pady=4)
        self.note.bind("<<Modified>>", self.note_changed)
        self.reviewer.trace_add("write", lambda *_: self.mark_dirty())
        actions = ttk.Frame(root)
        actions.pack(fill="x", padx=8, pady=6)
        ttk.Button(actions, text="Luu dong (Ctrl+S)", command=self.save).pack(side="left")
        ttk.Button(actions, text="Luu va anh sau", command=lambda: self.save(True)).pack(side="left", padx=5)
        ttk.Label(actions, text=f"CSV: {out}").pack(side="left", padx=8)
        root.bind("<Control-s>", lambda _: self.save())
        root.protocol("WM_DELETE_WINDOW", self.close)
        root.update_idletasks()
        if self.queue:
            self.load()
        else:
            self.status.set(f"Phan {member}/{members}: 0 anh. Khong co ket luan nao duoc tao.")
            self.images = ()
        self.dirty = False

    def mark_dirty(self):
        self.dirty = True

    def note_changed(self, _=None):
        if self.note.edit_modified():
            self.dirty = True
            self.note.edit_modified(False)

    def guard(self):
        from tkinter import messagebox
        if not self.dirty:
            return True
        answer = messagebox.askyesnocancel("Chua luu", "Luu dong dang nhap truoc khi tiep tuc?", parent=self.root)
        if answer is None:
            return False
        return self.save() if answer else True

    def select_kind(self, _=None):
        if not self.queue:
            return
        chosen = self.kind.get()
        self.kind.set(self.previous_kind)
        if self.guard():
            self.kind.set(chosen)
            self.restore_row()

    def restore_row(self):
        self.previous_kind = self.kind.get()
        row = self.rows.get((self.queue[self.index], self.kind.get()))
        self.verdict.set(row["verdict"] if row else "")
        self.note.delete("1.0", "end")
        if row:
            note = row["note"]
            if note.startswith("[reviewer=") and "] " in note:
                identity, _, note = note.partition("] ")
                self.reviewer.set(identity.removeprefix("[reviewer="))
            self.note.insert("1.0", note)
        self.note.edit_modified(False)
        self.dirty = False

    def load(self):
        key = self.queue[self.index]
        try:
            *self.images, legend, warnings = self.dataset.views(key)
        except (OSError, ValueError, KeyError) as exc:
            self.images = [Image.new("RGB", (640, 480), "#303030")] * 3
            legend, warnings = [], [str(exc)]
        kinds = self.candidates[key]
        self.kind.set(kinds[0])
        self.restore_row()
        self.details.configure(state="normal")
        self.details.delete("1.0", "end")
        self.details.insert("1.0", "Goi y (chua ket luan): " + ", ".join(kinds) + "\n" +
                            "\n".join(["CANH BAO: " + w for w in warnings] + legend))
        self.details.configure(state="disabled")
        done = sum(any((im, kind) in self.rows for kind in TYPES) for im in self.queue)
        self.status.set(f"Phan {self.member}/{self.members} | {self.index + 1}/{len(self.queue)} | {key} | "
                        f"{done} anh co dong da luu | Goi y: {', '.join(kinds)}")
        self.fit()

    def draw(self):
        from PIL import ImageTk
        if not self.images:
            return
        selection = {"Anh goc": [0], "YOLO": [1], "Panoptic": [2], "Ca ba": [0, 1, 2]}[self.layer.get()]
        self.canvas.delete("all")
        self.photos = []
        x = 0
        for index in selection:
            image = self.images[index]
            width, height = (max(1, round(v * self.zoom)) for v in image.size)
            rendered = image.resize((width, height), Image.Resampling.NEAREST if self.zoom >= 1 else Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(rendered)
            self.photos.append(photo)
            self.canvas.create_text(x + 8, 12, text=("ANH GOC", "YOLO - box vang", "PANOPTIC - vien segment")[index],
                                    fill="white", anchor="w", font=("Segoe UI", 11, "bold"))
            self.canvas.create_image(x, 28, image=photo, anchor="nw")
            x += width + 12
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def fit(self):
        if not self.images:
            return
        width, height = self.images[0].size
        columns = 3 if self.layer.get() == "Ca ba" else 1
        self.zoom = max(0.05, min((self.canvas.winfo_width() - 12 * columns) / (columns * width),
                                  (self.canvas.winfo_height() - 30) / height, 4.0))
        self.draw()
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

    def scale(self, factor=1, absolute=None):
        self.zoom = max(0.05, min(8.0, absolute if absolute is not None else self.zoom * factor))
        self.draw()

    def move(self, delta):
        if self.queue and 0 <= self.index + delta < len(self.queue) and self.guard():
            self.index += delta
            self.load()

    def save(self, advance=False):
        from tkinter import messagebox
        try:
            if not self.queue:
                write_log(self.out, self.rows, self.dataset.root)
                self.dirty = False
                self.status.set(f"Da xuat CSV cho phan rong: {self.out}")
                return True
            row = make_row(self.queue[self.index], self.kind.get(), self.verdict.get(),
                           self.note.get("1.0", "end"), self.reviewer.get())
            # Reload to preserve any other rows; never silently overwrite an external edit.
            disk = read_log(self.out)
            key = (row["image"], row["type"])
            if disk.get(key) != self.rows.get(key):
                raise ValueError("Dong nay da doi boi phien khac. Dong/mo lai tool de doi chieu.")
            disk[key] = row
            write_log(self.out, disk, self.dataset.root)
            self.rows, self.dirty = disk, False
            self.status.set(f"Da luu {key[0]} / {key[1]} / {row['verdict']} -> {self.out.name}")
            if advance:
                if self.index + 1 < len(self.queue):
                    self.move(1)
                else:
                    messagebox.showinfo("Da luu", "Da den cuoi phan anh. Kiem tra du cac loai goi y trong moi anh.", parent=self.root)
            return True
        except (OSError, ValueError) as exc:
            messagebox.showerror("Chua luu", str(exc), parent=self.root)
            return False

    def close(self):
        if self.guard():
            self.root.destroy()


def main(argv=None):
    parser = argparse.ArgumentParser(description="Review thu cong YOLO/Panoptic, chia theo so thanh vien; khong tu ket luan.")
    parser.add_argument("--delivery", type=Path, default=ROOT / "runs/r999/delivery",
                        help="Thu muc delivery, mac dinh %(default)s")
    parser.add_argument("--candidates", type=Path, help="Mac dinh: thu muc cha delivery/candidates.json")
    parser.add_argument("--members", type=int, default=DEFAULT_MEMBERS,
                        help="Tong so thanh vien/phan >=1, mac dinh %(default)s")
    parser.add_argument("--member", type=int, default=4, help="So phan 1..--members, mac dinh 4")
    parser.add_argument("--reviewer", help="Ten/ma nguoi truc tiep xem anh; mac dinh TV<member>")
    parser.add_argument("--out", type=Path, help="CSV rieng tung nguoi; --merge dung lam CSV tong")
    parser.add_argument("--merge", nargs="+", type=Path, metavar="CSV", help="Gop log; dung neu xung dot, khong tu chon verdict")
    parser.add_argument("--check", action="store_true", help="Doc/render phan duoc chia, bao canh bao, khong mo GUI/ghi verdict")
    parser.add_argument("--preview", type=Path, metavar="PNG", help="Xuat 3 khung anh dau tien trong phan; khong ghi verdict")
    args = parser.parse_args(argv)
    if args.members < 1:
        parser.error("--members phai >= 1")
    if not args.merge and not 1 <= args.member <= args.members:
        parser.error(f"--member phai tu 1 den {args.members} (theo --members)")
    try:
        if args.merge:
            if args.out is None:
                parser.error("--merge can --out review_log.csv")
            count = merge_logs(args.merge, args.out)
            print(f"Da gop {count} dong -> {args.out}")
            return 0
        delivery = allowed(args.delivery)
        path = allowed(args.candidates or delivery.parent / "candidates.json")
        if not path.is_file():
            raise ValueError(f"Chua co {path}. Can thanh vien phu trach validator xuat candidates.json truoc.")
        candidates = load_candidates(path)
        dataset = Dataset(delivery)
        unknown = set(candidates) - dataset.items.keys()
        if unknown:
            raise ValueError(f"Candidate khong co trong manifest: {', '.join(sorted(unknown)[:5])}")
        out = output_path(args.out or path.parent / f"review_log_m{args.member}.csv", delivery)
        if out == path:
            raise ValueError("Khong ghi de candidates.json")
        queue = partition(candidates, args.member, args.members)
        print(f"{len(candidates)} anh / {args.members} phan: " + ", ".join(
            str(len(partition(candidates, m, args.members))) for m in range(1, args.members + 1)))
        print(f"Phan {args.member}: {len(queue)} anh. CSV: {out}")
        if args.check or args.preview:
            preview = output_path(args.preview, delivery, ".png") if args.preview else None
            for index, key in enumerate(queue):
                original, det, pan, legend, warnings = dataset.views(key)
                print(f"{key}: {original.width}x{original.height}, {len(legend)} nhan; {len(warnings)} canh bao")
                for warning in warnings:
                    print("  " + warning)
                if preview and index == 0:
                    panel = Image.new("RGB", (original.width * 3, original.height + 25), "#222222")
                    draw = ImageDraw.Draw(panel)
                    for column, (label, im) in enumerate(zip(("ORIGINAL", "YOLO", "PANOPTIC"), (original, det, pan))):
                        draw.text((column * original.width + 5, 5), label, fill="white")
                        panel.paste(im, (column * original.width, 25))
                    preview.parent.mkdir(parents=True, exist_ok=True)
                    panel.save(preview)
                    print(f"Preview: {preview}")
                if not args.check:
                    break
            if preview and not queue:
                raise ValueError("Phan nay khong co anh de preview")
            return 0
        import tkinter as tk
        root = tk.Tk()
        ReviewApp(root, dataset, candidates, args.member, args.reviewer or f"TV{args.member}", out,
                  members=args.members)
        root.mainloop()
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"LOI: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
