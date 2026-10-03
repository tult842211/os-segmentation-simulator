# Kịch bản demo Topic 12

Thời lượng gợi ý: **5–7 phút**. Đây là kịch bản để nhóm tự quay; dự án không coi tài liệu này là video đã hoàn thành.

**Người trình bày:** ____________________  
**Ngày quay thực tế:** ____________________  
**URL video:** ____________________

## Chuẩn bị

Chạy `py run.py`, mở sẵn CSV mẫu và terminal tại thư mục repository. Kiểm tra cỡ chữ/độ phân giải đủ rõ khi quay. Chuẩn bị bảng mẫu sau; có thể tạo một CSV riêng nếu dữ liệu mặc định của ứng dụng khác:

```csv
segment_id,base,limit,permissions
0,1000,400,rx
1,2000,300,rw
2,3000,500,rw
```

## 0:00–0:40 — Giới thiệu bài toán

Nêu tên đề tài, thành viên thực tế và mục tiêu: mô phỏng dịch địa chỉ `(segment_id, offset)`, kiểm tra giới hạn và quyền. Chỉ vào hai file đầu vào. Giải thích `base = 1000`, `limit = 400` nghĩa là 400 vị trí, từ 1000 đến 1399.

## 0:40–1:40 — Trường hợp bình thường

Nạp bảng segment. Nhập ID `0`, offset `120`, quyền `r`. Trước khi bấm dịch, nói kết quả kỳ vọng `1000 + 120 = 1120`. Sau khi chạy, chỉ vào trạng thái `OK`, địa chỉ vật lý, trace kiểm tra và vị trí trên sơ đồ. Nêu rằng phần mềm chỉ mô phỏng con số, không truy cập địa chỉ 1120 trên máy thật.

## 1:40–2:40 — Kiểm tra biên và segment không tồn tại

Lần lượt dùng segment `0` với offset `399` rồi `400`. Kết quả kỳ vọng là `1399` và `SEGMENTATION_FAULT`. Nêu lý do điều kiện là `< limit`, không phải `<= limit`. Sau đó dùng segment `9`, offset `10` để nhận `SEGMENT_NOT_FOUND`. Chỉ ra ô địa chỉ vật lý để trống khi lỗi.

## 2:40–3:20 — Kiểm tra bảo vệ

Dùng segment `0`, offset `20`, quyền `w`. Vì segment có quyền `rx`, kết quả là `PROTECTION_FAULT`. Giữ offset 20 và đổi sang `x` để nhận `OK`, địa chỉ `1020`. Nhấn mạnh cùng một vị trí có thể đọc/thực thi được nhưng không được ghi, tùy quyền trong bảng.

## 3:20–4:10 — Chạy CSV và xuất minh chứng

Chuyển sang tab **Xử lý CSV**, chọn **Mở addresses.csv và chạy** hoặc **Chạy bộ địa chỉ mẫu**. Chọn một dòng để đọc trace. Bấm **Xuất kết quả CSV**, lưu file mới trong `output/`, rồi mở file để chỉ header và một dòng thành công/một dòng lỗi. Trace nằm ở cột cuối trong cùng CSV. Có thể dùng một file thiếu cột để minh họa thông báo lỗi dữ liệu; dữ liệu sai định dạng cần được sửa trước khi mô phỏng.

## 4:10–5:10 — Kiểm thử và hiệu năng

Chạy `py -m unittest discover -s tests -v` và `py scripts/verify.py`. Đọc kết quả thực tế trên màn hình. Mở `output/verification.csv` để chỉ expected/actual. Mở `output/benchmark-summary.md`, nêu một giá trị đo thật cùng số segment, số địa chỉ, đơn vị và môi trường. Không đọc số liệu trong kịch bản như thể đã đo.

Giải thích ngắn: dictionary tra ID có chi phí trung bình `O(1)`; tìm tuyến tính có thể xét đến `S` mục. Các phép đo tra cứu cần được so sánh với nhau, không so tra cứu đơn thuần với cả GUI hoặc cả quá trình đọc file.

## 5:10–6:10 — Cấu trúc, giới hạn và đóng góp

Mở phần lõi để chỉ thứ tự kiểm tra; cho thấy GUI, CSV và test nằm ở các module khác nhau. Nêu giới hạn: một tiến trình, không chia sẻ/chồng lấn, không paging hoặc cấp phát động. Trình bày đóng góp thực tế của thành viên, các phần AI hỗ trợ và việc nhóm đã kiểm chứng.

## Kiểm tra video trước khi nộp

- Âm thanh nghe rõ, tên cột và kết quả đọc được.
- Có ít nhất ca bình thường, ca biên và ca lỗi; kết quả nói ra trùng màn hình.
- Có demo CSV, GUI, test và số liệu thực tế.
- Link video phát được theo quyền truy cập yêu cầu; đã điền URL vào hồ sơ.
- Không để lộ token GitHub, mật khẩu hoặc thông tin tài khoản trong cửa sổ terminal/trình duyệt.
