# Tài liệu tham khảo

Các đường dẫn dưới đây đã được mở để kiểm tra vào ngày **03/10/2026**. Nhóm nên kiểm tra lại trước khi nộp. Ngày này là ngày kiểm tra tài liệu của bản dự án, không phải ngày nhóm hoàn thành học phần.

1. **Remzi H. Arpaci-Dusseau, Andrea C. Arpaci-Dusseau. _Operating Systems: Three Easy Pieces_, Chapter 16: Segmentation.** University of Wisconsin–Madison. [PDF chương chính thức](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-segmentation.pdf), [trang sách](https://pages.cs.wisc.edu/~remzi/OSTEP/). Dùng để tham khảo base/bounds, giới hạn segment, quyền truy cập và phân mảnh ngoài. Mô hình của dự án đơn giản hơn chương sách: chỉ một tiến trình và segment tăng theo chiều dương.
2. **Abraham Silberschatz, Peter Baer Galvin, Greg Gagne. _Operating System Concepts_, 10th edition.** [Trang sách chính thức của tác giả](https://www.os-book.com/OS10/). Nguồn học thuật bổ sung để đặt bài toán vào chủ đề quản lý bộ nhớ. Không dùng trang giới thiệu sách làm bằng chứng rằng đã đọc toàn bộ nội dung sách.
3. **Python Software Foundation. _tkinter — Python interface to Tcl/Tk_.** [Tài liệu chính thức](https://docs.python.org/3/library/tkinter.html). Tham khảo cách dùng Tkinter, vòng lặp sự kiện và kiểm tra cài đặt bằng `python -m tkinter`.
4. **Python Software Foundation. _csv — CSV File Reading and Writing_.** [Tài liệu chính thức](https://docs.python.org/3/library/csv.html). Tham khảo đọc/ghi CSV theo tên cột và xử lý newline.
5. **Python Software Foundation. _unittest — Unit testing framework_.** [Tài liệu chính thức](https://docs.python.org/3/library/unittest.html). Tham khảo tổ chức ca kiểm thử và khám phá test bằng `python -m unittest discover`.
6. **Python Software Foundation. _time — Time access and conversions_.** [Mục `time.perf_counter`](https://docs.python.org/3/library/time.html#time.perf_counter). Tham khảo đồng hồ dùng đo khoảng thời gian ngắn; chỉ hiệu của hai giá trị có ý nghĩa trong phép đo.
7. **Bảng đề tài học phần do người dùng cung cấp.** [Google Sheets — tab `gid=1338212617`](https://docs.google.com/spreadsheets/d/1PigNLKNb0rQIhPnzGMw1dEI2CuofGvee/edit?gid=1338212617#gid=1338212617). Nguồn yêu cầu Topic 12 và các yêu cầu nộp bài. Đây là đề bài, không thay thế nguồn lý thuyết.

## Cách sử dụng nguồn trong báo cáo

Phần lý thuyết tham khảo [1] và đặt trong bối cảnh môn học theo [2]. Phần công cụ và phương pháp thực nghiệm dùng [3]–[6]. Ví dụ số, trường hợp kiểm thử, giả định, thiết kế phần mềm và kết quả thực nghiệm là nội dung của dự án. Không chép hình, đoạn văn dài hoặc số liệu từ sách để trình bày như kết quả thực hiện của nhóm.

Tài liệu Python ở đường dẫn `/3/` có thể trỏ đến bản Python mới hơn bản đang dùng trên máy. API sử dụng trong dự án thuộc thư viện chuẩn và dự án đặt mục tiêu Python 3.10 trở lên; phiên bản thực nghiệm phải xem trong `output/system-info.json`.
