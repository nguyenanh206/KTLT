import os
import time
from datetime import datetime

from budget_checker import checkBudgetExceeded
from models_manager import Budget, Transaction


_id_counter = 0


def _generateId(prefix="T"):
    global _id_counter
    _id_counter += 1
    try:
        ts = time.time_ns()
    except AttributeError:
        ts = int(time.time() * 1_000_000)

    raw = ts ^ (os.getpid() << 17) ^ (_id_counter * 2654435761)
    return prefix + format(raw & 0xFFFFFFFF, "08X")


def _categoryByNumber(raw):
    if raw == "1":
        return "An uong"
    if raw == "2":
        return "Di lai"
    if raw == "3":
        return "Hoc tap"
    if raw == "4":
        return "Giai tri"
    if raw == "5":
        return "Y te"
    if raw == "6":
        return "Tien nha"
    if raw == "7":
        return "Luong"
    if raw == "8":
        return "Phu cap"
    if raw == "9":
        return "Khac"
    return None


def inputTransaction():
    print("\n--- NHAP GIAO DICH MOI ---")
    print("(Nhap 0 de huy)")

    while True:
        choice = input("Loai giao dich (1 = Thu, 2 = Chi): ").strip()
        if choice == "0":
            return None
        if choice in ("1", "2"):
            trans_type = "thu" if choice == "1" else "chi"
            break
        print("  Vui long chon 1 hoac 2.")

    while True:
        raw = input("So tien (VND): ").strip()
        if raw == "0":
            return None
        try:
            amount = float(raw.replace(",", ""))
            if amount > 0:
                break
        except ValueError:
            pass
        print("  So tien khong hop le.")

    print("Danh muc:")
    print("  1. An uong")
    print("  2. Di lai")
    print("  3. Hoc tap")
    print("  4. Giai tri")
    print("  5. Y te")
    print("  6. Tien nha")
    print("  7. Luong")
    print("  8. Phu cap")
    print("  9. Khac")
    while True:
        raw = input("Chon so hoac nhap ten danh muc: ").strip()
        if raw == "0":
            return None
        category = _categoryByNumber(raw)
        if category is not None:
            break
        if len(raw) >= 2:
            category = raw.capitalize()
            break
        print("  Danh muc khong hop le.")

    today = datetime.today().strftime("%Y-%m-%d")
    while True:
        raw = input(f"Ngay (YYYY-MM-DD) [Enter = {today}]: ").strip()
        if raw == "":
            date = today
            break
        try:
            datetime.strptime(raw, "%Y-%m-%d")
            date = raw
            break
        except ValueError:
            print("  Ngay khong hop le.")

    note = input("Ghi chu: ").strip()
    return Transaction(_generateId("T"), amount, category, trans_type, date, note)


def modifyTransaction(transaction_list, trans_id):
    t = transaction_list.findById(trans_id)
    if t is None:
        print(f"  Khong tim thay giao dich ma: {trans_id}")
        return False

    print(f"\n--- SUA GIAO DICH [{trans_id}] ---")
    print("(Enter de giu nguyen gia tri cu)")

    raw = input(f"Loai moi (thu/chi) [{t.type}]: ").strip().lower()
    if raw in ("thu", "chi"):
        t.type = raw

    raw = input(f"So tien moi [{t.amount:,.0f}]: ").strip()
    if raw:
        try:
            amount = float(raw.replace(",", ""))
            if amount > 0:
                t.amount = amount
        except ValueError:
            print("  So tien khong hop le, giu gia tri cu.")

    raw = input(f"Danh muc moi [{t.category}]: ").strip()
    if raw:
        t.category = raw.capitalize()

    raw = input(f"Ngay moi [{t.date}]: ").strip()
    if raw:
        try:
            datetime.strptime(raw, "%Y-%m-%d")
            t.date = raw
        except ValueError:
            print("  Ngay khong hop le, giu gia tri cu.")

    raw = input(f"Ghi chu moi [{t.note}]: ").strip()
    if raw:
        t.note = raw

    print("  Giao dich da duoc cap nhat.")
    return True


def updateBudget(budget_list, category, limit, month, year):
    category = category.strip().capitalize()
    limit = float(limit)
    month = int(month)
    year = int(year)

    current = budget_list.head
    while current is not None:
        b = current.data
        if b.category.lower() == category.lower() and b.month == month and b.year == year:
            b.limit = limit
            print(f"  Da cap nhat ngan sach: {category} {month:02d}/{year} = {limit:,.0f} VND")
            return budget_list
        current = current.next

    budget_list.addNode(Budget(_generateId("B"), category, limit, month, year))
    print(f"  Da them ngan sach moi: {category} {month:02d}/{year} = {limit:,.0f} VND")
    return budget_list


def addTransactionWithCheck(transaction_list, budget_list, t):
    if t is None:
        return transaction_list

    if t.type == "chi":
        exceeded, spent, budget_limit = checkBudgetExceeded(transaction_list, budget_list, t)
        if exceeded:
            total_after = spent + t.amount
            print("\n  CANH BAO VUOT HAN MUC!")
            print(f"  Danh muc : {t.category}")
            print(f"  Da chi   : {spent:,.0f} VND")
            print(f"  Han muc  : {budget_limit:,.0f} VND")
            print(f"  Sau them : {total_after:,.0f} VND")

    transaction_list.addNode(t)
    print(f"  Da them giao dich [{t.id}]: {t.type.upper()} {t.amount:,.0f} VND - {t.category}")
    return transaction_list
