Python 3.13.7 (tags/v3.13.7:bcee1c3, Aug 14 2025, 14:15:11) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
>>> import os
... 
... # ===================== MODELS =====================
... class Transaction:
...     """Đối tượng lưu thông tin một khoản Thu/Chi"""
...     def __init__(self, trans_id, date, amount, category, note=""):
...         self.id = trans_id          # Mã giao dịch
...         self.date = date            # Ngày (YYYY-MM-DD)
...         self.amount = int(amount)   # Số tiền (Kiểu số nguyên)
...         self.category = category    # Danh mục
...         self.note = note            # Ghi chú
... 
... class Node:
...     """Nút của danh sách liên kết đơn"""
...     def __init__(self, data):
...         self.data = data    # Dữ liệu (Transaction)
...         self.next = None    # Con trỏ đến nút tiếp theo
... 
... 
... # ===================== EXPENSE SERVICES =====================
... class LinkedList:
...     def __init__(self):
...         self.head = None
... 
...     def addNode(self, newData: Transaction):
...         """Thêm một nút mới vào cuối danh sách"""
...         new_node = Node(newData)
...         if self.head is None:
...             self.head = new_node
...             return
...         
...         temp = self.head
...         while temp.next is not None:
...             temp = temp.next
...         temp.next = new_node
... 
...     def deleteNode(self, trans_id: str) -> bool:
        """Xóa nút theo mã ID. Trả về True nếu thành công, False nếu không tìm thấy"""
        if self.head is None:
            return False

        temp = self.head
        prev = None

        # Trường hợp xóa nút đầu
        if temp is not None and temp.data.id == trans_id:
            self.head = temp.next
            return True

        # Tìm nút cần xóa ở giữa hoặc cuối
        while temp is not None and temp.data.id != trans_id:
            prev = temp
            temp = temp.next

        if temp is None:
            return False

        prev.next = temp.next
        return True

    def printList(self):
        """Duyệt và in toàn bộ danh sách giao dịch"""
        if self.head is None:
            print("Danh sach giao dich trong!")
            return
        
        print("\n--- DANH SACH GIAO DICH ---")
        current = self.head
        while current is not None:
            print(f"ID: {current.data.id} | Ngay: {current.data.date} | "
                  f"Sotien: {current.data.amount} | Danh muc: {current.data.category} | "
                  f"Ghi chu: {current.data.note}")
            current = current.next


# ===================== DATA MANAGER =====================
def loadDataFromFile(file_path: str) -> LinkedList:
    """Đọc dữ liệu từ file văn bản nạp vào Danh sách liên kết"""
    llist = LinkedList()
    if not os.path.exists(file_path):
        return llist # Trả về danh sách trống nếu file chưa tồn tại

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                
                # Tách chuỗi theo dấu '|' tương tự sstream/getline trong C++
                parts = line.split("|")
                if len(parts) >= 5:
                    t = Transaction(
                        trans_id=parts[0],
                        date=parts[1],
                        amount=int(parts[2]),
                        category=parts[3],
                        note=parts[4]
                    )
                    llist.addNode(t)
    except IOError:
        print("[Lỗi] Không thể đọc file dữ liệu.")
    
    return llist

def saveDataToFile(llist: LinkedList, file_path: str) -> bool:
    """Ghi toàn bộ dữ liệu từ Danh sách liên kết xuống file text"""
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            current = llist.head
            while current is not None:
                line = f"{current.data.id}|{current.data.date}|{current.data.amount}|{current.data.category}|{current.data.note}\n"
                file.write(line)
                current = current.next
        return True
    except IOError:
        return False


# ===================== PROGRAM CONTROLLER =====================
def displayMainMenu() -> int:
    """Hiển thị menu và nhận lựa chọn từ người dùng"""
    print("\n===== QUAN LY TAI CHINH CA NHAN =====")
    print("1. Xem danh sach giao dich")
    print("2. Them giao dich moi")
    print("3. Xoa giao dich theo Ma")
    print("4. Luu du lieu vao file")
    print("0. Thoat chuong trinh")
    
    try:
        choice = int(input("Nhap lua chon cua ban: ").strip())
        return choice
    except ValueError:
        return -1 # Trả về số không hợp lệ nếu người dùng nhập chữ


def main():
    file_path = "transactions.txt"
    
    # Kiểm tra sự tồn tại của file trước khi nạp
    if os.path.exists(file_path):
        listTransaction = loadDataFromFile(file_path)
        print("✓ Da tai du lieu tu file san co.")
    else:
        listTransaction = LinkedList()
        print("[Thong bao] File du lieu trong hoac chua ton tai. Khoi tao danh sach moi.")

    while True:
        choice = displayMainMenu()
        
        if choice == 1:
            listTransaction.printList()
            
        elif choice == 2:
            print("\n--- THEM GIAO DICH MOI ---")
            trans_id = input("Nhap ma giao dich (ID): ").strip()
            date = input("Nhap ngay (YYYY-MM-DD): ").strip()
            
            try:
                amount = int(input("Nhap so tien: ").strip())
            except ValueError:
                print("✗ So tien khong hop le! Vui long nhap so nguyen.")
                continue
                
            category = input("Nhap danh muc: ").strip()
            note = input("Nhap ghi chu: ").strip()
            
            newT = Transaction(trans_id, date, amount, category, note)
            listTransaction.addNode(newT)
            print("✓ Da them vao bo nho tam.")
            
        elif choice == 3:
            trans_id = input("Nhap ma ID can xoa: ").strip()
            if listTransaction.deleteNode(trans_id):
                print(f"✓ Xoa thanh cong giao dich {trans_id} khoi bo nho tam.")
            else:
                print("✗ Khong tim thay ma ID hop le.")
                
        elif choice == 4:
            if saveDataToFile(listTransaction, file_path):
                print(f"✓ Da ghi va luu du lieu vao file {file_path} thanh cong!")
            else:
                print("✗ Ghi file that bai!")
                
        elif choice == 0:
            print("Dang tu dong luu du lieu truoc khi thoat...")
            saveDataToFile(listTransaction, file_path)
            print("Cam on ban da su dung chuong trinh. Tam biet!")
            break
            
        else:
            print("Lua chon khong hop le. Vui long chon lai!")


if __name__ == "__main__":
