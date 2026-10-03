# Câu hỏi chuẩn bị bảo vệ

Các câu trả lời sau là gợi ý học tập. Thành viên nên giải thích bằng lời của mình và tự tính một ví dụ khác trước khi trình bày.

1. **Địa chỉ logic trong dự án gồm những gì?** Hai thành phần là ID segment và offset. Yêu cầu có thêm loại truy cập `r`, `w` hoặc `x` để kiểm tra bảo vệ. Loại truy cập không phải phần cộng vào địa chỉ.
2. **`base` và `limit` khác nhau như thế nào?** `base` là địa chỉ bắt đầu. `limit` là số vị trí hợp lệ. Địa chỉ cuối là `base + limit − 1`.
3. **Tại sao offset bằng limit bị lỗi?** Offset bắt đầu từ 0. Với limit 4, chỉ có 0, 1, 2, 3; offset 4 là vị trí thứ năm.
4. **Công thức dịch là gì?** Khi segment tồn tại, offset hợp lệ và quyền được phép: `physical = base + offset`.
5. **Tại sao không chỉ cộng hai số rồi trả kết quả?** Một tổng có thể nằm trong segment khác hoặc ngoài vùng cho phép. Quyền cũng có thể không phù hợp. Cộng được về mặt số học không đồng nghĩa được phép truy cập.
6. **Có bao nhiêu nhóm kết quả?** `OK`, `SEGMENT_NOT_FOUND`, `SEGMENTATION_FAULT`, `PROTECTION_FAULT`. Lỗi nhập dữ liệu sai kiểu được xử lý ở bước kiểm tra đầu vào, không dùng để giả làm một địa chỉ đã dịch.
7. **Nếu vừa sai quyền vừa vượt giới hạn?** Dự án kiểm tra tồn tại, giới hạn rồi quyền. Vì vậy vượt giới hạn được báo trước. Thứ tự này là hợp đồng của phần mềm và phải được kiểm thử.
8. **`SEGMENTATION_FAULT` có làm ứng dụng bị crash không?** Không. Đây là trạng thái mô phỏng trong kết quả; ứng dụng tiếp tục xử lý và cho xem trace.
9. **Offset âm có được đọc từ CSV không?** Có thể đọc như một số nguyên để kiểm thử, nhưng phép dịch phải từ chối. Nó khác với chuỗi `abc`, vốn sai kiểu đầu vào.
10. **Tại sao không cho hai segment chồng nhau?** Đây là giả định đơn giản hóa cho một tiến trình và vùng riêng biệt. Segmentation nói chung có thể hỗ trợ chia sẻ; dự án chưa mô hình hóa quan hệ đó.
11. **Hai vùng sát nhau có bị coi là chồng lấn?** Không. `[1000, 1400)` và `[1400, 1500)` không có phần chung. Cách dùng khoảng nửa mở giúp kiểm tra điều này rõ ràng.
12. **Vì sao dùng dictionary?** Để tra ID không cần duyệt lần lượt. Số ID có thể thưa, nên không phải cấp phát một danh sách dài tới ID lớn nhất.
13. **Dictionary có luôn `O(1)` không?** Không nên nói tuyệt đối. Tra cứu có thời gian trung bình/kỳ vọng `O(1)`; có tình huống xấu hơn do cơ chế băm. Benchmark chỉ phản ánh dữ liệu và môi trường đã đo.
14. **Kiểm tra chồng lấn tốn bao nhiêu?** Sắp xếp S segment theo base tốn `O(S log S)`, rồi duyệt các cặp kề nhau tốn `O(S)`.
15. **Dịch A địa chỉ tốn bao nhiêu bộ nhớ?** Bảng tốn `O(S)`; nếu lưu toàn bộ kết quả và trace có độ dài hữu hạn mỗi địa chỉ, thêm `O(A)`. Chế độ xử lý streaming có thể giảm phần này nhưng phải thay đổi cách hiển thị/lưu.
16. **Làm sao biết thuật toán đúng?** Tính tay các ca độc lập trước, kiểm tra bất biến `base <= physical < base + limit`, thử sát biên, thử mỗi nhánh lỗi và đối chiếu expected/actual. Không tạo expected bằng chính hàm cần kiểm tra.
17. **Tại sao cần cả unit test và kiểm tra CSV?** Unit test giúp cô lập logic; kiểm tra CSV chứng minh đọc file, dịch và xuất/so sánh phối hợp đúng. GUI cần kiểm tra thao tác riêng.
18. **Tại sao tách GUI khỏi thuật toán?** Để cùng một logic được dùng trong cửa sổ, test và script. Thay bố cục giao diện không làm thay đổi công thức dịch.
19. **Tại sao benchmark không tính thời gian vẽ GUI?** Mục tiêu phép đo phần lõi là đánh giá thao tác dịch/tra cứu. GUI là phép đo khác, có chi phí cập nhật widget và vẽ màn hình.
20. **So sánh dictionary với tuyến tính có công bằng không?** Chỉ công bằng khi cùng dữ liệu, cùng kết quả cần tạo và cùng vùng thời gian được đo. Tra lookup-only với lookup-only; không so một bên có trace với một bên không có.
21. **Vì sao chạy lại cho thời gian khác?** Tải hệ thống, bộ nhớ đệm, bộ thu gom rác, bản Python và cách đo đều ảnh hưởng. Cần lặp, ghi cấu hình và dùng thống kê; không khẳng định một con số là tốc độ của mọi máy.
22. **Segmentation và paging khác nhau thế nào?** Trong phạm vi bài học, segment là vùng logic có độ dài thay đổi; paging chia không gian thành đơn vị kích thước cố định. Dự án này chỉ mô phỏng dịch theo segment và không có bảng trang.
23. **Sơ đồ khoảng trống có chứng minh phân mảnh ngoài không?** Nó giúp thấy các khoảng giữa vùng đã đặt. Chương trình không có thuật toán cấp phát động hoặc khối lượng yêu cầu cấp phát để kết luận mức phân mảnh của một hệ thống thật.
24. **Có thể truy cập nhiều byte một lần không?** Bản này xét một địa chỉ. Nếu thêm độ dài `n`, phải kiểm tra cả khoảng, chẳng hạn `offset >= 0`, `n > 0`, `offset + n <= limit`, đồng thời xét quyền.
25. **Python có mô phỏng tràn số địa chỉ 32-bit không?** Không trong giả định hiện tại. Python dùng số nguyên độ dài tùy ý; muốn mô phỏng 32-bit phải thêm cận rõ ràng và test tràn/cận trên.
26. **Nhóm thực sự đã làm phần nào?** Trả lời theo bảng đóng góp có bằng chứng; nêu phần AI hỗ trợ và những kiểm tra/sửa đổi nhóm đã thực hiện. Không đọc kế hoạch tám tuần như lịch sử đã làm.

## Bài tính nhanh tự luyện

Cho segment 7 có `base = 4096`, `limit = 256`, `permissions = r`:

| Yêu cầu | Kết quả để tự đối chiếu |
|---|---|
| `(7, 0, r)` | `OK`, 4096 |
| `(7, 255, r)` | `OK`, 4351 |
| `(7, 256, r)` | `SEGMENTATION_FAULT` |
| `(7, 10, w)` | `PROTECTION_FAULT` |
| `(8, 10, r)` | `SEGMENT_NOT_FOUND` |
| `(7, -1, r)` | `SEGMENTATION_FAULT` |

Hãy viết trace cho từng dòng mà không mở chương trình, rồi dùng ứng dụng để kiểm tra lại.
