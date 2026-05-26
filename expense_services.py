"""
Module 3: expense_services.py
Xử lý Giao dịch & Nghiệp vụ cốt lõi: Thêm/Xóa/Sửa giao dịch, Quản lý ngân sách
Thành viên B - Hà Anh
"""

import uuid
from datetime import datetime
from models import Transaction, Budget
from budget_checker import checkBudgetExceeded


def _generateId(prefix="T"):
    """Sinh mã định danh ngắn duy nhất"""
    return prefix + str(uuid.uuid4())[:8].upper()


def inputTransaction():
    """
    Nhập liệu giao dịch từ bàn phím.
    Trả về: đối tượng Transaction hoặc None nếu người dùng huỷ.
    """
    print("\n--- NHẬP GIAO DỊCH MỚI ---")
    print("(Nhập 0 để huỷ)")

    # Loại giao dịch
    print("Loại giao dịch: 1 = Thu nhập | 2 = Chi tiêu")
    while True:
        choice = input("Chọn (1/2): ").strip()
        if choice == "0":
            return None
        if choice in ("1", "2"):
            trans_type = "thu" if choice == "1" else "chi"
            break
        print("  Vui lòng chọn 1 hoặc 2.")

    # Số tiền
    while True:
        raw = input("Số tiền (VND): ").strip()
        if raw == "0":
            return None
        try:
            amount = float(raw.replace(",", "").replace(".", ""))
            if amount <= 0:
                print("  Số tiền phải lớn hơn 0.")
                continue
            break
        except ValueError:
            print("  Số tiền không hợp lệ, vui lòng nhập lại.")

    # Danh mục
    CATEGORIES = ["An uong", "Di lai", "Hoc tap", "Giai tri", "Y te", "Tien nha", "Luong", "Phu cap", "Khac"]
    print("Danh mục:")
    for i, cat in enumerate(CATEGORIES, 1):
        print(f"  {i}. {cat}")
    while True:
        raw = input("Chọn số hoặc nhập tên danh mục: ").strip()
        if raw == "0":
            return None
        if raw.isdigit() and 1 <= int(raw) <= len(CATEGORIES):
            category = CATEGORIES[int(raw) - 1]
            break
        elif len(raw) >= 2:
            category = raw.capitalize()
            break
        print("  Vui lòng chọn hợp lệ.")

    # Ngày
    while True:
        raw = input(f"Ngày (YYYY-MM-DD) [Enter = hôm nay {datetime.today().strftime('%Y-%m-%d')}]: ").strip()
        if raw == "":
            date = datetime.today().strftime("%Y-%m-%d")
            break
        try:
            datetime.strptime(raw, "%Y-%m-%d")
            date = raw
            break
        except ValueError:
            print("  Ngày không hợp lệ. Định dạng: YYYY-MM-DD")

    note = input("Ghi chú (có thể để trống): ").strip()

    trans_id = _generateId("T")
    return Transaction(trans_id, amount, category, trans_type, date, note)


def modifyTransaction(transaction_list, trans_id):
    """
    Tìm giao dịch theo mã và cho phép thay đổi số tiền, danh mục, ghi chú.
    Trả về True nếu sửa thành công, False nếu không tìm thấy.
    """
    t = transaction_list.findById(trans_id)
    if t is None:
        print(f"  Không tìm thấy giao dịch mã: {trans_id}")
        return False

    print(f"\n--- SỬA GIAO DỊCH [{trans_id}] ---")
    print(f"  Loại  : {t.type.upper()}")
    print(f"  Số tiền: {t.amount:,.0f} VND")
    print(f"  Danh mục: {t.category}")
    print(f"  Ngày  : {t.date}")
    print(f"  Ghi chú: {t.note}")
    print("(Enter để giữ nguyên giá trị cũ)")

    raw = input(f"Số tiền mới [{t.amount:,.0f}]: ").strip()
    if raw:
        try:
            new_amount = float(raw.replace(",", ""))
            if new_amount > 0:
                t.amount = new_amount
        except ValueError:
            print("  Giá trị không hợp lệ, giữ số tiền cũ.")

    raw = input(f"Danh mục mới [{t.category}]: ").strip()
    if raw:
        t.category = raw.capitalize()

    raw = input(f"Ghi chú mới [{t.note}]: ").strip()
    if raw:
        t.note = raw

    print("  Giao dịch đã được cập nhật.")
    return True


def updateBudget(budget_list, category, limit, month, year):
    """
    Thiết lập hoặc sửa đổi hạn mức chi tiêu cho một danh mục/tháng/năm.
    Nếu đã tồn tại → cập nhật. Nếu chưa → thêm mới.
    Trả về budget_list đã cập nhật.
    """
    current = budget_list.head
    while current is not None:
        b = current.data
        if b.category == category and b.month == month and b.year == year:
            b.limit = limit
            print(f"  Đã cập nhật ngân sách: {category} tháng {month}/{year} = {limit:,.0f} VND")
            return budget_list
        current = current.next

    # Chưa tồn tại → thêm mới
    budget_id = _generateId("B")
    new_budget = Budget(budget_id, category, limit, month, year)
    budget_list.addNode(new_budget)
    print(f"  Đã thêm ngân sách mới: {category} tháng {month}/{year} = {limit:,.0f} VND")
    return budget_list


def addTransactionWithCheck(transaction_list, budget_list, t):
    """
    Thêm giao dịch vào DSLK, có kiểm tra vượt ngân sách trước.
    Luôn thêm vào dù có vượt hay không (chỉ cảnh báo).
    """
    if t.type == "chi":
        exceeded, spent, budget_limit = checkBudgetExceeded(transaction_list, budget_list, t)
        if exceeded:
            print(f"\n  ⚠️  CẢNH BÁO VƯỢT HẠN MỨC!")
            print(f"     Danh mục : {t.category}")
            print(f"     Đã tiêu  : {spent:,.0f} VND")
            print(f"     Hạn mức  : {budget_limit:,.0f} VND")
            print(f"     Khoản mới: {t.amount:,.0f} VND")
            print(f"     Tổng sẽ là: {spent + t.amount:,.0f} VND (vượt {spent + t.amount - budget_limit:,.0f} VND)\n")

    transaction_list.addNode(t)
    print(f"  ✓ Đã thêm giao dịch [{t.id}]: {t.type.upper()} {t.amount:,.0f} VND - {t.category}")
    return transaction_list
