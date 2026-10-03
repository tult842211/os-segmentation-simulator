# OS_MEM_12 — Mô phỏng Segmentation và địa chỉ logic

Ứng dụng desktop bằng **Python + Tkinter** giúp quan sát cách một địa chỉ logic `(segment_id, offset)` được kiểm tra và chuyển thành địa chỉ vật lý. Ứng dụng có bảng segment, quyền `r/w/x`, sơ đồ bộ nhớ, trace từng bước, nhập/xuất CSV và bộ kiểm thử có thể chạy lại.

Đây là mô hình phục vụ học tập. Chương trình chỉ tính toán trên số nguyên và mô phỏng lỗi; không đọc/ghi bộ nhớ vật lý của máy.

[Đọc báo cáo PDF](report/OS_MEM_12_Report.pdf) · [Mã nguồn báo cáo](report/report.md)

## 1. Chạy trên Windows

Yêu cầu **Python 3.10 trở lên**, có Tkinter. Dự án sử dụng thư viện chuẩn của Python, không yêu cầu gói `pip` để chạy ứng dụng và kiểm thử.

1. Tải repository bằng **Code → Download ZIP** rồi giải nén, hoặc clone bằng Git.
2. Mở terminal trong thư mục chứa file `run.py`.
3. Kiểm tra Python và Tkinter:

```powershell
py --version
py -m tkinter
```

Lệnh kiểm tra Tkinter sẽ mở một cửa sổ nhỏ; đóng cửa sổ đó rồi chạy:

```powershell
py run.py
```

