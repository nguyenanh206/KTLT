"""
Module 7: program_controller.py
Xây dựng giao diện Menu dòng lệnh và điều phối các tác vụ.
Thành viên A - Quang Anh
"""

from datetime import datetime
from ktlt import loadDataFromFile, saveDataToFile
from expense_services import inputTransaction, modifyTransaction, updateBudget, addTransactionWithCheck
from analytics_service import searchTransactions
from display_report_service import (
    generateMonthlyReport, printAllBudgets,
    printSearchResults, printBalanceSummary
)


def displayMainMenu():
    """Hiển thị menu chính và nhận lựa chọn"""
    print("\n" + "=" * 62)
    print("       QUẢN LÝ CHI TIÊU CÁ NHÂN - v1.0")
    print("=" * 62)
    print("  1. Thêm giao dịch mới (Thu / Chi)")
    print("  2. Xem / Tìm kiếm giao dịch")
    print("  3. Sửa giao dịch")
    print("  4. Xóa giao dịch")
    print("  5. Đặt / Cập nhật ngân sách danh mục")
    print("  6. Xem danh sách ngân sách")
    print("  7. Xem số dư tổng thể")
    print("  8. Báo cáo tháng")
    print("  0. Lưu & Thoát")
    print("-" * 62)
    choice = input("  Chọn tác vụ: ").strip()
    return choice


def run():
    """Hàm chính điều hướng toàn bộ chương trình"""
    print("\n  Đang nạp dữ liệu từ file...")
    transaction_list, budget_list = loadDataFromFile()
    print(f"  ✓ Đã nạp {transaction_list.size()} giao dịch và {budget_list.size()} ngân sách.")

    while True:
        choice = displayMainMenu()

        # ── 1. THÊM GIAO DỊCH ──────────────────────────────────
        if choice == "1":
            t = inputTransaction()
            if t:
                addTransactionWithCheck(transaction_list, budget_list, t)
                ok = saveDataToFile(transaction_list, budget_list)
                if ok:
                    print("  ✓ Đã lưu dữ liệu.")

        # ── 2. XEM / TÌM KIẾM ──────────────────────────────────
        elif choice == "2":
            print("\n--- TÌM KIẾM GIAO DỊCH ---")
            print("  (Để trống và Enter để liệt kê tất cả)")
            keyword  = input("  Từ khóa (ghi chú/danh mục): ").strip() or None
            cat      = input("  Danh mục cụ thể: ").strip() or None
            ttype    = input("  Loại [thu/chi/(để trống)]: ").strip().lower() or None
            df       = input("  Từ ngày (YYYY-MM-DD): ").strip() or None
            dt_end   = input("  Đến ngày (YYYY-MM-DD): ").strip() or None

            results = searchTransactions(transaction_list, keyword, cat, ttype, df, dt_end)
            printSearchResults(results)

        # ── 3. SỬA GIAO DỊCH ───────────────────────────────────
        elif choice == "3":
            tid = input("\n  Nhập mã giao dịch cần sửa: ").strip().upper()
            if modifyTransaction(transaction_list, tid):
                saveDataToFile(transaction_list, budget_list)
                print("  ✓ Đã lưu thay đổi.")

        # ── 4. XÓA GIAO DỊCH ───────────────────────────────────
        elif choice == "4":
            tid = input("\n  Nhập mã giao dịch cần xóa: ").strip().upper()
            t = transaction_list.findById(tid)
            if t:
                confirm = input(f"  Xác nhận xóa [{tid}] - {t.type.upper()} {t.amount:,.0f} VND - {t.category}? (y/n): ")
                if confirm.lower() == "y":
                    transaction_list.deleteNode(tid)
                    saveDataToFile(transaction_list, budget_list)
                    print("  ✓ Đã xóa giao dịch.")
            else:
                print(f"  Không tìm thấy giao dịch mã: {tid}")

        # ── 5. ĐẶT NGÂN SÁCH ───────────────────────────────────
        elif choice == "5":
            print("\n--- ĐẶT NGÂN SÁCH DANH MỤC ---")
            category = input("  Tên danh mục: ").strip().capitalize()
            if not category:
                print("  Danh mục không được trống.")
                continue
            try:
                limit = float(input("  Hạn mức chi (VND): ").replace(",", ""))
                raw_month = input(f"  Tháng [{datetime.today().month}]: ").strip()
                month = int(raw_month) if raw_month else datetime.today().month
                raw_year = input(f"  Năm [{datetime.today().year}]: ").strip()
                year = int(raw_year) if raw_year else datetime.today().year
                if not (1 <= month <= 12):
                    raise ValueError
                updateBudget(budget_list, category, limit, month, year)
                saveDataToFile(transaction_list, budget_list)
                print("  ✓ Đã lưu ngân sách.")
            except (ValueError, AttributeError):
                print("  Dữ liệu không hợp lệ.")

        # ── 6. XEM NGÂN SÁCH ───────────────────────────────────
        elif choice == "6":
            printAllBudgets(budget_list)

        # ── 7. SỐ DƯ TỔNG THỂ ──────────────────────────────────
        elif choice == "7":
            printBalanceSummary(transaction_list)

        # ── 8. BÁO CÁO THÁNG ───────────────────────────────────
        elif choice == "8":
            try:
                raw_month = input(f"\n  Tháng [{datetime.today().month}]: ").strip()
                month = int(raw_month) if raw_month else datetime.today().month
                raw_year = input(f"  Năm [{datetime.today().year}]: ").strip()
                year = int(raw_year) if raw_year else datetime.today().year
                if not (1 <= month <= 12):
                    raise ValueError
                generateMonthlyReport(transaction_list, budget_list, month, year)
            except ValueError:
                print("  Tháng/Năm không hợp lệ.")

        # ── 0. THOÁT ────────────────────────────────────────────
        elif choice == "0":
            print("\n  Đang lưu dữ liệu lần cuối...")
            saveDataToFile(transaction_list, budget_list)
            print("  Cảm ơn bạn đã sử dụng. Tạm biệt!")
            break

        else:
            print("  Lựa chọn không hợp lệ. Vui lòng thử lại.")
