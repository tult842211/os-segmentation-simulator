# Kết quả benchmark Segmentation

Đo thực tế bằng Python 3.12.14 / Windows 11 / AMD64.

## Phương pháp

Seed `random.Random(12)`; mỗi cấu hình warm-up một lượt rồi lấy median của 5 lượt. Mọi cấu hình dùng cùng seed, số segment và địa chỉ thay đổi theo bảng. Dữ liệu đã tạo trước lượt đo.

- `table_build_median_ms`: dựng chỉ mục và kiểm tra bảng, bao gồm sắp xếp để phát hiện chồng lấn; các đối tượng Segment đã được tạo trước.
- `translation_median_ms`: dịch toàn bộ danh sách, bao gồm kiểm tra biên/quyền, thông báo và trace, giữ danh sách kết quả trong lượt đo; không gồm CSV, GUI, dựng bảng hoặc sinh input.
- Hai phép tra cứu dùng cùng danh sách ID, cùng phép cộng checksum, không tạo trace. Dict đã dựng trước; linear duyệt từ đầu danh sách segment. So sánh toàn bộ đối tượng tìm thấy và checksum trước khi đo. Tỷ lệ chỉ so sánh phần tra cứu, không được dùng để khẳng định tốc độ toàn ứng dụng.
- `translation_peak_python_bytes`: peak các cấp phát Python được tracemalloc theo dõi trong một lượt dịch riêng, bao gồm danh sách kết quả/trace; không phải RAM toàn bộ tiến trình và không gồm input/bảng đã tồn tại.
- Workload gồm địa chỉ hợp lệ, thiếu segment, vượt biên và lỗi quyền. Số lượng từng trạng thái nằm trong benchmark.csv. Thời gian phụ thuộc CPU, hệ điều hành, phiên bản Python và tải nền; không là bảo đảm thời gian thực.

## Số đo

| Segments | Addresses | Build (ms) | Dịch + trace (ms) | Dict (ms) | Linear (ms) | Linear / dict | Peak Python (KiB) |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 100 | 0.0024 | 0.403 | 0.0121 | 0.0289 | 2.39x | 83.4 |
| 10 | 1000 | 0.0024 | 2.670 | 0.1129 | 0.2421 | 2.14x | 818.1 |
| 10 | 10000 | 0.0025 | 33.289 | 0.7589 | 2.2506 | 2.97x | 8382.8 |
| 100 | 100 | 0.0156 | 0.274 | 0.0068 | 0.1089 | 16.02x | 82.6 |
| 100 | 1000 | 0.0168 | 2.849 | 0.0622 | 1.0157 | 16.33x | 821.6 |
| 100 | 10000 | 0.0151 | 29.906 | 0.6074 | 10.6500 | 17.53x | 8444.8 |
| 1000 | 100 | 0.1388 | 0.263 | 0.0074 | 0.8711 | 117.72x | 85.1 |
| 1000 | 1000 | 0.1308 | 2.627 | 0.0701 | 9.6649 | 137.87x | 828.1 |
| 1000 | 10000 | 0.1326 | 32.239 | 0.7285 | 96.3816 | 132.30x | 8530.5 |

## Stress test

Dịch lần lượt 100,000 địa chỉ trên 1000 segment, dùng lặp workload 10.000 địa chỉ, không tích lũy kết quả/trace: 331.918 ms. Số trạng thái và checksum địa chỉ vật lý khớp oracle công thức độc lập: **PASS**. Thời gian stress là một lượt đo, không phải median.

## Diễn giải

Dựng bảng cần O(S log S) do kiểm tra chồng lấn; chỉ mục chiếm O(S). Với giả định phép toán số nguyên có chi phí hằng, tra cứu dictionary trung bình O(1), dịch A địa chỉ trung bình O(A), duyệt tuyến tính tra cứu O(A × S). Python hỗ trợ số nguyên lớn tùy ý nên chi phí phép toán và tạo chuỗi còn phụ thuộc số chữ số. Kết quả có trace được giữ trong bộ nhớ nên dung lượng tăng theo A; giao diện chỉ nên hiển thị số hàng vừa phải.

Chạy lại: `python scripts/benchmark.py`. CSV và JSON ghi số đo thật của lần chạy gần nhất.
