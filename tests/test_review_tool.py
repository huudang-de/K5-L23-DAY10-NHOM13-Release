"""Synthetic, temporary fixtures only; never reads original answers or writes lab reviews."""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image, ImageDraw

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/review_tool.py"
spec = importlib.util.spec_from_file_location("review_tool", SCRIPT)
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


class ReviewToolTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="review-tool-test-")
        self.base = Path(self.temp.name).resolve()
        self.delivery = self.base / "delivery"
        for directory in ("images", "labels", "masks"):
            (self.delivery / directory).mkdir(parents=True)
        # Opaque name, nonnumeric image_id: the same contract as the hidden dataset.
        self.key = "img_0001"
        Image.new("RGB", (120, 100), (30, 30, 30)).save(self.delivery / "images/img_0001.png")
        mask = Image.new("RGB", (120, 100))
        draw = ImageDraw.Draw(mask)
        self.sid = 1 + 2 * 256 + 3 * 65536
        draw.rectangle((10, 20, 50, 70), fill=(1, 2, 3))
        draw.rectangle((80, 50, 119, 99), fill=(2, 2, 3))
        mask.save(self.delivery / "masks/img_0001.png")
        (self.delivery / "labels/img_0001.txt").write_text("7 0.5 0.5 0.5 0.4\n", encoding="utf-8")
        (self.delivery / "classes.txt").write_text("0 person\n7 truck\n", encoding="utf-8")
        manifest = {"items": {self.key: {"image": "images/img_0001.png",
                    "label": "labels/img_0001.txt", "mask": "masks/img_0001.png"}}}
        self.put_json(self.delivery / "manifest.json", manifest)
        self.put_json(self.delivery / "panoptic.json", {
            "categories": [{"id": 8, "name": "truck", "isthing": 1}],
            "images": [{"id": 91, "file_name": "img_0001.png", "width": 120, "height": 100}],
            "annotations": [{"image_id": 91, "file_name": "img_0001.png", "segments_info": [
                {"id": self.sid, "category_id": 8, "bbox": [0, 0, 1, 1]},
                {"id": self.sid + 1, "category_id": 8, "iscrowd": 1}]}]})
        self.candidates = self.base / "candidates.json"
        self.put_json(self.candidates, {"candidates": [{"image": self.key, "type": "class_swap"}]})
        self.out = self.base / "review.csv"

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def put_json(path, value):
        path.write_text(json.dumps(value), encoding="utf-8")

    def row(self, verdict="confirmed", note="SYNTHETIC TEST ONLY: mot vat hinh chu nhat trong fixture"):
        return tool.make_row(self.key, "class_swap", verdict, note, "TV4 thử nghiệm")

    def digest(self):
        return {p.relative_to(self.delivery).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.delivery.rglob("*") if p.is_file()}

    def test_candidate_formats_normalization_and_duplicates(self):
        for payload in ([{"target": "000001.jpg", "type": "bbox_drift"}] * 2,
                        {"errors": [{"target": "000001", "types": ["bbox_drift"]}]},
                        {"candidates": [{"image": "000001", "type": "bbox_drift"}]}):
            self.put_json(self.candidates, payload)
            self.assertEqual(tool.load_candidates(self.candidates), {"000001": ["bbox_drift"]})

    def test_invalid_candidates_fail_explicitly(self):
        for row in ({"image": "img_1", "type": "anything"},
                    {"image": "../secret", "type": "class_swap"},
                    {"image": 123, "type": "class_swap"}):
            self.put_json(self.candidates, [row])
            with self.assertRaises(ValueError):
                tool.load_candidates(self.candidates)

    def test_partition_stable_disjoint_balanced_at_image_level(self):
        for count in (0, 1, 5, 6, 7, 29):
            data = {f"img_{i:04}": ["class_swap", "category_swap"] for i in reversed(range(count))}
            parts = [tool.partition(data, member) for member in range(1, 7)]
            self.assertEqual(sum(map(len, parts)), count)
            self.assertEqual(len(set(sum(parts, []))), count)
            self.assertLessEqual(max(map(len, parts)) - min(map(len, parts)), 1)
            self.assertEqual(parts, [tool.partition(dict(reversed(list(data.items()))), m) for m in range(1, 7)])

    def test_yolo_coordinates_and_class_name(self):
        original, det, _, legend, warnings = tool.Dataset(self.delivery).views(self.key)
        self.assertEqual(warnings, [])
        self.assertEqual(original.getpixel((30, 60)), (30, 30, 30))
        self.assertEqual(det.getpixel((30, 60)), (255, 176, 0))
        self.assertTrue(any("truck [7]" in line and "30.0,30.0,90.0,70.0" in line for line in legend))

    def test_real_pixel_contours_rgb_decode_border_and_crowd(self):
        _, _, pan, legend, warnings = tool.Dataset(self.delivery).views(self.key)
        self.assertEqual(warnings, [])
        self.assertEqual(pan.getpixel((10, 60)), tool.segment_color(self.sid))
        self.assertEqual(pan.getpixel((20, 60)), (30, 30, 30))  # unfilled interior
        self.assertEqual(pan.getpixel((119, 90)), tool.segment_color(self.sid + 1))
        self.assertEqual(pan.getpixel((90, 99)), tool.segment_color(self.sid + 1))
        self.assertTrue(any("crowd" in line for line in legend))

    def test_missing_image_label_mask_report_warnings_without_verdict(self):
        for path in (self.delivery / "images/img_0001.png", self.delivery / "labels/img_0001.txt",
                     self.delivery / "masks/img_0001.png"):
            path.unlink()
        *_, warnings = tool.Dataset(self.delivery).views(self.key)
        self.assertEqual(len(warnings), 3)
        self.assertFalse(self.out.exists())

    def test_mismatched_mask_not_silently_resized(self):
        Image.new("RGB", (5, 5)).save(self.delivery / "masks/img_0001.png")
        *_, warnings = tool.Dataset(self.delivery).views(self.key)
        self.assertIn("khong tu resize", warnings[0])

    def test_bad_labels_nan_and_invalid_class_are_visible(self):
        (self.delivery / "labels/img_0001.txt").write_text(
            "7 nan 0.5 0.1 0.1\n7 bad\n999 0.5 0.5 0.2 0.2\n", encoding="utf-8")
        *_, legend, warnings = tool.Dataset(self.delivery).views(self.key)
        self.assertEqual(len(warnings), 2)
        self.assertTrue(any("INVALID_CLASS(999)" in line for line in legend))

    def test_path_guards_and_manifest_escape(self):
        for name in ("_private/x", "data_source/x", "delivery/out.csv"):
            with self.assertRaises(ValueError):
                tool.output_path(self.base / name)
        ds = tool.Dataset(self.delivery)
        ds.items[self.key]["image"] = "../outside.png"
        with self.assertRaises(ValueError):
            ds.views(self.key)
        ds.items[self.key]["image"] = "../_private/answer.json"
        with self.assertRaises(ValueError):
            ds.views(self.key)

    def test_review_requires_explicit_verdict_note_and_person(self):
        for verdict, note, reviewer in (("", "X" * 30, "TV4"),
                                        ("confirmed", "short", "TV4"),
                                        ("rejected", "X" * 30, "")):
            with self.assertRaises(ValueError):
                tool.make_row(self.key, "class_swap", verdict, note, reviewer)
        self.assertFalse(self.out.exists())

    def test_csv_utf8_escaping_resume_and_edit(self):
        row = self.row(note='SYNTHETIC TEST: "xe tải", ghi chú tiếng Việt\nxuống dòng')
        key = (self.key, "class_swap")
        tool.write_log(self.out, {key: row})
        self.assertFalse(self.out.read_bytes().startswith(b"\xef\xbb\xbf"))
        self.assertEqual(self.out.read_text(encoding="utf-8").splitlines()[0], "image,type,verdict,note")
        self.assertEqual(tool.read_log(self.out)[key], row)
        tool.write_log(self.out, {key: self.row("rejected")})
        self.assertEqual(len(tool.read_log(self.out)), 1)
        self.assertEqual(tool.read_log(self.out)[key]["verdict"], "rejected")

    def test_merge_dedup_and_conflict_does_not_replace_output(self):
        first, second = self.base / "m1.csv", self.base / "m2.csv"
        key = (self.key, "class_swap")
        tool.write_log(first, {key: self.row()})
        tool.write_log(second, {key: self.row()})
        self.assertEqual(tool.merge_logs([first, second], self.out), 1)
        before = self.out.read_bytes()
        tool.write_log(second, {key: self.row("rejected")})
        with self.assertRaises(ValueError):
            tool.merge_logs([first, second], self.out)
        self.assertEqual(self.out.read_bytes(), before)

    def test_merge_six_separate_people(self):
        paths = []
        for member in range(1, 7):
            row = tool.make_row(f"img_{member:04}", "bbox_drift", "rejected",
                                "SYNTHETIC TEST ONLY: fixture chu nhat de kiem thu", f"TV{member}")
            path = self.base / f"m{member}.csv"
            tool.write_log(path, {(row["image"], row["type"]): row})
            paths.append(path)
        self.assertEqual(tool.merge_logs(paths, self.out), 6)
        self.assertEqual(len(tool.read_log(self.out)), 6)

    def test_compatible_with_existing_merge_review_script(self):
        # Only a synthetic rules file and synthetic log are supplied to the unchanged lab script.
        tool.write_log(self.out, {(self.key, "class_swap"): self.row()})
        rules, merged = self.base / "rules.json", self.base / "errors.json"
        self.put_json(rules, {"errors": []})
        result = subprocess.run([sys.executable, "-X", "utf8", str(SCRIPT.parent / "merge_review.py"),
                                 "--rules", str(rules), "--review", str(self.out), "--out", str(merged)],
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(merged.read_text()), {"errors": [{"type": "class_swap", "target": self.key}]})

    def test_cli_check_preview_and_empty_partition_never_create_review(self):
        before = self.digest()
        preview = self.base / "preview.png"
        self.assertEqual(tool.main(["--delivery", str(self.delivery), "--candidates", str(self.candidates),
                                    "--member", "1", "--check", "--preview", str(preview),
                                    "--out", str(self.out)]), 0)
        with Image.open(preview) as image:
            self.assertEqual(image.size, (360, 125))
        self.assertEqual(tool.main(["--delivery", str(self.delivery), "--member", "6", "--check"]), 0)
        self.assertEqual(before, self.digest())
        self.assertFalse(self.out.exists())

    def test_tk_gui_save_resume_zoom_type_switch_and_unsaved_guard(self):
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        try:
            app = tool.ReviewApp(root, tool.Dataset(self.delivery), tool.load_candidates(self.candidates),
                                 1, "TV4 test", self.out)
            root.update()
            self.assertEqual(app.verdict.get(), "")
            self.assertFalse(self.out.exists())
            app.scale(absolute=2.0)
            self.assertEqual(app.zoom, 2.0)
            self.assertEqual(len(app.photos), 3)
            app.layer.set("Anh goc")
            app.draw()
            self.assertEqual(len(app.photos), 1)
            app.verdict.set("rejected")
            app.note.insert("1.0", "SYNTHETIC TEST ONLY: hinh chu nhat trong du lieu tu tao")
            root.update()
            self.assertTrue(app.save())
            root.update()
            self.assertFalse(app.dirty)
            app.restore_row()
            self.assertEqual(app.verdict.get(), "rejected")
            self.assertIn("SYNTHETIC TEST ONLY", app.note.get("1.0", "end"))
            app.kind.set("category_swap")
            app.select_kind()
            self.assertEqual(app.verdict.get(), "")
            self.assertEqual(app.note.get("1.0", "end").strip(), "")
            app.note.insert("1.0", "unsaved")
            root.update()
            with patch("tkinter.messagebox.askyesnocancel", return_value=None):
                self.assertFalse(app.guard())
        finally:
            root.destroy()

    def test_tk_previous_next_keep_all_hypotheses_on_one_image(self):
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        try:
            dataset = tool.Dataset(self.delivery)
            candidates = {f"img_{i:04}": ["class_swap", "category_swap"] for i in range(1, 8)}
            for key in candidates:
                dataset.items[key] = dataset.items[self.key]
                dataset.annotations[key] = dataset.annotations[self.key]
            app = tool.ReviewApp(root, dataset, candidates, 1, "TV1 test", self.out)
            root.update()
            self.assertEqual(app.queue, ["img_0001", "img_0007"])
            app.move(1)
            root.update()
            self.assertEqual(app.index, 1)
            self.assertEqual(app.verdict.get(), "")
            app.move(-1)
            root.update()
            self.assertEqual(app.index, 0)
            self.assertFalse(self.out.exists())
        finally:
            root.destroy()

    def test_tk_empty_partition_can_export_header_only(self):
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        try:
            app = tool.ReviewApp(root, tool.Dataset(self.delivery), tool.load_candidates(self.candidates),
                                 6, "Lead test", self.out)
            root.update()
            self.assertFalse(self.out.exists())
            self.assertTrue(app.save())
            self.assertEqual(self.out.read_text().strip(), "image,type,verdict,note")
            self.assertEqual(tool.read_log(self.out), {})
        finally:
            root.destroy()

    def test_tk_external_edit_not_overwritten(self):
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        try:
            app = tool.ReviewApp(root, tool.Dataset(self.delivery), tool.load_candidates(self.candidates),
                                 1, "TV1 test", self.out)
            root.update()
            external = self.row("rejected")
            tool.write_log(self.out, {(self.key, "class_swap"): external})
            app.verdict.set("confirmed")
            app.note.insert("1.0", "SYNTHETIC TEST ONLY: fixture dung de kiem thu ghi de")
            with patch("tkinter.messagebox.showerror") as error:
                self.assertFalse(app.save())
                error.assert_called_once()
            self.assertEqual(tool.read_log(self.out)[(self.key, "class_swap")], external)
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main(verbosity=2)
