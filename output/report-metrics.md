# Số liệu thực nghiệm dùng trong báo cáo

Đo ngày 03/10/2026 trên **CPython 3.12.14, Windows 11, AMD64**, CPU được hệ điều hành nhận diện là Intel64 Family 6 Model 154 Stepping 3, GenuineIntel. Đây là số đo của môi trường thực nghiệm này; thời gian trên máy khác hoặc lần chạy khác có thể thay đổi.

## Đối chiếu tính đúng đắn

| Phép kiểm chứng | Kết quả thực tế |
|---|---|
| Bộ CSV mẫu đối chiếu với expected tính tay | **10/10 PASS** |
| Stress: 100.000 địa chỉ trên 1.000 segment | **PASS**, checksum và số trạng thái khớp công thức độc lập |
| Thời gian stress, một lượt streaming | **331,918 ms** |
| Trạng thái trong stress | OK: 39.520; không có segment: 9.940; vượt biên: 18.050; sai quyền: 32.490 |

Stress dùng lặp một bộ 10.000 địa chỉ đã tạo sẵn và không giữ toàn bộ kết quả/trace trong bộ nhớ. Thời gian stress bao gồm dịch địa chỉ, cập nhật số lượng trạng thái và checksum; không phải median và không trực tiếp tương đương phép đo batch bên dưới.

## Đo batch với 1.000 segment

Mỗi cấu hình dùng seed `12`, chạy warm-up một lượt rồi lấy **median 5 lượt** bằng `time.perf_counter`. Input và bảng được chuẩn bị trước phép đo dịch. Đơn vị trong bảng là **mili giây (ms)**; dấu chấm là dấu thập phân.

| Số địa chỉ | Dựng bảng | Dịch đầy đủ và trace | Chỉ tra cứu dict | Chỉ tra cứu tuyến tính |
|---:|---:|---:|---:|---:|
| 100 | 0.1388 | 0.2631 | 0.0074 | 0.8711 |
| 1.000 | 0.1308 | 2.6268 | 0.0701 | 9.6649 |
| 10.000 | 0.1326 | 32.2393 | 0.7285 | 96.3816 |

Dựng bảng gồm lập chỉ mục và kiểm tra chồng lấn, không gồm tạo đối tượng Segment. Dịch đầy đủ gồm kiểm tra giới hạn/quyền và tạo kết quả/trace; không gồm CSV hay GUI. Hai cột tra cứu dùng cùng danh sách ID và phép cộng checksum, đã kiểm tra đối tượng trả về tương đương trước khi đo. Tỷ lệ giữa hai cột này chỉ mô tả phần tra cứu.

Ở cấu hình 1.000 segment / 10.000 địa chỉ, peak cấp phát Python được `tracemalloc` ghi nhận cho một lượt dịch riêng là **8.735.226 byte**. Chỉ số này gồm kết quả/trace; không phải RAM toàn tiến trình và không gồm input/bảng đã tồn tại.

Nguồn số liệu trong repository: `output/verification.csv`, `output/benchmark.csv`, `output/system-info.json`. Phương pháp đầy đủ: `output/benchmark-summary.md`. Mã tái lập: `scripts/verify.py` và `scripts/benchmark.py`. Bảng này được tự động tạo lại khi benchmark hoàn tất; có thể cập nhật từ số đo đã lưu bằng `python scripts/report_metrics.py`.