Có thể dùng `python run.py` hoặc `python -m src.main` nếu máy nhận lệnh `python` thay cho `py`. Nếu máy chưa có Python, cài từ [python.org](https://www.python.org/downloads/windows/) và bật thành phần Tcl/Tk trong trình cài đặt. Không cài một gói tên `tkinter` qua `pip`.

Sau khi đã cài Python, có thể nhấp đúp **`Start-Windows.cmd`** trong thư mục dự án để mở ứng dụng.

## 2. Thử nhanh

1. Trong tab **Dịch địa chỉ**, chọn **Nạp mẫu** hoặc **Mở segments.csv** để nạp bảng.
2. Nhập một địa chỉ hợp lệ, chọn **Dịch địa chỉ** để xem đủ trace, hoặc **Từng bước** rồi **Bước tiếp →** để xem lần lượt.
3. Đặt `offset` bằng `limit` để quan sát lỗi vượt giới hạn.
4. Thử ghi vào segment chỉ có quyền đọc/thực thi để quan sát lỗi bảo vệ.
5. Trong tab **Xử lý CSV**, chọn **Mở addresses.csv và chạy** hoặc **Chạy bộ địa chỉ mẫu**, sau đó **Xuất kết quả CSV**. File xuất chứa kết quả và trace trong cùng một CSV.

Bảng giao diện hiển thị tối đa **1.000 dòng đầu**; xuất CSV vẫn giữ **toàn bộ kết quả**. Sơ đồ hiển thị tối đa **10 segment**, có gồm segment đang chọn. Vùng quá nhỏ được vẽ rộng tối thiểu để nhìn thấy, nên hãy đọc giá trị số để xác định địa chỉ.

Quy tắc của mô hình:

```text
Tìm segment theo ID.
Nếu không tồn tại: SEGMENT_NOT_FOUND.
Nếu offset < 0 hoặc offset >= limit: SEGMENTATION_FAULT.
Nếu quyền truy cập không được cho phép: PROTECTION_FAULT.
Ngược lại: physical_address = base + offset, trạng thái OK.
```

`limit` là **độ dài**, không phải địa chỉ cuối. Một segment có `base = 1000`, `limit = 400` chiếm các địa chỉ từ `1000` đến `1399`. `offset = 399` hợp lệ, còn `offset = 400` không hợp lệ. Quyền được kiểm tra sau giới hạn; địa chỉ đồng thời vượt giới hạn và sai quyền sẽ được báo `SEGMENTATION_FAULT`.

## 3. Định dạng CSV

File dùng dấu phẩy làm dấu phân cách, hàng đầu là tên cột. Chương trình đọc dữ liệu UTF-8; dữ liệu xuất tương thích BOM UTF-8 để thuận tiện mở trong Excel. Các giá trị số dùng hệ thập phân, không dùng dấu phân cách hàng nghìn.

### Bảng segment

```csv
segment_id,base,limit,permissions
0,1000,400,rx
1,2000,300,rw
2,3000,500,rw
```

| Cột | Ý nghĩa | Điều kiện |
|---|---|---|
| `segment_id` | Mã segment | Số nguyên không âm, không trùng |
| `base` | Địa chỉ bắt đầu | Số nguyên không âm |
| `limit` | Độ dài segment | Số nguyên dương |
| `permissions` | Các quyền được phép | Cột tùy chọn; chuỗi không rỗng gồm `r`, `w`, `x` không lặp; nếu không có cột thì mặc định `rw` |

Mô hình của dự án chỉ xét một tiến trình và các vùng không chồng lấn. Hai vùng nằm sát nhau được chấp nhận; hai vùng có ít nhất một địa chỉ chung bị từ chối. Đây là lựa chọn của mô hình, không phải khẳng định mọi hệ thống segmentation đều cấm chia sẻ vùng nhớ.

### Địa chỉ cần dịch

```csv
segment_id,offset,access
0,120,r
0,399,x
0,400,r
0,20,w
9,10,r
```

| Cột | Ý nghĩa |
|---|---|
| `segment_id` | Segment muốn truy cập |
| `offset` | Độ lệch; được phép nhập số âm để kiểm thử lỗi địa chỉ |
| `access` | Một quyền `r`, `w` hoặc `x`; cột tùy chọn, nếu thiếu mặc định `r` |

Lỗi định dạng CSV được phân biệt với lỗi mô phỏng. Ví dụ, `offset = abc` là dữ liệu sai kiểu; `offset = -1` là một yêu cầu dịch đúng kiểu nhưng bị từ chối vì nằm ngoài segment.

### Kết quả và trace

Mỗi yêu cầu hợp lệ về định dạng có một kết quả gồm địa chỉ đầu vào, trạng thái, thông tin segment khi tìm thấy, địa chỉ vật lý nếu thành công và thông báo. Địa chỉ vật lý để trống khi có lỗi. Cột `trace` lưu các bước, ngăn bằng xuống dòng bên trong một ô CSV, để đối chiếu với giao diện.

```csv
segment_id,offset,access,base,limit,status,physical_address,message,trace
```

## 4. Kiểm thử và số liệu

Chạy từ thư mục gốc:

```powershell
py -m unittest discover -s tests -v
py scripts/verify.py
py scripts/benchmark.py
```

Các tài liệu minh chứng được lưu tại:

| File | Nội dung |
|---|---|
| [`input/expected_results.csv`](input/expected_results.csv) | Kết quả kỳ vọng được tính trước cho bộ mẫu |
| [`output/verification.csv`](output/verification.csv) | So sánh expected/actual theo từng trường hợp |
| [`output/test-results.txt`](output/test-results.txt) | Nhật ký lần chạy kiểm thử được lưu kèm dự án |
| [`output/benchmark.csv`](output/benchmark.csv) | Dữ liệu đo hiệu năng |
| [`output/benchmark-summary.md`](output/benchmark-summary.md) | Bảng tóm tắt và cách đọc số liệu |
| [`output/system-info.json`](output/system-info.json) | Môi trường dùng để đo |

Số liệu trong repository là một lần đo trên môi trường được ghi nhận. Khi chạy lại trên máy khác, thời gian có thể thay đổi. Kết quả đúng/sai cần khớp; thời gian chạy không cần giống hoàn toàn.

Benchmark phân biệt **thời gian tra cứu bảng** và **thời gian dịch đầy đủ**. Chỉ so sánh hai phép đo có cùng công việc. Chi phí Tkinter, đọc/ghi file và vẽ sơ đồ không được diễn giải thành chi phí của thuật toán dịch địa chỉ.

## 5. Cấu trúc dự án

```text
os-segmentation-simulator/
├── run.py                  # Điểm chạy ứng dụng
├── src/
│   ├── main.py             # Khởi động GUI
│   ├── segmentation.py     # Mô hình, kiểm tra bảng và dịch địa chỉ
│   ├── csv_io.py           # Đọc/xuất dữ liệu
│   └── gui.py              # Giao diện, trace, sơ đồ
├── input/                  # CSV mẫu và dữ liệu kỳ vọng
├── output/                 # Minh chứng kiểm thử và benchmark
├── tests/                  # Kiểm thử tự động
├── scripts/                # Xác minh, đo hiệu năng, tạo báo cáo
└── report/                 # Báo cáo, kịch bản demo, tài liệu bảo vệ
```

Logic mô phỏng được tách khỏi giao diện để có thể kiểm thử mà không mở cửa sổ. GUI dùng cùng phần lõi với kiểm thử và xác minh CSV.

## 6. Độ phức tạp và giới hạn

Gọi `S` là số segment, `A` là số địa chỉ. Kiểm tra chồng lấn bằng cách sắp xếp các khoảng tốn `O(S log S)`. Tra cứu bằng dictionary có thời gian trung bình `O(1)` cho mỗi địa chỉ; tra cứu tuần tự có thời gian xấu nhất `O(S)`. Dịch một lô bằng dictionary có thời gian kỳ vọng `O(A)` sau khi tạo bảng; lưu kết quả và trace làm tăng bộ nhớ theo số địa chỉ.

Chương trình dùng địa chỉ số nguyên trừu tượng, segment tăng theo chiều dương và thao tác một địa chỉ mỗi lần. Dự án chưa mô phỏng MMU thật, paging, TLB, stack tăng xuống, chia sẻ giữa nhiều tiến trình, cấp phát/thu hồi động, dồn bộ nhớ, độ trễ phần cứng hoặc truy cập nhiều byte vượt biên.

## 7. Báo cáo và hồ sơ nộp bài

- [Báo cáo PDF](report/OS_MEM_12_Report.pdf)
- [Báo cáo nguồn](report/report.md)
- [Kịch bản demo](report/demo-script.md)
- [Kế hoạch nhóm và bảng đóng góp](report/team-plan.md)
- [Câu hỏi chuẩn bị bảo vệ](report/defense-questions.md)
- [Tài liệu tham khảo](report/references.md)
- [Khai báo sử dụng AI](report/ai-disclosure.md)
- [Đề bài / bảng đăng ký](https://docs.google.com/spreadsheets/d/1PigNLKNb0rQIhPnzGMw1dEI2CuofGvee/edit?gid=1338212617#gid=1338212617)

Thông tin nhóm cần điền theo thực tế:

| Mục | Thông tin |
|---|---|
| Tên trường / khoa | ____________________ |
| Lớp / học phần | ____________________ |
| Giảng viên | ____________________ |
| Mã nhóm | ____________________ |
| Họ tên — MSSV thành viên | ____________________ |
| URL video demo | ____________________ |

Mã nguồn và tài liệu hỗ trợ đã được chuẩn bị trong dự án. Trước khi nộp, nhóm cần điền thông tin thật, chạy thử trên máy dùng để trình bày, đọc và giải thích được thuật toán, tự quay video demo, hoàn thiện phần đóng góp thực tế và đối chiếu yêu cầu hiện hành của giảng viên. Không biến kế hoạch đề xuất thành lịch sử công việc đã làm.

Nếu sửa nội dung báo cáo và muốn tạo lại PDF, cài các gói riêng cho công cụ xuất báo cáo rồi chạy:

```powershell
python -m pip install -r requirements-report.txt
python scripts/build_report.py
```

Các gói này chỉ cần khi tạo PDF; ứng dụng Tkinter và unit test vẫn dùng thư viện chuẩn. File tạo ra là `report/OS_MEM_12_Report.pdf`.

## 8. Làm việc với GitHub

Nên chia từng thay đổi thành commit có ý nghĩa: sửa kiểm tra biên, bổ sung ca test, chỉnh phần giải thích hoặc sửa giao diện. Thành viên clone repository, tạo nhánh, thay đổi, chạy test rồi mở pull request để người khác xem. Không cần tạo lại lịch sử commit theo tám tuần trong kế hoạch.

Nếu repository để riêng tư, cấp quyền cho giảng viên/người chấm theo hướng dẫn môn học. Đường dẫn riêng tư không tự trở thành truy cập được chỉ vì đã đặt trong báo cáo.
