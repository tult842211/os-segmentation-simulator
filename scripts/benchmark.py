"""Benchmark có seed cố định; chỉ số thời gian phụ thuộc máy và tải nền."""

import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import random
import statistics
import sys
from time import perf_counter
import tracemalloc
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.segmentation import LogicalAddress, Segment, SegmentTable
from scripts.report_metrics import write_report_metrics


def make_workload(segment_count: int, address_count: int, seed: int):
    rng = random.Random(seed)
    segments = [Segment(index, index * 256, 192, ("r", "rw", "rx")[index % 3]) for index in range(segment_count)]
    addresses = []
    for _ in range(address_count):
        segment_id = rng.randrange(segment_count) if rng.random() < 0.9 else segment_count + rng.randrange(10)
        kind = rng.randrange(10)
        offset = -1 if kind == 0 else 192 if kind == 1 else rng.randrange(192)
        addresses.append(LogicalAddress(segment_id, offset, rng.choice("rwx")))
    return segments, addresses


def lookup_dict(index: dict[int, Segment], ids: list[int]) -> int:
    checksum = 0
    for segment_id in ids:
        segment = index.get(segment_id)
        checksum += -1 if segment is None else segment.base + segment.limit + segment.segment_id
    return checksum


def lookup_linear(segments: list[Segment], ids: list[int]) -> int:
    checksum = 0
    for segment_id in ids:
        found = None
        for segment in segments:
            if segment.segment_id == segment_id:
                found = segment
                break
        checksum += -1 if found is None else found.base + found.limit + found.segment_id
    return checksum


def median_ms(operation: Callable, repeats: int) -> float:
    operation()  # Warm-up: không đưa vào thống kê.
    samples = []
    for _ in range(repeats):
        start = perf_counter()
        result = operation()
        samples.append((perf_counter() - start) * 1000)
        del result
    return statistics.median(samples)


def benchmark_case(segment_count: int, address_count: int, seed: int, repeats: int) -> dict:
    segments, addresses = make_workload(segment_count, address_count, seed)
    table = SegmentTable(segments)
    index = {segment.segment_id: segment for segment in segments}
    ids = [address.segment_id for address in addresses]
    # So sánh toàn bộ kết quả tra cứu từng ID, không chỉ checksum.
    expected_lookup = [next((segment for segment in segments if segment.segment_id == identifier), None) for identifier in ids]
    assert [index.get(identifier) for identifier in ids] == expected_lookup
    dict_checksum = lookup_dict(index, ids)
    assert dict_checksum == lookup_linear(segments, ids)
    results = table.translate_many(addresses)
    counts = Counter(result.status for result in results)
    del results
    build_ms = median_ms(lambda: SegmentTable(segments), repeats)
    translation_ms = median_ms(lambda: table.translate_many(addresses), repeats)
    dict_ms = median_ms(lambda: lookup_dict(index, ids), repeats)
    linear_ms = median_ms(lambda: lookup_linear(segments, ids), repeats)
    # Đo bộ nhớ ở lượt riêng; tracemalloc không làm nhiễu lượt đo thời gian.
    tracemalloc.start()
    memory_results = table.translate_many(addresses)
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    del memory_results
    return {
        "segments": segment_count, "addresses": address_count, "seed": seed, "repeats": repeats,
        "table_build_median_ms": round(build_ms, 6),
        "translation_median_ms": round(translation_ms, 6),
        "translation_addresses_per_second": round(address_count * 1000 / translation_ms, 2),
        "dict_lookup_median_ms": round(dict_ms, 6),
        "linear_lookup_median_ms": round(linear_ms, 6),
        "linear_over_dict_ratio": round(linear_ms / dict_ms, 3),
        "translation_peak_python_bytes": peak_bytes,
        "lookup_checksum": dict_checksum,
        "ok": counts["OK"], "segment_not_found": counts["SEGMENT_NOT_FOUND"],
        "segmentation_fault": counts["SEGMENTATION_FAULT"], "protection_fault": counts["PROTECTION_FAULT"],
    }


