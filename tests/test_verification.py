from pathlib import Path
import tempfile
import unittest

from scripts.benchmark import lookup_dict, lookup_linear, make_workload, stress_test
from scripts.verify import compare_results, load_expected
from src.segmentation import LogicalAddress, Segment, SegmentTable


class VerificationTests(unittest.TestCase):
    def setUp(self):
        self.table = SegmentTable([Segment(0, 1000, 400)])
        self.result = self.table.translate(LogicalAddress(0, 120))
        self.expected = [{"segment_id": "0", "offset": "120", "access": "r", "status": "OK", "physical_address": "1120"}]

    def test_matching_result_passes(self):
        self.assertEqual(compare_results([self.result], self.expected)[0]["passed"], "PASS")

    def test_wrong_value_fails(self):
        self.expected[0]["physical_address"] = "1121"
        row = compare_results([self.result], self.expected)[0]
        self.assertEqual(row["passed"], "FAIL")
        self.assertIn("physical_address", row["detail"])

    def test_wrong_input_identity_fails_even_if_answer_matches(self):
        self.expected[0]["offset"] = "121"
        self.assertEqual(compare_results([self.result], self.expected)[0]["passed"], "FAIL")

    def test_missing_actual_is_not_silently_ignored(self):
        self.assertEqual(compare_results([], self.expected)[0]["passed"], "FAIL")

    def test_extra_actual_is_not_silently_ignored(self):
        rows = compare_results([self.result, self.result], self.expected)
        self.assertEqual([row["passed"] for row in rows], ["PASS", "FAIL"])

    def test_empty_expected_file_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "expected.csv"
            path.write_text("segment_id,offset,access,status,physical_address\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_expected(path)

    def test_lookup_benchmarks_have_same_known_checksum(self):
        segments = [Segment(0, 0, 10), Segment(2, 100, 5)]
        ids = [0, 2, 8, 2]
        expected = 10 + 107 - 1 + 107
        self.assertEqual(lookup_dict({s.segment_id: s for s in segments}, ids), expected)
        self.assertEqual(lookup_linear(segments, ids), expected)

    def test_workload_reproducible_and_valid(self):
        self.assertEqual(make_workload(10, 100, 12), make_workload(10, 100, 12))
        segments, addresses = make_workload(10, 100, 12)
        self.assertEqual(len(SegmentTable(segments).translate_many(addresses)), 100)

    def test_small_stress_matches_independent_formula(self):
        result = stress_test(12, count=1000)
        self.assertEqual(result["independent_formula_check"], "PASS")
        self.assertEqual(sum(result["status_counts"].values()), 1000)


if __name__ == "__main__":
    unittest.main()
