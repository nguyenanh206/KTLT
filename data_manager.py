"""
Module 2: data_manager.py
Quản lý đọc/ghi dữ liệu giữa RAM (DSLK) và file JSON trong thư mục data/
Thành viên A - Quang Anh
"""

import json
import os
from models import Transaction, Budget, LinkedList

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
TRANSACTIONS_FILE = os.path.join(DATA_DIR, "transactions.json")
BUDGETS_FILE = os.path.join(DATA_DIR, "budgets.json")


def _ensureDataDir():
    """Đảm bảo thư mục data/ tồn tại"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def loadDataFromFile():
    """
    Đọc toàn bộ giao dịch và ngân sách từ file khi khởi động.
    Trả về: (transaction_list: LinkedList, budget_list: LinkedList)
    """
    _ensureDataDir()
    transaction_list = LinkedList()
    budget_list = LinkedList()

    # --- Đọc giao dịch ---
    if os.path.exists(TRANSACTIONS_FILE):
        try:
            with open(TRANSACTIONS_FILE, "r", encoding="utf-8") as f:
                raw = f.read().strip()
                if raw:
                    data = json.loads(raw)
                    for item in data:
                        t = Transaction.from_dict(item)
                        transaction_list.addNode(t)
        except (json.JSONDecodeError, KeyError):
            print("[Cảnh báo] File transactions.json bị lỗi, khởi tạo danh sách rỗng.")

    # --- Đọc ngân sách ---
    if os.path.exists(BUDGETS_FILE):
        try:
            with open(BUDGETS_FILE, "r", encoding="utf-8") as f:
                raw = f.read().strip()
                if raw:
                    data = json.loads(raw)
                    for item in data:
                        b = Budget.from_dict(item)
                        budget_list.addNode(b)
        except (json.JSONDecodeError, KeyError):
            print("[Cảnh báo] File budgets.json bị lỗi, khởi tạo danh sách rỗng.")

    return transaction_list, budget_list


def saveDataToFile(transaction_list, budget_list):
    """
    Ghi toàn bộ dữ liệu DSLK xuống file JSON.
    Trả về True nếu thành công, False nếu thất bại.
    """
    _ensureDataDir()
    try:
        # --- Ghi giao dịch ---
        transactions_arr = []
        current = transaction_list.head
        while current is not None:
            transactions_arr.append(current.data.to_dict())
            current = current.next

        with open(TRANSACTIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(transactions_arr, f, ensure_ascii=False, indent=2)

        # --- Ghi ngân sách ---
        budgets_arr = []
        current = budget_list.head
        while current is not None:
            budgets_arr.append(current.data.to_dict())
            current = current.next

        with open(BUDGETS_FILE, "w", encoding="utf-8") as f:
            json.dump(budgets_arr, f, ensure_ascii=False, indent=2)

        return True
    except IOError as e:
        print(f"[Lỗi] Không thể ghi file: {e}")
        return False
