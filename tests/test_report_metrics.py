import csv
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import benchmark
from scripts.report_metrics import write_report_metrics


class ReportMetricsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output_dir = Path(self.temp.name)
        self.row = {
            "segments": 1000, "addresses": 10000, "seed": 12, "repeats": 5,
            "table_build_median_ms": 0.1388, "translation_median_ms": 32.2393,
            "dict_lookup_median_ms": 0.7285, "linear_lookup_median_ms": 96.3816,
            "translation_peak_python_bytes": 8735226,
        }
        self.stress = {
            "addresses": 100000, "segments": 1000, "seed": 12, "streaming": True,
            "elapsed_ms": 331.918,
            "status_counts": {"OK": 39520, "SEGMENT_NOT_FOUND": 9940,
                              "SEGMENTATION_FAULT": 18050, "PROTECTION_FAULT": 32490},
            "independent_formula_check": "PASS",
        }
        self.environment = {
            "measured_at_utc": "2026-10-03T23:30:00+00:00",
            "python_version": "3.12.14", "implementation": "CPython",
            "operating_system": "Windows", "os_release": "11", "architecture": "AMD64",
            "processor": "Test CPU", "timer": "time.perf_counter", "seed": 12, "repeats": 5,
            "stress_test": self.stress,
        }
        self.write_artifacts()
        self.write_verification(["PASS", "PASS"])

    def write_artifacts(self):
        with (self.output_dir / "benchmark.csv").open("w", encoding="utf-8-sig", newline="") as target:
            writer = csv.DictWriter(target, fieldnames=list(self.row))
            writer.writeheader()
            writer.writerow(self.row)
        (self.output_dir / "system-info.json").write_text(json.dumps(self.environment), encoding="utf-8")

    def write_verification(self, statuses):
        with (self.output_dir / "verification.csv").open("w", encoding="utf-8-sig", newline="") as target:
            writer = csv.DictWriter(target, fieldnames=["case", "passed"])
            writer.writeheader()
            writer.writerows({"case": i, "passed": status} for i, status in enumerate(statuses, 1))

    def test_refresh_replaces_old_numbers_with_latest_saved_measurements(self):
        path = write_report_metrics(self.output_dir)
        first = path.read_text(encoding="utf-8")
        self.assertIn("32.2393", first)
        self.assertIn("Đo ngày 04/10/2026", first)  # Vietnam date, rather than the UTC date.
        self.row["translation_median_ms"] = 55.4321
        self.row["translation_peak_python_bytes"] = 12345678
        self.stress["elapsed_ms"] = 456.789
        self.stress["status_counts"]["OK"] = 12345
        self.environment["python_version"] = "3.13.0"
        self.write_artifacts()
        write_report_metrics(self.output_dir)
        current = path.read_text(encoding="utf-8")
        self.assertNotIn("32.2393", current)
        for expected in ("55.4321", "12.345.678 byte", "456,789 ms", "OK: 12.345", "CPython 3.13.0"):
            self.assertIn(expected, current)
        self.assertTrue(current.startswith("# Số liệu thực nghiệm dùng trong báo cáo\n"))
        self.assertIn("## Đo batch với 1.000 segment", current)

    def test_failed_or_missing_verification_never_claims_all_cases_passed(self):
        self.write_verification(["PASS", "FAIL"])
        path = write_report_metrics(self.output_dir)
        self.assertIn("**1/2 FAIL**", path.read_text(encoding="utf-8"))
        self.write_verification([])
        write_report_metrics(self.output_dir)
        self.assertIn("Chưa có trường hợp kiểm chứng", path.read_text(encoding="utf-8"))
        (self.output_dir / "verification.csv").unlink()
        write_report_metrics(self.output_dir)
        self.assertIn("Chưa có verification.csv", path.read_text(encoding="utf-8"))

    def test_benchmark_completion_refreshes_snippet_without_manual_command(self):
        def measured_case(segment_count, address_count, seed, repeats):
            row = dict(self.row)
            row.update(segments=segment_count, addresses=address_count, seed=seed,
                       repeats=repeats, linear_over_dict_ratio=3.0)
            return row
        with patch("sys.argv", ["benchmark.py", "--output-dir", str(self.output_dir)]), \
                patch("scripts.benchmark.benchmark_case", side_effect=measured_case), \
                patch("scripts.benchmark.stress_test", return_value=self.stress), \
                patch("builtins.print"):
            self.assertEqual(benchmark.main(), 0)
        snippet = (self.output_dir / "report-metrics.md").read_text(encoding="utf-8")
        self.assertIn("32.2393", snippet)
        self.assertIn("**2/2 PASS**", snippet)
        self.assertIn("331,918 ms", snippet)


if __name__ == "__main__":
    unittest.main()
