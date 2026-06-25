Chủ đề 6 : Quản lý chi tiêu cá nhân
Ứng dụng quản lý chi tiêu cá nhân:
Mô tả: Cho phép người dùng ghi lại các khoản thu/chi theo ngày, phân loại (ăn uống, đi lại, học tập,...). Tính toán tổng thu/chi theo ngày/tháng/năm/loại. Đặt ngân sách cho từng loại, báo cáocác khoản vượt quá.
-	Tính năng cốt lõi:
o	Ghi chép giao dịch: Số tiền, phân loại (ăn uống, học phí, lương...), ghi chú.
o	Thiết lập ngân sách (Budget): Đặt hạn mức chi cho từng danh mục theo tháng.
-	Logic nghiệp vụ:
o	Kiểm tra và cảnh báo khi chi vượt mức ngân sách đã đặt.
o	Tính toán số dư hiện tại dựa trên tổng thu và tổng chi.
-	Báo cáo: 
o	dạng văn bản hoặc đồ họa đơn giản: tỷ lệ chi tiêu giữa các nhóm
o	tổng hợp trong kỳ (tháng): các mục vượt budget, …

YÊU CẦU/HƯỚNG DẪN
Yêu cầu ngôn ngữ lập trình: Có thể sử dụng các ngôn ngữ sau đây: C/C++/C#/Java/Python
Không sử dụng các cấu trúc dữ liệu nâng cao/thư viện được cung cấp sẵn có (như list, hash, queue, thư viện ma trận, thư viện số lớn của nền tảng lập trình) mà phải tự cài đặt các cấu trúc dữ liệu, thuật toán được sử dụng
Yêu cầu chung của chương trình:
-	Người sử dụng có thể lựa chọn tác vụ từ menu (đơn giản) để thực hiện các tác vụ cho đến khi chọn kết thúc chương trình
-	Các dữ liệu vào ra được lưu trữ trong file text (có thể có cấu trúc như json, xml, cách dòng, …). Người sử dụng có thể nhập liệu từ bàn phím, các dữ liệu được lưu xuống file text)
-	Vận dụng các kỹ thuật thiết kế, lập trình, kiểm thử
Yêu cầu kết quả: 
-	Kết quả điện tử: phân thành 2 file, tải lên assignment trên MS Teams
(1)	File báo cáo (word), thể thức (font chữ, trình bày) tham khảo mẫu đồ án của Đại học. Một số thông tin cần có:
a.	thông tin người thực hiện, phân công (nếu là nhóm)
b.	mô tả tổng thể chức năng, cách thiết kế/tổ chức chương trình, file dữ liệu
c.	tình huống kiểm thử, kết quả thực hiện (hình ảnh chụp kết quả) 
d.	tổng kết các kỹ thuật đã vận dụng
e.	phụ lục code hàm main, các mô tả hàm xử lý tác nghiệp chính
(2)	File nén (.zip, .rar) chương trình, trong đó chứa
a.	Thư mục, các file mã nguồn
b.	Các file dữ liệu

 
Dự án môn KTLT_QuanLyChiTieu/
│
├── __pycache__/                      # Thư mục chứa các file .pyc do Python sinh ra khi chạy
│
├── data/                             # Thư mục chứa dữ liệu lưu trữ (Định dạng JSON hoặc Text) 
│   ├── transactions.json             # Lưu cơ sở dữ liệu về lịch sử giao dịch Thu/Chi 
│   └── budgets.json                  # Lưu cơ sở dữ liệu về hạn mức ngân sách các danh mục [
│
├── [test/](file:///c:/Users/acer/OneDrive/Documents/5.KTLT/KTLT/test)                             # Thư mục chứa hình ảnh chụp kết quả kiểm thử thực tế
│
├── models.py                   # Module 1: Định nghĩa cấu trúc dữ liệu tự cài đặt (Thành viên A)
│                                     # (Cài đặt thủ công Node, Linked List cho Giao dịch & Ngân sách) 
│
├── data_manager.py                   # Module 2: Quản lý Tệp tin (Thành viên A)
│                         # (Các hàm đọc/ghi dữ liệu từ bộ nhớ RAM xuống file trong thư mục data/) 
│
├── expense_services.py     # Module 3: Xử lý Giao dịch & Nghiệp vụ cốt lõi (Thành viên B)
│                              # (Các hàm thêm/xóa/sửa giao dịch, quản lý và đặt hạn mức ngân sách) 
│
├── budget_checker.py              # Module 4: Hệ thống Cảnh báo thông minh (Thành viên B)
│                                # (Thuật toán kiểm tra điều kiện và đưa ra cảnh báo khi chi vượt mức)
│
├── analytics_service.py            # Module 5: Thống kê & Phân tích tài chính (Thành viên C)
│                                     # (Thuật toán tính số dư, tính tỷ lệ % chi tiêu giữa các danh mục) 
│
├── display_report_service.py         # Module 6: Xuất bản báo cáo (Thành viên C)
│                           # (Định dạng và in bảng tổng hợp định kỳ, liệt kê các mục vượt hạn mức) 
│
├── program_controller.py             # Module 7: Điều hướng chương trình (Thành viên A)
│                                     # (Xây dựng giao diện Menu và bắt các sự kiện lựa chọn tác vụ) 
│
└── main.py                           # Chương trình chính (Điểm khởi chạy hệ thống) 

CHI TIẾT CÁC LUỒNG NGHIỆP VỤ (USE-CASE WORKFLOWS)
Luồng 1: Khởi động hệ thống (System Initialization)
  •	Bước 1: main.py kích hoạt và gọi hàm điều hướng trong program_controller.py.
  •	Bước 2: Hệ thống tự động gọi hàm loadDataFromFile() nằm tại data_manager.py. Hàm này mở các file transactions.json và budgets.json ở thư mục data/.
  •	Bước 3: Hàm đọc file tiến hành phân tách dữ liệu, lặp và gọi hàm addNode() thuộc models.py để dựng thành 2 Danh sách liên kết (DSLK) trên RAM: một danh sách chứa toàn bộ lịch sử giao dịch và một danh sách chứa các hạn mức ngân sách.
  •	Bước 4: Sau khi nạp dữ liệu thành công, hàm displayMainMenu() được gọi để hiển thị các tùy chọn tác vụ ra màn hình cho người dùng.
Luồng 2: Thêm mới một khoản Chi tiêu (Expense Transaction Workflow)
Đây là luồng nghiệp vụ phức tạp nhất, đòi hỏi sự phối hợp chặt chẽ giữa cả 3 thành viên:
  •	Bước 1 (Giao diện): Người dùng chọn chức năng thêm giao dịch. Hàm inputTransaction() (expense_services.py) kích hoạt để người dùng nhập: Số tiền, danh mục (ví dụ: "Ăn uống"), ngày tháng và ghi chú từ bàn phím.
  •	Bước 2 (Kiểm tra logic): Trước khi thêm vào danh sách, hệ thống gọi hàm checkBudgetExceeded() (budget_checker.py).
    o	Hàm này sẽ duyệt qua DSLK Giao dịch để tính tổng số tiền đã tiêu của mục "Ăn uống" trong tháng hiện tại.
    o	Sau đó, nó duyệt qua DSLK Ngân sách để lấy ra số tiền hạn mức đã đặt cho mục "Ăn uống".
    o	Nếu Tổng đã tiêu + Khoản chi mới > Hạn mức ngân sách, hàm trả về True $\rightarrow$ Hệ thống lập tức in một dòng Cảnh báo vượt hạn mức bằng chữ màu nổi bật lên console để nhắc nhở người dùng.
  •	Bước 3 (Cập nhật RAM): Hệ thống gọi hàm addNode() (models.py) để tạo một nút mới và nối vào đuôi của DSLK Giao dịch.
  •	Bước 4 (Đồng bộ ổ cứng): Ngay lập tức, hàm saveDataToFile() (data_manager.py) được kích hoạt để chuyển dịch toàn bộ DSLK hiện tại lưu đè lại vào file transactions.json, đảm bảo nếu mất điện hay tắt app đột ngột dữ liệu vẫn được bảo toàn.
Luồng 3: Điều chỉnh hoặc Thiết lập Ngân sách (Budget Management Workflow)
  •	Bước 1: Người dùng chọn cài đặt hạn mức cho một danh mục chi tiêu trong tháng.
  •	Bước 2: Hàm updateBudget() (expense_services.py) nhận thông tin về Tên danh mục, Số tiền hạn mức mới và thời gian áp dụng.
  •	Bước 3: Hàm tiến hành duyệt qua DSLK Ngân sách:
    o	Nếu danh mục đó đã tồn tại hạn mức trong tháng đó, hệ thống sẽ sửa đổi giá trị số tiền trực tiếp trên nút đó.
    o	Nếu danh mục đó chưa có hạn mức, hệ thống gọi addNode() để chèn thêm một nút ngân sách mới vào DSLK Ngân sách.
  •	Bước 4: Gọi saveDataToFile() để cập nhật dữ liệu mới xuống file budgets.json.
Luồng 4: Xuất báo cáo tài chính định kỳ (Analytics & Reporting Workflow)
Luồng này thuần túy là việc đọc và xử lý dữ liệu từ RAM để hiển thị, không làm thay đổi hay ghi thêm dữ liệu:
  •	Bước 1: Người dùng chọn xem báo cáo của một Tháng/Năm cụ thể.
  •	Bước 2 (Tính toán): Hàm generateMonthlyReport() (display_report_service.py) được gọi và kích hoạt các hàm tính toán song song:
    o	Gọi calculateBalance() (analytics_service.py) duyệt DSLK Giao dịch để tính toán: Tổng Thu - Tổng Chi.
    o	Gọi calculateCategoryRatios() (analytics_service.py) để tính toán tỷ lệ % chi tiêu của từng danh mục.
  •	Bước 3 (Lọc dữ liệu vi phạm): Hàm quét qua DSLK Ngân sách và đối chiếu với tổng chi thực tế của tháng đó để lọc ra danh sách riêng các mục đã bị tiêu dùng vượt ngưỡng kèm theo số tiền vượt cụ thể.
  •	Bước 4 (Hiển thị): Định dạng toàn bộ các thông số trên thành một bảng biểu văn bản trực quan (giao diện dòng lệnh ngăn nắp) hiển thị ra màn hình.
  
