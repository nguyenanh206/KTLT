
from decimal import MAX_PREC
from datetime import datetime

def calculateBalance(transaction_list):
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


def calculateCategoryRatios(transaction_list, month = None, year = None):
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
    for amount in cat_amounts:
        total += amount
    # Tính phần trăm và đưa kết quả vào mảng kết quả
    result = []
    for i in range(len(cat_names)):
        percent = (cat_amounts[i] / total * 100) if total > 0 else 0.0
        result.append((cat_names[i], cat_amounts[i], percent))
    # Sắp xếp giảm dần theo amount (dùng bubble sort)
    n = len(result)
    for i in range(n - 1):
        for j in range(n - 1 - i):
            if result[j][1] < result[j+1][1]:
                result[j], result[j+1] = result[j+1], result[j]

    return total, result

def searchTransactions(transaction_list, keyword = None, category = None, trans_type = None,
                        date_from = None, date_to = None, id = None):
    results = []
    current = transaction_list.head

    while current is not None:
        t = current.data
        match = True
        # Lọc theo từ khóa (danh mục hoặc ghi chú)
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
                    dt = datetime.strptime(date_to, "%Y-%m-%d")
                    if t.date > dt:
                        match = False
            except ValueError:
                match = False
        
        if match:
            results.append(t)

        current = current.next

    # Sắp xếp giảm dần theo ngày (Selection sort)
    for i in range(len(results) - 1):
        max_idx = i
        for j in range(i+1, len(results)):
            if results[max_idx].date < results[j].date:
                max_idx = j
        if max_idx != i:
            results[i], results[max_idx] = results[max_idx], results[i]
    
    return results
