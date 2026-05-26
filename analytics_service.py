"""
Module 5: analytics_service.py
Thống kê & Phân tích tài chính: số dư, tỷ lệ chi tiêu, tìm kiếm giao dịch.
Thành viên C - Vinh
"""

from datetime import datetime


def calculateBalance(transaction_list):
    """
    Duyệt toàn bộ DSLK Giao dịch để tính số dư tích lũy:
        Số dư = Tổng Thu - Tổng Chi

    Trả về: (balance: float, total_income: float, total_expense: float)
    """
    total_income = 0.0
    total_expense = 0.0

    current = transaction_list.head
    while current is not None:
        t = current.data
        if t.type == "thu":
            total_income += t.amount
        elif t.type == "chi":
            total_expense += t.amount
        current = current.next

    balance = total_income - total_expense
    return balance, total_income, total_expense


def calculateCategoryRatios(transaction_list, month=None, year=None):
    """
    Tính tỷ lệ % chi tiêu của từng danh mục trong kỳ (tháng/năm).
    Nếu month=None thì tính toàn bộ.

    Trả về: danh sách [(category, amount, percent), ...] sắp xếp giảm dần theo amount.
    """
    # Dùng mảng song song (key-value thủ công, không dùng dict built-in)
    cat_names = []
    cat_amounts = []

    current = transaction_list.head
    while current is not None:
        t = current.data
        if t.type == "chi":
            include = True
            if month is not None and year is not None:
                try:
                    dt = datetime.strptime(t.date, "%Y-%m-%d")
                    if dt.month != month or dt.year != year:
                        include = False
                except ValueError:
                    include = False

            if include:
                # Tìm danh mục có sẵn
                found = False
                for i in range(len(cat_names)):
                    if cat_names[i] == t.category:
                        cat_amounts[i] += t.amount
                        found = True
                        break
                if not found:
                    cat_names.append(t.category)
                    cat_amounts.append(t.amount)

        current = current.next

    # Tính tổng
    total = 0.0
    for amt in cat_amounts:
        total += amt

    # Tạo kết quả và tính %
    result = []
    for i in range(len(cat_names)):
        pct = (cat_amounts[i] / total * 100) if total > 0 else 0.0
        result.append((cat_names[i], cat_amounts[i], pct))

    # Sắp xếp giảm dần (Bubble Sort thủ công)
    n = len(result)
    for i in range(n - 1):
        for j in range(n - 1 - i):
            if result[j][1] < result[j + 1][1]:
                result[j], result[j + 1] = result[j + 1], result[j]

    return result, total


def searchTransactions(transaction_list, keyword=None, category=None, trans_type=None,
                        date_from=None, date_to=None):
    """
    Tìm kiếm giao dịch theo nhiều tiêu chí (lọc kết hợp).
    Tất cả tham số đều tùy chọn.

    Trả về: danh sách các Transaction phù hợp.
    """
    results = []
    current = transaction_list.head

    while current is not None:
        t = current.data
        match = True

        # Lọc theo từ khóa (ghi chú hoặc danh mục)
        if keyword:
            kw = keyword.lower()
            if kw not in t.note.lower() and kw not in t.category.lower():
                match = False

        # Lọc theo danh mục
        if category and t.category.lower() != category.lower():
            match = False

        # Lọc theo loại (thu/chi)
        if trans_type and t.type != trans_type:
            match = False

        # Lọc theo khoảng ngày
        if date_from or date_to:
            try:
                t_date = datetime.strptime(t.date, "%Y-%m-%d")
                if date_from:
                    df = datetime.strptime(date_from, "%Y-%m-%d")
                    if t_date < df:
                        match = False
                if date_to:
                    dt_end = datetime.strptime(date_to, "%Y-%m-%d")
                    if t_date > dt_end:
                        match = False
            except ValueError:
                match = False

        if match:
            results.append(t)

        current = current.next

    # Sắp xếp theo ngày giảm dần (Insertion Sort)
    for i in range(1, len(results)):
        key = results[i]
        j = i - 1
        while j >= 0 and results[j].date < key.date:
            results[j + 1] = results[j]
            j -= 1
        results[j + 1] = key

    return results
