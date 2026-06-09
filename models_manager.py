import os

# ===================== MODELS =====================

class Transaction:
    """Đối tượng lưu thông tin một khoản Thu/Chi"""
    # [SỬA] Thêm trường `trans_type` (thu/chi) vào __init__
    # Thiếu trường này khiến checkBudgetExceeded() và calculateBalance()
    # báo AttributeError khi truy cập t.type
    # [SỬA] Đổi thứ tự tham số thành (id, date, trans_type, amount, category, note)
    # để thống nhất với cách dùng ở các module khác
    def __init__(self, trans_id, date, trans_type, amount, category, note=""):
        self.id = trans_id          # Mã giao dịch
        self.date = date            # Ngày (YYYY-MM-DD)
        self.type = trans_type      # Loại: "thu" hoặc "chi"  <- THÊM MỚI
        self.amount = int(amount)   # Số tiền (kiểu số nguyên)
        self.category = category    # Danh mục
        self.note = note            # Ghi chú

#Thêm đối tượng Budget để quản lý ngân sách theo danh mục/tháng/năm, phục vụ tính năng checkBudgetExceeded() và báo cáo ngân sách
class Budget:
    """Ngan sach chi tieu theo danh muc/thang/nam."""

    def __init__(self, budget_id, category, limit, month, year):
        self.id = str(budget_id).strip()
        self.category = str(category).strip()
        self.limit = float(limit)
        self.month = int(month)
        self.year = int(year)

class Node:
    """Nút của danh sách liên kết đơn"""
    def __init__(self, data):
        self.data = data    # Dữ liệu (Transaction)
        self.next = None    # Con trỏ đến nút tiếp theo


# ===================== EXPENSE SERVICES =====================

class LinkedList:
    """Danh sách liên kết đơn quản lý các giao dịch"""
    def __init__(self):
        self.head = None

    def addNode(self, newData):
        """Thêm một nút mới vào cuối danh sách"""
        new_node = Node(newData)
        if self.head is None:
            self.head = new_node
            return
        temp = self.head
        while temp.next is not None:
            temp = temp.next
        temp.next = new_node

    def deleteNode(self, trans_id):
        """Xóa nút theo mã ID. Trả về True nếu thành công, False nếu không tìm thấy"""
        if self.head is None:
            return False

        # Trường hợp xóa nút đầu
        if self.head.data.id == trans_id:
            self.head = self.head.next
            return True

        # Tìm nút cần xóa ở giữa hoặc cuối
        temp = self.head
        while temp.next is not None:
            if temp.next.data.id == trans_id:
                temp.next = temp.next.next
                return True
            temp = temp.next

        return False
    #Thêm phương thức tìm kiếm giao dịch theo ID, phục vụ tính năng sửa giao dịch và checkBudgetExceeded()
    def findById(self, item_id):
        current = self.head
        while current is not None:
            if current.data.id == item_id:
                return current.data
            current = current.next
        return None
    #thêm phương thức đếm số lượng giao dịch, phục vụ tính năng thống kê số lượng giao dịch
    def count(self):
        total = 0
        current = self.head
        while current is not None:
            total += 1
            current = current.next
        return total
    #Thêm phương thức kiểm tra danh sách có rỗng hay không, phục vụ tính năng hiển thị thông báo khi danh sách trống
    def isEmpty(self):
        return self.head is None
    
    def printList(self):
        """Duyệt và in toàn bộ danh sách giao dịch"""
        if self.head is None:
            print("Danh sách giao dịch trống!")
            return
        print("\n--- DANH SÁCH GIAO DỊCH ---")
        current = self.head
        while current is not None:
            t = current.data
            print(f"ID: {t.id} | Ngày: {t.date} | Loại: {t.type} | "
                  f"Số tiền: {t.amount:,} | Danh mục: {t.category} | Ghi chú: {t.note}")
            current = current.next


# ===================== DATA MANAGER =====================

def loadDataFromFile(file_path):
    """Đọc dữ liệu từ file văn bản, nạp vào Danh sách liên kết"""
    llist = LinkedList()
    if not os.path.exists(file_path):
        return llist  # Trả về danh sách trống nếu file chưa tồn tại

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                # Tách chuỗi theo dấu '|'
                parts = line.split("|")
                # [SỬA] Cập nhật đọc 6 trường (thêm trans_type)
                if len(parts) >= 6:
                    t = Transaction(
                        trans_id=parts[0],
                        date=parts[1],
                        trans_type=parts[2],
                        amount=int(parts[3]),
                        category=parts[4],
                        note=parts[5]
                    )
                    llist.addNode(t)
    except IOError:
        print("[Lỗi] Không thể đọc file dữ liệu.")

    return llist


def saveDataToFile(llist, file_path):
    """Ghi toàn bộ dữ liệu từ Danh sách liên kết xuống file text"""
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            current = llist.head
            while current is not None:
                d = current.data
                # [SỬA] Ghi thêm trường type vào file
                line = f"{d.id}|{d.date}|{d.type}|{d.amount}|{d.category}|{d.note}\n"
                file.write(line)
                current = current.next
        return True
    except IOError:
        return False
