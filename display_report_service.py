"""
Module 6: display_report_service.py
Định dạng và in bảng báo cáo tổng hợp định kỳ.
Thành viên C - Vinh
"""

from datetime import datetime
from analytics_service import calculateBalance, calculateCategoryRatios

def printLine(char = '-', width = 62):
    print(char * width)

def printHeader(title):
    printLine('=')
    print(f"    {title}")
    printLine("=")

def generateMonthlyReport(transaction_list, budget_list, month, year):
    """
    Liệt kê các khoản thu chi và danh mục vượt Ngân sách trong tháng
    Input: DSLK Giao dịch, DSLK Ngân sách, tháng, năm
    In bảng biểu báo cáo thu chi ra màn hình
    """
    printHeader(f"BÁO CÁO THÁNG {month:02d}/{year}")

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

    # Sắp xếp tăng dần theo ngày (Selection sort)
    for i in range(len(transactions_in_month) - 1):
        min_idx = i
        for j in range(i+1, len(transactions_in_month)):
            if transactions_in_month[j].date < transactions_in_month[min_idx].date:
                min_idx = j
            if min_idx != i:
                transactions_in_month[i], transactions_in_month[min_idx] = transactions_in_month[min_idx], transactions_in_month[i]

    # --- In danh sách giao dịch (đã sắp xếp) cùng tổng tiền thu, chi và số dư
    print(f"\n{"Ngày":<12} {"Loại":<5} {"Danh mục":<14} {"Số tiền":>14}     {"Ghi chú"}")
    printLine()
    total_income = 0.0
    total_expense = 0.0
    
    for t in transactions_in_month:
        trans_type = "THU" if t.type == "thu" else "CHI"
        print(f"{t.date:<12} {trans_type:<5} {t.category:<14} {t.amount:>14,.0f} {t.note}")
        if t.type == "thu":
            total_income += t.amount
        else:
            total_expense += t.amount
        
    if not transactions_in_month:
        print("     (Không có giao dịch nào trong tháng này)")

    printLine()
    print(f"{"Tổng thu":>43}: {total_income:>14,.0f} VND")
    print(f"{"Tổng chi":>43}: {total_expense:>14,.0f} VND")
    balance = total_income - total_expense
    sign = "+" if balance > 0 else ""
    print(f"{"Số dư:":>43} {" ":>1} {sign}{balance:>13,.0f} VND")

    # --- In tỷ lệ chi tiêu theo danh mục ---
    print("\n--- TỶ LỆ CHI TIÊU THEO DANH MỤC ---")
    total, ratios = calculateCategoryRatios(transaction_list, month, year)
    if ratios:
        print(f"{"Danh mục":<18} {"Số tiền":>14} {"Tỷ lệ":>7}")
        printLine()
        for cat, amt, pct in ratios:
            print(f"{cat:<18} {amt:>14,.0f} {pct:>6.1f}%")
    else:
        print("     (Không có dữ liệu về chi tiêu)")

    # --- In các mục vượt ngân sách
    print("\n--- CẢNH BÁO VƯỢT NGÂN SÁCH ---")
    exceeded = False

    # Tính tổng chi theo danh mục trong tháng
    cat_names = []
    cat_amounts = []

    for t in transactions_in_month:
        if t.type == "chi":
            found = False
            for i in range(len(cat_names)):
                if t.category == cat_names[i]:
                    found = True
                    cat_amounts[i] += t.amount
                    break
            if not found:
                cat_names.append(t.category)
                cat_amounts.append(t.amount)
    
    # Đối chiếu với ngân sách
    current = budget_list.head
    while current is not None:
        b = current.data
        if b.month == month and b.year == year:
            spent = 0.0
            for i in range(len(cat_names)):
                if cat_names[i] == b.category:
                    spent = cat_amounts[i]
                    break
            if spent > b.limit:
                over = spent - b.limit
                print(f"    !!!   {b.category:<14}: Hạn mức {b.limit:>12,.0f}  |  Đã chi {spent:>12,.0f}  |  Vượt {over:>12,.0f} VND")
                exceeded = True
        current = current.next
        
    if not exceeded:
        print("     Không có danh mục nào vượt ngân sách.")

    printLine("=")

def printAllBudgets(budget_list):
    """
    In ra toàn bộ ngân sách đã đặt
    Input: DSLK Ngân sách
    """
    printHeader("DANH SÁCH NGÂN SÁCH ĐÃ ĐẶT")
    current = budget_list.head
    count = 0
    print(f"{'Mã':<12} {'Danh mục':<15} {'Tháng/Năm':<12} {'Hạn mức':>15}")
    printLine()
    while current is not None:
        b = current.data
        print(f"{b.id:<12} {b.category:<15} {b.month:02d}/{b.year}      {b.limit:>15,,.0f} VND")
        count += 1
        current = current.next
    printLine()
    if count == 0:
        print("  (Chưa có ngân sách nào)")
    else:
        print(f"  Tổng: {count} ngân sách")


def printSearchResults(results):
    """
    In ra kết quả tìm kiếm giao dịch
    Input: danh sách các giao dịch thỏa mãn tiêu chí
    """
    printHeader(f"KẾT QUẢ TÌM KIẾM ({len(results)} giao dịch)")
    if not results:
        print("  Không tìm thấy giao dịch phù hợp.")
    else:
        print(f"{'Mã':<12} {'Ngày':<12} {'Loại':<5} {'Danh mục':<14} {'Số tiền':>14}  Ghi chú")
        printLine()
        for t in results:
            loai = "THU" if t.type == "thu" else "CHI"
            print(f"{t.id:<12} {t.date:<12} {loai:<5} {t.category:<14} {t.amount:>14,,.0f}  {t.note}")
    printLine("=")

def printBalanceSummary(transaction_list):
    """
    In ra số dư tổng thể
    Input: DSLK Giao dịch
    """
    balance, total_income, total_expense = calculateBalance(transaction_list)
    printHeader("SỐ DƯ TỔNG THỂ")
    print(f"  Tổng Thu    : {total_income:>15,,.0f} VND")
    print(f"  Tổng Chi    : {total_expense:>15,,.0f} VND")
    printLine()
    sign = "+" if balance >= 0 else ""
    status = "Dư" if balance >= 0 else "Âm"
    print(f"  {status:<12}: {sign}{balance:>14,,.0f} VND")
    printLine("=")
