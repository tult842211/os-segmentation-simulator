"""Đối chiếu kết quả thật với bộ expected tính tay; sai khác trả exit code 1."""

import argparse
import csv
from pathlib import Path
import sys
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.csv_io import load_addresses, load_segments
from src.segmentation import SegmentTable, TranslationResult

EXPECTED_FIELDS = ("segment_id", "offset", "access", "status", "physical_address")
REPORT_FIELDS = (
    "case", "expected_segment_id", "actual_segment_id", "expected_offset", "actual_offset",
    "expected_access", "actual_access", "expected_status", "actual_status",
    "expected_physical_address", "actual_physical_address", "passed", "detail",
)


def load_expected(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source, strict=True)
        if reader.fieldnames != list(EXPECTED_FIELDS):
            raise ValueError(f"Expected CSV phải có các cột theo thứ tự: {','.join(EXPECTED_FIELDS)}")
        rows = list(reader)
    if not rows:
        raise ValueError("Expected CSV chưa có trường hợp kiểm thử.")
    for row in rows:
        if None in row or any(value is None for value in row.values()):
            raise ValueError("Expected CSV có dòng thừa hoặc thiếu ô.")
    return rows


def compare_results(
    results: Iterable[TranslationResult], expected: list[dict[str, str]],
) -> list[dict[str, str]]:
    actual = [
        {
            "segment_id": str(result.segment_id),
            "offset": str(result.offset),
            "access": result.access,
            "status": result.status,
            "physical_address": "" if result.physical_address is None else str(result.physical_address),
        }
        for result in results
    ]
    report = []
    for index in range(max(len(expected), len(actual))):
        wanted = expected[index] if index < len(expected) else {}
        received = actual[index] if index < len(actual) else {}
        different = [field for field in EXPECTED_FIELDS if wanted.get(field) != received.get(field)]
        detail = ", ".join(different)
        if not wanted:
            detail = "Có kết quả thực tế thừa so với expected."
        elif not received:
            detail = "Thiếu kết quả thực tế so với expected."
        row = {"case": str(index + 1), "passed": "PASS" if wanted == received else "FAIL", "detail": detail}
        for field in EXPECTED_FIELDS:
            row[f"expected_{field}"] = wanted.get(field, "")
            row[f"actual_{field}"] = received.get(field, "")
        report.append(row)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--segments", type=Path, default=ROOT / "input" / "segments.csv")
    parser.add_argument("--addresses", type=Path, default=ROOT / "input" / "addresses.csv")
    parser.add_argument("--expected", type=Path, default=ROOT / "input" / "expected_results.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "output" / "verification.csv")
    args = parser.parse_args()
    try:
        table = SegmentTable(load_segments(args.segments))
        results = table.translate_many(load_addresses(args.addresses))
        report = compare_results(results, load_expected(args.expected))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8-sig", newline="") as target:
            writer = csv.DictWriter(target, fieldnames=REPORT_FIELDS)
            writer.writeheader()
            writer.writerows(report)
    except (OSError, ValueError, csv.Error) as exc:
        print(f"Verification error: {exc}", file=sys.stderr)
        return 2
    passed = sum(row["passed"] == "PASS" for row in report)
    print(f"Verification: {passed}/{len(report)} PASS. Output: {args.output.name}")
    return 0 if passed == len(report) else 1


if __name__ == "__main__":
    raise SystemExit(main())
