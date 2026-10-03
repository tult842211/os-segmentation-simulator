# Bàn giao trạng thái OS_MEM_12

Ngày lưu: 03/10/2026, 23:47, giờ Việt Nam.

Dự án Topic 12 đã có mã nguồn Python + Tkinter, đọc/xuất CSV, trace từng bước, sơ đồ bộ nhớ, xử lý batch, kiểm thử và báo cáo. Repository GitHub đích là [tult842211/os-segmentation-simulator](https://github.com/tult842211/os-segmentation-simulator), hiện cần commit/push mã nguồn.

## Bằng chứng đã lưu

- `output/test-results.txt`: 65/65 kiểm thử đạt, gồm 13 kiểm thử GUI trên Windows.
- `output/verification.csv`: 10/10 trường hợp expected/actual PASS.
- `output/benchmark.csv`: chín cấu hình, median năm lượt.
- `output/benchmark-summary.md`: phương pháp và kết quả đo.
- `output/system-info.json`: môi trường đo, không chứa đường dẫn riêng tư.
- `report/OS_MEM_12_Report.pdf`: báo cáo 12 trang; bản nguồn là `report/report.md`.

## Việc phải điền trước khi nộp

Tên trường, lớp, giảng viên, mã nhóm, họ tên/MSSV, ngày nộp, đóng góp thực tế và URL video demo phải lấy từ nhóm. Các dòng trống trong báo cáo là có chủ ý.

## Lệnh kiểm tra lại

```powershell
py -m unittest discover -s tests -v
py scripts/verify.py
py scripts/benchmark.py
py scripts/build_report.py
```

Sau khi thay đổi mã hoặc dữ liệu, chạy lại các lệnh liên quan và cập nhật các tệp trong `output/` trước khi nộp.
