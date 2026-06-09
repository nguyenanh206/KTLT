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

# Default file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DEFAULT_TRANS_FILE = os.path.join(DATA_DIR, "transactions.txt")
DEFAULT_BUDGET_FILE = os.path.join(DATA_DIR, "budgets.txt")

def _ensureDataDir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def loadDataFromFile(file_path=None):
    """
    Đọc dữ liệu từ file văn bản.
    - Nếu file_path là None: đọc cả 2 file giao dịch và ngân sách mặc định, trả về (transaction_list, budget_list).
    - Nếu file_path không None: đọc file đó. Nếu file_path chứa "budget" thì nạp Budget, ngược lại nạp Transaction. Trả về LinkedList.
    """
    _ensureDataDir()
    
    if file_path is None:
        transaction_list = loadDataFromFile(DEFAULT_TRANS_FILE)
        budget_list = loadDataFromFile(DEFAULT_BUDGET_FILE)
        return transaction_list, budget_list

    llist = LinkedList()
    if not os.path.exists(file_path):
        return llist

    is_budget_file = "budget" in os.path.basename(file_path).lower()

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                parts = [p.strip() for p in line.split("|")]
                if is_budget_file:
                    if len(parts) >= 5:
                        b = Budget(
                            budget_id=parts[0],
                            category=parts[1],
                            limit=float(parts[2]),
                            month=int(parts[3]),
                            year=int(parts[4])
                        )
                        llist.addNode(b)
                else:
                    if len(parts) >= 6:
                        # Convert amount safely, handling possible float representation like 100000.0
                        amt = int(float(parts[3]))
                        t = Transaction(
                            trans_id=parts[0],
                            date=parts[1],
                            trans_type=parts[2],
                            amount=amt,
                            category=parts[4],
                            note=parts[5]
                        )
                        llist.addNode(t)
    except Exception as e:
        print(f"[Lỗi] Không thể đọc file dữ liệu {file_path}: {e}")

    return llist


def saveDataToFile(arg1, arg2=None):
    """
    Ghi toàn bộ dữ liệu xuống file text.
    Hỗ trợ 2 signature:
    1. saveDataToFile(transaction_list, budget_list) -> Ghi xuống các file mặc định
    2. saveDataToFile(llist, file_path) -> Ghi llist xuống file_path
    """
    _ensureDataDir()
    
    # Signature 1: saveDataToFile(transaction_list, budget_list)
    if arg2 is None or isinstance(arg2, LinkedList):
        transaction_list = arg1
        budget_list = arg2 if arg2 is not None else LinkedList()
        ok1 = saveDataToFile(transaction_list, DEFAULT_TRANS_FILE)
        ok2 = saveDataToFile(budget_list, DEFAULT_BUDGET_FILE)
        return ok1 and ok2

    # Signature 2: saveDataToFile(llist, file_path)
    llist = arg1
    file_path = arg2
    
    is_budget_file = "budget" in os.path.basename(file_path).lower()
    
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            current = llist.head
            while current is not None:
                d = current.data
                if is_budget_file:
                    # Budget format: id|category|limit|month|year
                    line = f"{d.id}|{d.category}|{d.limit}|{d.month}|{d.year}\n"
                else:
                    # Transaction format: id|date|type|amount|category|note
                    line = f"{d.id}|{d.date}|{d.type}|{d.amount}|{d.category}|{d.note}\n"
                file.write(line)
                current = current.next
        return True
    except Exception as e:
        print(f"[Lỗi] Không thể ghi file dữ liệu {file_path}: {e}")
        return False
