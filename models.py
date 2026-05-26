"""
Module 1: models.py
Định nghĩa cấu trúc dữ liệu tự cài đặt: Node, LinkedList cho Giao dịch và Ngân sách
Thành viên A - Quang Anh
"""

# ===================== CẤU TRÚC DỮ LIỆU: GIAO DỊCH =====================

class Transaction:
    """Đối tượng lưu thông tin một khoản Thu/Chi"""
    def __init__(self, trans_id, amount, category, trans_type, date, note=""):
        self.id = trans_id          # Mã giao dịch (chuỗi duy nhất)
        self.amount = amount        # Số tiền (float, luôn dương)
        self.category = category    # Danh mục (ăn uống, đi lại, lương, ...)
        self.type = trans_type      # "thu" hoặc "chi"
        self.date = date            # Ngày (chuỗi "YYYY-MM-DD")
        self.note = note            # Ghi chú tùy chọn

    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "category": self.category,
            "type": self.type,
            "date": self.date,
            "note": self.note
        }

    @staticmethod
    def from_dict(d):
        return Transaction(d["id"], d["amount"], d["category"], d["type"], d["date"], d.get("note", ""))


# ===================== CẤU TRÚC DỮ LIỆU: NGÂN SÁCH =====================

class Budget:
    """Đối tượng lưu hạn mức ngân sách cho một danh mục trong một tháng"""
    def __init__(self, budget_id, category, limit, month, year):
        self.id = budget_id     # Mã ngân sách
        self.category = category  # Tên danh mục
        self.limit = limit        # Hạn mức chi tiêu (float)
        self.month = month        # Tháng (int 1-12)
        self.year = year          # Năm (int)

    def to_dict(self):
        return {
            "id": self.id,
            "category": self.category,
            "limit": self.limit,
            "month": self.month,
            "year": self.year
        }

    @staticmethod
    def from_dict(d):
        return Budget(d["id"], d["category"], d["limit"], d["month"], d["year"])


# ===================== NODE (NÚT DANH SÁCH LIÊN KẾT) =====================

class Node:
    """Nút của danh sách liên kết đơn"""
    def __init__(self, data):
        self.data = data    # Dữ liệu (Transaction hoặc Budget)
        self.next = None    # Con trỏ đến nút tiếp theo


# ===================== DANH SÁCH LIÊN KẾT TỰ CÀI ĐẶT =====================

class LinkedList:
    """
    Danh sách liên kết đơn tự cài đặt.
    Không sử dụng list/dict có sẵn của Python để lưu trữ nội bộ.
    """
    def __init__(self):
        self.head = None    # Nút đầu tiên
        self._size = 0      # Số lượng phần tử

    def addNode(self, data):
        """Thêm một nút mới vào cuối danh sách"""
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
        else:
            current = self.head
            while current.next is not None:
                current = current.next
            current.next = new_node
        self._size += 1

    def deleteNode(self, item_id):
        """
        Xóa nút theo ID (trường .id của data).
        Trả về True nếu xóa thành công, False nếu không tìm thấy.
        """
        if self.head is None:
            return False

        # Trường hợp xóa nút đầu
        if self.head.data.id == item_id:
            self.head = self.head.next
            self._size -= 1
            return True

        # Tìm và xóa nút giữa/cuối
        current = self.head
        while current.next is not None:
            if current.next.data.id == item_id:
                current.next = current.next.next
                self._size -= 1
                return True
            current = current.next
        return False

    def findById(self, item_id):
        """Tìm và trả về đối tượng data theo ID, hoặc None nếu không có"""
        current = self.head
        while current is not None:
            if current.data.id == item_id:
                return current.data
            current = current.next
        return None

    def toArray(self):
        """Chuyển DSLK thành mảng (list Python) để tiện duyệt - chỉ dùng khi cần xuất"""
        result = []
        current = self.head
        while current is not None:
            result.append(current.data)
            current = current.next
        return result

    def size(self):
        return self._size

    def isEmpty(self):
        return self.head is None

    def clear(self):
        """Xóa toàn bộ danh sách"""
        self.head = None
        self._size = 0
