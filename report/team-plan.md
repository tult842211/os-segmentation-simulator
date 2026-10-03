# Kế hoạch nhóm và đóng góp thực tế

## Kế hoạch tám tuần — đề xuất

Đây là lịch đề xuất để nhóm học, kiểm chứng và hoàn thiện dự án. Nó không khẳng định tám tuần đã diễn ra, không phải bảng chấm công và không phải hướng dẫn tạo commit lùi ngày. Điều chỉnh theo thời hạn thực tế của học phần.

| Tuần | Mục tiêu | Sản phẩm kiểm tra được |
|---|---|---|
| 1 | Đọc đề; thống nhất segment, offset, limit, quyền | Bảng yêu cầu; ví dụ tính tay; giả định được ghi rõ |
| 2 | Hiểu phần lõi và kiểm tra bảng | Giải thích được các nhánh; test ID trùng, chồng lấn, sát biên |
| 3 | Xác minh CSV và xử lý dữ liệu sai | File mẫu tự tạo; expected/actual; lỗi có vị trí dễ tìm |
| 4 | Chạy và rà soát GUI | Checklist thao tác; ảnh minh chứng do nhóm chụp |
| 5 | Kiểm thử mở rộng | Test hồi quy cho lỗi tìm thấy; nhật ký chạy lại |
| 6 | Đo hiệu năng và phân tích | CSV số liệu, môi trường, so sánh có cùng điều kiện |
| 7 | Hoàn thiện báo cáo và tài liệu | Báo cáo có nguồn, giả định, giới hạn và minh chứng thật |
| 8 | Tập bảo vệ và quay demo | Video thật; thông tin nhóm; rà soát hồ sơ nộp |

## Gợi ý chia việc

Với ba thành viên: một người phụ trách lõi/kiểm thử, một người GUI/CSV, một người thực nghiệm/tài liệu. Tất cả cùng đọc phần lõi, tự giải thích ít nhất một ca biên và kiểm tra chéo phần của người khác. Nếu chỉ có một người, làm lần lượt theo các nhóm việc này; không tạo thêm thành viên giả.

Đóng góp được tính theo công việc thực tế, chẳng hạn phát hiện lỗi, viết ca test mới, sửa tài liệu, chạy đo trên máy nhóm, rà soát pull request hoặc quay demo. Không chỉ căn cứ vào số dòng code hoặc số commit.

## Bảng đóng góp thực tế — chưa điền

| Họ tên | MSSV | Công việc thực tế | Minh chứng: commit/PR/file/video | Người kiểm tra | Ngày hoàn thành |
|---|---|---|---|---|---|
| ____________________ | ____________________ | ____________________ | ____________________ | ____________________ | ____________________ |
| ____________________ | ____________________ | ____________________ | ____________________ | ____________________ | ____________________ |
| ____________________ | ____________________ | ____________________ | ____________________ | ____________________ | ____________________ |

## Nhật ký nhóm — ghi sau khi làm

| Ngày thực tế | Người thực hiện | Việc đã làm | Kết quả / lỗi tìm thấy | Liên kết minh chứng |
|---|---|---|---|---|
| ____________________ | ____________________ | ____________________ | ____________________ | ____________________ |

## Hoàn tất trước khi nộp

- Điền tên, MSSV, lớp, giảng viên và mã nhóm trong README/báo cáo.
- Chạy `py -m unittest discover -s tests -v`, `py scripts/verify.py`, `py scripts/benchmark.py` trên máy nhóm.
- Lưu nhật ký và kiểm tra các file trong `output/`; không tự sửa số liệu để đẹp hơn.
- Thử mở ứng dụng từ một bản clone/ZIP sạch, không phụ thuộc đường dẫn cá nhân.
- Thử quyền truy cập repository bằng tài khoản mà giảng viên sử dụng hoặc cấp quyền theo yêu cầu.
- Tự quay demo, kiểm tra link phát được và điền URL vào README/báo cáo.
- Đọc lại khai báo AI và thay mẫu bằng nội dung đúng thực tế.
- Mỗi thành viên tự giải thích `offset = limit − 1` và `offset = limit`, quyền `w` trên segment `rx`, và vì sao một kết quả lỗi không có địa chỉ vật lý.
