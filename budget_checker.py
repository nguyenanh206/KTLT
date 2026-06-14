from datetime import datetime


def checkBudgetExceeded(transaction_list, budget_list, new_transaction):
    try:
        dt = datetime.strptime(new_transaction.date, "%Y-%m-%d")
        month = dt.month
        year = dt.year
    except ValueError:
        return False, 0.0, 0.0

    category = new_transaction.category

    # Tính tổng đã chi
    tong_chi = 0.0
    current = transaction_list.head
    while current is not None:
        t = current.data
        if t.type == "chi" and t.category == category:
            try:
                t_date = datetime.strptime(t.date, "%Y-%m-%d")
                if t_date.month == month and t_date.year == year:
                    tong_chi += t.amount
            except ValueError:
                pass
        current = current.next

    # Lấy hạn mức ngân sách
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
        return False, tong_chi, 0.0

    over_budget = (tong_chi + new_transaction.amount) > budget_limit
    return over_budget, tong_chi, budget_limit
