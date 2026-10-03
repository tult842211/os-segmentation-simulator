"""Real-widget integration tests; safely skip if the host has no Tk display.

File choosers and modal error boxes are mocked, never the translation core.
"""
import csv
import gc
from pathlib import Path
import tempfile
import time
import tkinter as tk
import unittest
from unittest.mock import patch

from src.gui import DISPLAY_LIMIT, PROJECT_ROOT, SegmentationApp
from src.segmentation import LogicalAddress, Segment, SegmentTable


class GuiIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.root = tk.Tk()
            cls.root.withdraw()
        except tk.TclError as exc:
            raise unittest.SkipTest(f"Tk display/runtime unavailable: {exc}")

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def setUp(self):
        self.callback_errors = []
        self.root.report_callback_exception = lambda *args: self.callback_errors.append(args)
        self.error_patch = patch("src.gui.messagebox.showerror")
        self.error_dialog = self.error_patch.start()
        self.app = SegmentationApp(self.root)
        self.root.update_idletasks()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.addCleanup(self.error_patch.stop)

    def tearDown(self):
        self.app.destroy()
        del self.app
        # Tk variables must be finalized on the UI thread, before the next
        # test's CSV worker can trigger Python's cyclic garbage collector.
        gc.collect()
        self.root.update_idletasks()
        self.assertEqual(self.callback_errors, [], "Tk callbacks raised an exception")

    def wait_for_worker(self):
        deadline = time.monotonic() + 8
        while self.app._job_running and time.monotonic() < deadline:
            self.root.update()
            time.sleep(.01)
        self.assertFalse(self.app._job_running, "CSV worker did not finish")
        self.root.update_idletasks()

    def csv_file(self, filename, text):
        path = Path(self.temp_dir.name) / filename
        path.write_text(text, encoding="utf-8")
        return path

    def test_sample_startup_and_single_translation_button(self):
        self.assertEqual(len(self.app.segment_tree.get_children()), 3)
        self.app.translate_button.invoke()
        self.assertEqual(self.app.single_result.physical_address, 1120)
        self.assertIn("1120", self.app.result_title.cget("text"))
        self.assertEqual(self.app.trace_visible, 5)
        self.assertNotIn("1. 1.", self.app.trace_text.get("1.0", "end"))
        self.error_dialog.assert_not_called()

    def test_startup_reserves_screen_space_without_showing_window(self):
        # Check the window manager's requested geometry while it stays hidden;
        # tests do not open or move a visible application window.
        width, height = map(int, self.root.geometry().split("+")[0].split("x"))
        self.assertLessEqual(width, self.root.winfo_screenwidth() - 80)
        self.assertLessEqual(height, self.root.winfo_screenheight() - 120)
        self.assertEqual(self.app.status_label.pack_info()["side"], "bottom")

    def test_step_mode_reveals_trace_until_disabled(self):
        self.app.step_button.invoke()
        self.assertEqual(self.app.trace_visible, 1)
        self.assertNotIn("5. Địa chỉ", self.app.trace_text.get("1.0", "end"))
        for _ in range(4):
            self.app.next_button.invoke()
        self.assertEqual(self.app.trace_visible, 5)
        self.assertTrue(self.app.next_button.instate(["disabled"]))
        self.assertIn("1120", self.app.trace_text.get("1.0", "end"))

    def test_boundary_and_permission_failures_do_not_produce_address(self):
        self.app.offset_var.set("400")
        self.app.translate_button.invoke()
        self.assertEqual(self.app.single_result.status, "SEGMENTATION_FAULT")
        self.assertIsNone(self.app.single_result.physical_address)
        self.app.offset_var.set("100")
        self.app.access_var.set("Ghi (w)")
        self.app.translate_button.invoke()
        self.assertEqual(self.app.single_result.status, "PROTECTION_FAULT")
        self.assertIn("PROTECTION_FAULT", self.app.result_title.cget("text"))

    def test_invalid_typed_input_shows_error_without_replacing_result(self):
        self.app.translate_button.invoke()
        previous = self.app.single_result
        self.app.offset_var.set("không phải số")
        self.app.translate_button.invoke()
        self.assertIs(self.app.single_result, previous)
        self.error_dialog.assert_called_once()

    def test_add_update_remove_and_preserve_nonempty_table(self):
        self.app.add_button.invoke()  # Default editor is segment 3 at 4000.
        self.assertEqual(len(self.app.table.segments), 4)
        self.app.limit_var.set("250")
        self.app.add_button.invoke()
        self.assertEqual(self.app.table.segments[-1].limit, 250)
        self.assertEqual(len(self.app.table.segments), 4)
        self.app.segment_tree.selection_set("3")
        self.app.remove_button.invoke()
        self.assertEqual(len(self.app.table.segments), 3)
        self.app._replace_table(SegmentTable([Segment(0, 100, 10)]), "test")
        self.app.segment_tree.selection_set("0")
        self.app.remove_button.invoke()
        self.assertEqual(len(self.app.table.segments), 1)
        self.error_dialog.assert_called_once()

    def test_segment_csv_dialog_and_failed_reload_are_atomic(self):
        path = self.csv_file("segments.csv", "segment_id,base,limit\n8,5000,50\n")
        with patch("src.gui.filedialog.askopenfilename", return_value=str(path)):
            self.app.load_segments_button.invoke()
        self.assertEqual(self.app.table.segments[0].segment_id, 8)
        self.assertEqual(len(self.app.segment_tree.get_children()), 1)
        previous = self.app.table
        invalid = self.csv_file("invalid.csv", "segment_id,base\n1,300\n")
        self.assertFalse(self.app.load_segments_path(invalid))
        self.assertIs(self.app.table, previous)
        self.error_dialog.assert_called_once()

    def test_sample_batch_and_export_contain_all_statuses(self):
        self.app.batch_sample_button.invoke()
        self.wait_for_worker()
        self.assertEqual(len(self.app.batch_results), 10)
        self.assertEqual({r.status for r in self.app.batch_results},
                         {"OK", "SEGMENTATION_FAULT", "SEGMENT_NOT_FOUND", "PROTECTION_FAULT"})
        target = Path(self.temp_dir.name) / "results.csv"
        with patch("src.gui.filedialog.asksaveasfilename", return_value=str(target)):
            self.app.export_button.invoke()
        self.wait_for_worker()
        with target.open(encoding="utf-8-sig", newline="") as source:
            rows = list(csv.DictReader(source))
        self.assertEqual(len(rows), 10)
        self.assertEqual(rows[0]["physical_address"], "1120")
        self.assertIn("5. Địa chỉ", rows[0]["trace"])
        self.error_dialog.assert_not_called()

    def test_bad_batch_preserves_previous_results(self):
        self.app.batch_sample_button.invoke()
        self.wait_for_worker()
        previous = self.app.batch_results
        path = self.csv_file("bad.csv", "segment_id,offset\n0,abc\n")
        self.app.run_batch_path(path)
        self.wait_for_worker()
        self.assertIs(self.app.batch_results, previous)
        self.assertEqual(len(self.app.batch_tree.get_children()), 10)
        self.error_dialog.assert_called_once()
        self.assertFalse(self.app.export_button.instate(["disabled"]))

    def test_batch_uses_snapshot_and_selected_row_uses_same_map(self):
        original = self.app.table
        self.app.run_batch_path(PROJECT_ROOT / "input" / "addresses.csv")
        self.app._replace_table(SegmentTable([Segment(0, 8000, 400)]), "changed")
        self.wait_for_worker()
        self.assertIs(self.app.batch_table, original)
        self.assertEqual(self.app.batch_results[0].physical_address, 1120)
        self.app.batch_tree.selection_set("0")
        self.app.show_batch_map()
        self.assertIs(self.app._map_table, original)
        self.assertEqual(self.app.table.segments[0].base, 8000)
        self.assertIn("đã chụp", self.app.status_var.get())

    def test_large_batch_caps_widgets_but_exports_all_rows(self):
        count = DISPLAY_LIMIT + 17
        path = self.csv_file("large.csv", "segment_id,offset\n" + "0,120\n" * count)
        self.app.run_batch_path(path)
        self.wait_for_worker()
        self.assertEqual(len(self.app.batch_tree.get_children()), DISPLAY_LIMIT)
        self.assertEqual(len(self.app.batch_results), count)
        target = Path(self.temp_dir.name) / "full.csv"
        with patch("src.gui.filedialog.asksaveasfilename", return_value=str(target)):
            self.app.export_button.invoke()
        self.wait_for_worker()
        with target.open(encoding="utf-8-sig", newline="") as source:
            self.assertEqual(len(list(csv.DictReader(source))), count)

    def test_huge_integer_map_and_translation_do_not_overflow(self):
        huge = 10 ** 400
        self.app._replace_table(SegmentTable([Segment(0, huge, huge)]), "huge values")
        self.app.address_segment_var.set("0")
        self.app.offset_var.set(str(huge - 1))
        self.app.translate_button.invoke()
        self.assertEqual(self.app.single_result.physical_address, huge * 2 - 1)
        self.assertTrue(self.app.map_canvas.find_all())
        self.error_dialog.assert_not_called()

    def test_cancelled_dialog_does_not_mutate_state(self):
        previous = self.app.table
        with patch("src.gui.filedialog.askopenfilename", return_value=""):
            self.app.load_segments_button.invoke()
            self.app.batch_run_button.invoke()
        self.assertIs(self.app.table, previous)
        self.assertFalse(self.app._job_running)
        self.error_dialog.assert_not_called()


if __name__ == "__main__":
    unittest.main()
