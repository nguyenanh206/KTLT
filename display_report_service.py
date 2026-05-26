"""
Module 6: display_report_service.py
Định dạng và in bảng báo cáo tổng hợp định kỳ.
Thành viên C - Vinh
"""

from datetime import datetime
from analytics_service import calculateBalance, calculateCategoryRatios


def _printLine(char="-", width=62):
    print(char * width)


def _printHeader(title):
    _printLine("=")
    print(f"  {title}")
    _printLine("=")


def generateMonthlyReport(transaction_list, budget_list, month, year):
    """
    Liệt kê các khoản thu chi và mục vượt budget trong tháng.
    In bảng biểu văn bản ra màn hình.
    """
    _printHeader(f"BÁO CÁO THÁNG {month:02d}/{year}")

    # --- Lọc giao dịch trong tháng ---
    transactions_in_month = []
    current = transaction_list.head
    while current is not None:
        t = current.data
        try:
            dt = datetime.strptime(t.date, "%Y-%m-%d")
            if dt.month == month and dt.year == year:
                transactions_in_month.append(t)
        except ValueError:
            pass
        current = current.next

    # Sắp xếp theo ngày tăng dần
    for i in range(1, len(transactions_in_month)):
        key = transactions_in_month[i]
        j = i - 1
        while j >= 0 and transactions_in_month[j].date > key.date:
            transactions_in_month[j + 1] = transactions_in_month[j]
            j -= 1
        transactions_in_month[j + 1] = key

    # --- In danh sách giao dịch ---
    print(f"\n{'Ngày':<12} {'Loại':<5} {'Danh mục':<14} {'Số tiền':>14}  Ghi chú")
    _printLine()
    total_thu = 0.0
    total_chi = 0.0
    for t in transactions_in_month:
        loai = "THU" if t.type == "thu" else "CHI"
        print(f"{t.date:<12} {loai:<5} {t.category:<14} {t.amount:>14,.0f}  {t.note}")
        if t.type == "thu":
            total_thu += t.amount
        else:
            total_chi += t.amount

    if not transactions_in_month:
        print("  (Không có giao dịch trong tháng này)")

    _printLine()
    print(f"{'Tổng Thu':>43}: {total_thu:>14,.0f} VND")
    print(f"{'Tổng Chi':>43}: {total_chi:>14,.0f} VND")
    balance = total_thu - total_chi
    sign = "+" if balance >= 0 else ""
    print(f"{'Số dư':>43}: {sign}{balance:>13,.0f} VND")

    # --- Tỷ lệ chi tiêu theo danh mục ---
    print("\n--- TỶ LỆ CHI TIÊU THEO DANH MỤC ---")
    ratios, total = calculateCategoryRatios(transaction_list, month, year)
    if ratios:
        print(f"{'Danh mục':<18} {'Số tiền':>14}  {'Tỷ lệ':>7}  Biểu đồ")
        _printLine()
        for cat, amt, pct in ratios:
            bar_len = int(pct / 5)
            bar = "█" * bar_len
            print(f"{cat:<18} {amt:>14,.0f}  {pct:>6.1f}%  {bar}")
    else:
        print("  (Không có dữ liệu chi tiêu)")

    # --- Các mục vượt ngân sách ---
    print("\n--- CẢNH BÁO VƯỢT NGÂN SÁCH ---")
    found_exceeded = False

    # Tính tổng chi theo danh mục trong tháng
    cat_names = []
    cat_spent = []
    for t in transactions_in_month:
        if t.type == "chi":
            found = False
            for i in range(len(cat_names)):
                if cat_names[i] == t.category:
                    cat_spent[i] += t.amount
                    found = True
                    break
            if not found:
                cat_names.append(t.category)
                cat_spent.append(t.amount)

    # Đối chiếu với ngân sách
    current = budget_list.head
    while current is not None:
        b = current.data
        if b.month == month and b.year == year:
            spent = 0.0
            for i in range(len(cat_names)):
                if cat_names[i] == b.category:
                    spent = cat_spent[i]
                    break
            if spent > b.limit:
                over = spent - b.limit
                print(f"  ⚠️  {b.category:<14}: Hạn mức {b.limit:>12,.0f}  |  Đã chi {spent:>12,.0f}  |  Vượt {over:>10,.0f} VND")
                found_exceeded = True
        current = current.next

    if not found_exceeded:
        print("  ✓ Không có danh mục nào vượt ngân sách.")

    _printLine("=")


def printAllBudgets(budget_list):
    """In toàn bộ ngân sách đã đặt"""
    _printHeader("DANH SÁCH NGÂN SÁCH ĐÃ ĐẶT")
    current = budget_list.head
    count = 0
    print(f"{'Mã':<12} {'Danh mục':<15} {'Tháng/Năm':<12} {'Hạn mức':>15}")
    _printLine()
    while current is not None:
        b = current.data
        print(f"{b.id:<12} {b.category:<15} {b.month:02d}/{b.year}      {b.limit:>15,.0f} VND")
        count += 1
        current = current.next
    _printLine()
    if count == 0:
        print("  (Chưa có ngân sách nào)")
    else:
        print(f"  Tổng: {count} ngân sách")


def printSearchResults(results):
    """In kết quả tìm kiếm giao dịch"""
    _printHeader(f"KẾT QUẢ TÌM KIẾM ({len(results)} giao dịch)")
    if not results:
        print("  Không tìm thấy giao dịch phù hợp.")
    else:
        print(f"{'Mã':<12} {'Ngày':<12} {'Loại':<5} {'Danh mục':<14} {'Số tiền':>14}  Ghi chú")
        _printLine()
        for t in results:
            loai = "THU" if t.type == "thu" else "CHI"
            print(f"{t.id:<12} {t.date:<12} {loai:<5} {t.category:<14} {t.amount:>14,.0f}  {t.note}")
    _printLine("=")


def printBalanceSummary(transaction_list):
    """In tóm tắt số dư tổng thể"""
    balance, total_income, total_expense = calculateBalance(transaction_list)
    _printHeader("SỐ DƯ TỔNG THỂ")
    print(f"  Tổng Thu    : {total_income:>15,.0f} VND")
    print(f"  Tổng Chi    : {total_expense:>15,.0f} VND")
    _printLine()
    sign = "+" if balance >= 0 else ""
    status = "Dư" if balance >= 0 else "Âm"
    print(f"  {status:<12}: {sign}{balance:>14,.0f} VND")
    _printLine("=")
