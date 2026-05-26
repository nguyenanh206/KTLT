"""
Module 4: budget_checker.py
Thuật toán kiểm tra điều kiện vượt ngân sách và cảnh báo.
Thành viên B - Hà Anh
"""

from datetime import datetime


def checkBudgetExceeded(transaction_list, budget_list, new_transaction):
    """
    Kiểm tra xem khoản chi mới có làm vượt hạn mức không.

    Thuật toán:
    1. Lấy tháng/năm từ ngày của giao dịch mới.
    2. Duyệt DSLK Giao dịch: tính tổng chi đã có của danh mục đó trong tháng đó.
    3. Duyệt DSLK Ngân sách: lấy hạn mức của danh mục trong tháng đó.
    4. So sánh: (tổng đã chi + khoản mới) > hạn mức.

    Trả về: (exceeded: bool, spent_so_far: float, budget_limit: float)
    """
    try:
        dt = datetime.strptime(new_transaction.date, "%Y-%m-%d")
        month = dt.month
        year = dt.year
    except ValueError:
        return False, 0.0, 0.0

    category = new_transaction.category

    # Bước 2: Tính tổng đã chi cho danh mục này trong tháng
    spent_so_far = 0.0
    current = transaction_list.head
    while current is not None:
        t = current.data
        if t.type == "chi" and t.category == category:
            try:
                t_date = datetime.strptime(t.date, "%Y-%m-%d")
                if t_date.month == month and t_date.year == year:
                    spent_so_far += t.amount
            except ValueError:
                pass
        current = current.next

    # Bước 3: Lấy hạn mức ngân sách
    budget_limit = None
    current = budget_list.head
    while current is not None:
        b = current.data
        if b.category == category and b.month == month and b.year == year:
            budget_limit = b.limit
            break
        current = current.next

    # Nếu chưa đặt ngân sách thì không cảnh báo
    if budget_limit is None:
        return False, spent_so_far, 0.0

    exceeded = (spent_so_far + new_transaction.amount) > budget_limit
    return exceeded, spent_so_far, budget_limit