def stress_test(seed: int, count: int = 100000) -> dict:
    segments, addresses = make_workload(1000, 10000, seed)
    table = SegmentTable(segments)
    status_counts: Counter = Counter()
    physical_checksum = 0
    expected_counts: Counter = Counter()
    expected_checksum = 0
    # Oracle công thức độc lập cho layout do make_workload tạo.
    for i in range(count):
        address = addresses[i % len(addresses)]
        if address.segment_id >= 1000:
            expected_status = "SEGMENT_NOT_FOUND"
        elif address.offset < 0 or address.offset >= 192:
            expected_status = "SEGMENTATION_FAULT"
        elif address.access not in ("r", "rw", "rx")[address.segment_id % 3]:
            expected_status = "PROTECTION_FAULT"
        else:
            expected_status = "OK"
            expected_checksum += address.segment_id * 256 + address.offset
        expected_counts[expected_status] += 1
    start = perf_counter()
    for i in range(count):
        result = table.translate(addresses[i % len(addresses)])
        status_counts[result.status] += 1
        if result.physical_address is not None:
            physical_checksum += result.physical_address
    elapsed_ms = (perf_counter() - start) * 1000
    assert status_counts == expected_counts, (status_counts, expected_counts)
    assert physical_checksum == expected_checksum, (physical_checksum, expected_checksum)
    return {
        "addresses": count, "segments": 1000, "seed": seed,
        "streaming": True, "elapsed_ms": round(elapsed_ms, 3),
        "status_counts": dict(status_counts), "physical_checksum": physical_checksum,
        "independent_formula_check": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "output")
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--seed", type=int, default=12)
    args = parser.parse_args()
    if args.repeats < 5:
        parser.error("--repeats phải >= 5 để có thống kê median hợp lý.")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for segment_count in (10, 100, 1000):
        for address_count in (100, 1000, 10000):
            row = benchmark_case(segment_count, address_count, args.seed, args.repeats)
            rows.append(row)
            print(f"S={segment_count:4} A={address_count:5}: full={row['translation_median_ms']:.3f} ms; lookup ratio={row['linear_over_dict_ratio']:.2f}x", flush=True)
    with (args.output_dir / "benchmark.csv").open("w", encoding="utf-8-sig", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    stress = stress_test(args.seed)
    environment = {
        "measured_at_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": platform.python_version(), "implementation": platform.python_implementation(),
        "operating_system": platform.system(), "os_release": platform.release(),
        "architecture": platform.machine(), "processor": platform.processor(),
        "timer": "time.perf_counter", "seed": args.seed, "repeats": args.repeats,
        "stress_test": stress,
    }
    (args.output_dir / "system-info.json").write_text(json.dumps(environment, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Kết quả benchmark Segmentation", "",
        f"Đo thực tế bằng Python {environment['python_version']} / {environment['operating_system']} {environment['os_release']} / {environment['architecture']}.", "",
        "## Phương pháp", "",
        f"Seed `random.Random({args.seed})`; mỗi cấu hình warm-up một lượt rồi lấy median của {args.repeats} lượt. Mọi cấu hình dùng cùng seed, số segment và địa chỉ thay đổi theo bảng. Dữ liệu đã tạo trước lượt đo.", "",
        "- `table_build_median_ms`: dựng chỉ mục và kiểm tra bảng, bao gồm sắp xếp để phát hiện chồng lấn; các đối tượng Segment đã được tạo trước.",
        "- `translation_median_ms`: dịch toàn bộ danh sách, bao gồm kiểm tra biên/quyền, thông báo và trace, giữ danh sách kết quả trong lượt đo; không gồm CSV, GUI, dựng bảng hoặc sinh input.",
        "- Hai phép tra cứu dùng cùng danh sách ID, cùng phép cộng checksum, không tạo trace. Dict đã dựng trước; linear duyệt từ đầu danh sách segment. So sánh toàn bộ đối tượng tìm thấy và checksum trước khi đo. Tỷ lệ chỉ so sánh phần tra cứu, không được dùng để khẳng định tốc độ toàn ứng dụng.",
        "- `translation_peak_python_bytes`: peak các cấp phát Python được tracemalloc theo dõi trong một lượt dịch riêng, bao gồm danh sách kết quả/trace; không phải RAM toàn bộ tiến trình và không gồm input/bảng đã tồn tại.",
        "- Workload gồm địa chỉ hợp lệ, thiếu segment, vượt biên và lỗi quyền. Số lượng từng trạng thái nằm trong benchmark.csv. Thời gian phụ thuộc CPU, hệ điều hành, phiên bản Python và tải nền; không là bảo đảm thời gian thực.", "",
        "## Số đo", "", "| Segments | Addresses | Build (ms) | Dịch + trace (ms) | Dict (ms) | Linear (ms) | Linear / dict | Peak Python (KiB) |", "|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(f"| {row['segments']} | {row['addresses']} | {row['table_build_median_ms']:.4f} | {row['translation_median_ms']:.3f} | {row['dict_lookup_median_ms']:.4f} | {row['linear_lookup_median_ms']:.4f} | {row['linear_over_dict_ratio']:.2f}x | {row['translation_peak_python_bytes']/1024:.1f} |")
    lines += [
        "", "## Stress test", "",
        f"Dịch lần lượt {stress['addresses']:,} địa chỉ trên {stress['segments']} segment, dùng lặp workload 10.000 địa chỉ, không tích lũy kết quả/trace: {stress['elapsed_ms']:.3f} ms. Số trạng thái và checksum địa chỉ vật lý khớp oracle công thức độc lập: **PASS**. Thời gian stress là một lượt đo, không phải median.",
        "", "## Diễn giải", "",
        "Dựng bảng cần O(S log S) do kiểm tra chồng lấn; chỉ mục chiếm O(S). Với giả định phép toán số nguyên có chi phí hằng, tra cứu dictionary trung bình O(1), dịch A địa chỉ trung bình O(A), duyệt tuyến tính tra cứu O(A × S). Python hỗ trợ số nguyên lớn tùy ý nên chi phí phép toán và tạo chuỗi còn phụ thuộc số chữ số. Kết quả có trace được giữ trong bộ nhớ nên dung lượng tăng theo A; giao diện chỉ nên hiển thị số hàng vừa phải.",
        "", "Chạy lại: `python scripts/benchmark.py`. CSV và JSON ghi số đo thật của lần chạy gần nhất.", "",
    ]
    (args.output_dir / "benchmark-summary.md").write_text("\n".join(lines), encoding="utf-8")
    write_report_metrics(args.output_dir)
    print(f"Stress {stress['addresses']}: {stress['independent_formula_check']}. Saved benchmark.csv, benchmark-summary.md, system-info.json, report-metrics.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
