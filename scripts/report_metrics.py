"""Generate the report's measured-results section from saved CSV/JSON artifacts.

This command refreshes the report snippet without rerunning the benchmark.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source, strict=True))


def _count(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def render_report_metrics(output_dir: Path) -> str:
    """Read the current artifacts; never reuse an older Markdown snippet."""
    rows = _read_csv(output_dir / "benchmark.csv")
    environment = json.loads((output_dir / "system-info.json").read_text(encoding="utf-8-sig"))
    batch_rows = sorted(
        (row for row in rows if int(row["segments"]) == 1000),
        key=lambda row: int(row["addresses"]),
    )
    if not batch_rows:
        raise ValueError("benchmark.csv chưa có số đo cho 1.000 segment.")

    verification_path = output_dir / "verification.csv"
    if verification_path.exists():
        verification = _read_csv(verification_path)
        if verification:
            passed = sum(row["passed"] == "PASS" for row in verification)
            verdict = "PASS" if passed == len(verification) else "FAIL"
            verification_text = f"**{passed}/{len(verification)} {verdict}**"
        else:
            verification_text = "Chưa có trường hợp kiểm chứng trong verification.csv."
    else:
        verification_text = "Chưa có verification.csv; cần chạy scripts/verify.py."

    measured_at = datetime.fromisoformat(environment["measured_at_utc"].replace("Z", "+00:00"))
    measured_date = measured_at.astimezone(timezone(timedelta(hours=7))).strftime("%d/%m/%Y")
    stress = environment["stress_test"]
    stress_passed = stress["independent_formula_check"] == "PASS"
    stress_text = (
        "**PASS**, checksum và số trạng thái khớp công thức độc lập"
        if stress_passed else "**FAIL**, kiểm tra công thức độc lập không đạt"
    )
    counts = stress["status_counts"]
    elapsed = f"{float(stress['elapsed_ms']):.3f}".replace(".", ",")
    lines = [
        "# Số liệu thực nghiệm dùng trong báo cáo", "",
        f"Đo ngày {measured_date} trên **{environment['implementation']} {environment['python_version']}, "
        f"{environment['operating_system']} {environment['os_release']}, {environment['architecture']}**, "
        f"CPU được hệ điều hành nhận diện là {environment['processor']}. Đây là số đo của môi trường "
        "thực nghiệm này; thời gian trên máy khác hoặc lần chạy khác có thể thay đổi.", "",
        "## Đối chiếu tính đúng đắn", "",
        "| Phép kiểm chứng | Kết quả thực tế |", "|---|---|",
        f"| Bộ CSV mẫu đối chiếu với expected tính tay | {verification_text} |",
        f"| Stress: {_count(stress['addresses'])} địa chỉ trên {_count(stress['segments'])} segment | {stress_text} |",
        f"| Thời gian stress, một lượt streaming | **{elapsed} ms** |",
        f"| Trạng thái trong stress | OK: {_count(counts.get('OK', 0))}; không có segment: "
        f"{_count(counts.get('SEGMENT_NOT_FOUND', 0))}; vượt biên: {_count(counts.get('SEGMENTATION_FAULT', 0))}; "
        f"sai quyền: {_count(counts.get('PROTECTION_FAULT', 0))} |", "",
        "Stress dùng lặp một bộ 10.000 địa chỉ đã tạo sẵn và không giữ toàn bộ kết quả/trace trong bộ nhớ. "
        "Thời gian stress bao gồm dịch địa chỉ, cập nhật số lượng trạng thái và checksum; không phải median "
        "và không trực tiếp tương đương phép đo batch bên dưới.", "",
        "## Đo batch với 1.000 segment", "",
        f"Mỗi cấu hình dùng seed `{environment['seed']}`, chạy warm-up một lượt rồi lấy **median "
        f"{environment['repeats']} lượt** bằng `{environment['timer']}`. Input và bảng được chuẩn bị trước "
        "phép đo dịch. Đơn vị trong bảng là **mili giây (ms)**; dấu chấm là dấu thập phân.", "",
        "| Số địa chỉ | Dựng bảng | Dịch đầy đủ và trace | Chỉ tra cứu dict | Chỉ tra cứu tuyến tính |",
        "|---:|---:|---:|---:|---:|",
    ]
    for row in batch_rows:
        lines.append(
            f"| {_count(int(row['addresses']))} | {float(row['table_build_median_ms']):.4f} | "
            f"{float(row['translation_median_ms']):.4f} | {float(row['dict_lookup_median_ms']):.4f} | "
            f"{float(row['linear_lookup_median_ms']):.4f} |"
        )
    largest = batch_rows[-1]
    lines += [
        "", "Dựng bảng gồm lập chỉ mục và kiểm tra chồng lấn, không gồm tạo đối tượng Segment. "
        "Dịch đầy đủ gồm kiểm tra giới hạn/quyền và tạo kết quả/trace; không gồm CSV hay GUI. Hai cột "
        "tra cứu dùng cùng danh sách ID và phép cộng checksum, đã kiểm tra đối tượng trả về tương đương "
        "trước khi đo. Tỷ lệ giữa hai cột này chỉ mô tả phần tra cứu.", "",
        f"Ở cấu hình 1.000 segment / {_count(int(largest['addresses']))} địa chỉ, peak cấp phát Python "
        f"được `tracemalloc` ghi nhận cho một lượt dịch riêng là "
        f"**{_count(int(largest['translation_peak_python_bytes']))} byte**. Chỉ số này gồm kết quả/trace; "
        "không phải RAM toàn tiến trình và không gồm input/bảng đã tồn tại.", "",
        "Nguồn số liệu trong repository: `output/verification.csv`, `output/benchmark.csv`, "
        "`output/system-info.json`. Phương pháp đầy đủ: `output/benchmark-summary.md`. Mã tái lập: "
        "`scripts/verify.py` và `scripts/benchmark.py`. Bảng này được tự động tạo lại khi benchmark "
        "hoàn tất; có thể cập nhật từ số đo đã lưu bằng `python scripts/report_metrics.py`.", "",
    ]
    return "\n".join(lines)


def write_report_metrics(output_dir: Path) -> Path:
    text = render_report_metrics(output_dir)
    target = output_dir / "report-metrics.md"
    target.write_text(text, encoding="utf-8")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "output")
    args = parser.parse_args()
    try:
        path = write_report_metrics(args.output_dir)
    except (OSError, ValueError, KeyError, csv.Error) as exc:
        print(f"Report metrics error: {exc}", file=sys.stderr)
        return 2
    print(f"Updated {path.name} from saved measurements.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
