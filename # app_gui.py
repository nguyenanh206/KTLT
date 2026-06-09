"""
gui_app.py
Giao diện Desktop Dashboard - Quản lý Chi tiêu Cá nhân
Thư viện: CustomTkinter (CTk)

Cách nhúng backend:
    - Đặt file này cùng thư mục với: models_manager.py, analytics_service.py,
      budget_checker.py, expense_services.py
    - Chạy: python gui_app.py

Cài đặt thư viện:
    pip install customtkinter
"""

import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox

# ──────────────────────────────────────────────────────────────
#  NHÚNG BACKEND  (bỏ comment khi chạy cùng các file backend)
# ──────────────────────────────────────────────────────────────
from models_manager   import LinkedList, loadDataFromFile, saveDataToFile
from models_manager   import Transaction, Budget
from analytics_service import calculateBalance, calculateCategoryRatios, searchTransactions
from expense_services  import addTransactionWithCheck, updateBudget, _generateId
from budget_checker    import checkBudgetExceeded

# Đường dẫn file dữ liệu
TRANS_FILE  = "data/transactions.txt"
BUDGET_FILE = "data/budgets.txt"

# ──────────────────────────────────────────────────────────────
#  CẤU HÌNH GIAO DIỆN TOÀN CỤC
# ──────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ──── Bảng màu tùy chỉnh ────
CLR_BG        = "#1a1a2e"   # nền tối chính
CLR_SIDEBAR   = "#16213e"   # sidebar
CLR_CARD      = "#0f3460"   # thẻ thống kê
CLR_ROW_ODD   = "#1e1e3a"   # hàng lẻ bảng
CLR_ROW_EVEN  = "#16213e"   # hàng chẵn bảng
CLR_GREEN     = "#4ade80"   # thu nhập / an toàn
CLR_RED       = "#f87171"   # chi tiêu / nguy hiểm
CLR_YELLOW    = "#fbbf24"   # cảnh báo 80%
CLR_BLUE      = "#60a5fa"   # nhấn mạnh
CLR_TEXT      = "#e2e8f0"   # chữ chính
CLR_SUBTEXT   = "#94a3b8"   # chữ phụ
CLR_BORDER    = "#334155"   # viền

FONT_TITLE    = ("Segoe UI", 18, "bold")
FONT_HEADING  = ("Segoe UI", 13, "bold")
FONT_BODY     = ("Segoe UI", 12)
FONT_SMALL    = ("Segoe UI", 10)
FONT_MONO     = ("Consolas",  12)

CATEGORIES = ["An uong", "Di lai", "Hoc tap", "Giai tri", "Y te",
              "Tien nha", "Luong", "Phu cap", "Khac"]


# ══════════════════════════════════════════════════════════════
#  POPUP: CẢNH BÁO VƯỢT NGÂN SÁCH
# ══════════════════════════════════════════════════════════════
class BudgetWarningPopup(ctk.CTkToplevel):
    """
    Cửa sổ popup hiển thị cảnh báo khi khoản chi vượt hạn mức.
    Gọi: BudgetWarningPopup(parent, category, spent, limit, new_amount)
    """
    def __init__(self, parent, category, spent, limit, new_amount):
        super().__init__(parent)
        self.title("⚠  Cảnh báo Ngân sách")
        self.geometry("420x280")
        self.resizable(False, False)
        self.grab_set()                 # Modal: khóa cửa sổ cha
        self.configure(fg_color=CLR_BG)

        # Canh giữa so với cửa sổ cha
        px = parent.winfo_x() + (parent.winfo_width()  - 420) // 2
        py = parent.winfo_y() + (parent.winfo_height() - 280) // 2
        self.geometry(f"+{px}+{py}")

        total_after = spent + new_amount
        over        = total_after - limit

        # Icon và tiêu đề
        ctk.CTkLabel(self, text="⚠", font=("Segoe UI", 48),
                     text_color=CLR_YELLOW).pack(pady=(20, 4))
        ctk.CTkLabel(self, text="VƯỢT HẠN MỨC CHI TIÊU",
                     font=("Segoe UI", 15, "bold"),
                     text_color=CLR_RED).pack()

        # Chi tiết
        detail = (
            f"Danh mục : {category}\n"
            f"Hạn mức  : {limit:>12,.0f} VND\n"
            f"Đã chi   : {spent:>12,.0f} VND\n"
            f"Khoản mới: {new_amount:>12,.0f} VND\n"
            f"─────────────────────────────\n"
            f"Vượt thêm: {over:>12,.0f} VND"
        )
        ctk.CTkLabel(self, text=detail, font=FONT_MONO,
                     text_color=CLR_TEXT, justify="left").pack(pady=12)

        ctk.CTkButton(self, text="Đã hiểu, vẫn thêm",
                      fg_color=CLR_RED, hover_color="#dc2626",
                      command=self.destroy).pack(pady=(0, 16))


# ══════════════════════════════════════════════════════════════
#  POPUP: SỬA GIAO DỊCH
# ══════════════════════════════════════════════════════════════
class EditTransactionPopup(ctk.CTkToplevel):
    """
    Cửa sổ popup cho phép sửa thông tin một giao dịch.
    Gọi: EditTransactionPopup(parent, transaction_obj, on_save_callback)
    """
    def __init__(self, parent, transaction, on_save):
        super().__init__(parent)
        self.title("Sửa giao dịch")
        self.geometry("400x420")
        self.resizable(False, False)
        self.grab_set()
        self.configure(fg_color=CLR_BG)

        px = parent.winfo_x() + (parent.winfo_width()  - 400) // 2
        py = parent.winfo_y() + (parent.winfo_height() - 420) // 2
        self.geometry(f"+{px}+{py}")

        self.transaction = transaction
        self.on_save     = on_save

        ctk.CTkLabel(self, text=f"Sửa giao dịch [{transaction.id}]",
                     font=FONT_HEADING, text_color=CLR_BLUE).pack(pady=(16, 8))

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="x", padx=24)

        def row(label, default=""):
            ctk.CTkLabel(form, text=label, font=FONT_SMALL,
                         text_color=CLR_SUBTEXT, anchor="w").pack(fill="x", pady=(8, 2))
            e = ctk.CTkEntry(form, font=FONT_BODY, fg_color=CLR_SIDEBAR,
                             border_color=CLR_BORDER)
            e.insert(0, str(default))
            e.pack(fill="x")
            return e

        # Loại giao dịch
        ctk.CTkLabel(form, text="Loại", font=FONT_SMALL,
                     text_color=CLR_SUBTEXT, anchor="w").pack(fill="x", pady=(8, 2))
        self.seg_type = ctk.CTkSegmentedButton(
            form, values=["Thu nhập", "Chi tiêu"], font=FONT_BODY,
            selected_color=CLR_BLUE, unselected_color=CLR_SIDEBAR)
        self.seg_type.set("Thu nhập" if transaction.type == "thu" else "Chi tiêu")
        self.seg_type.pack(fill="x")

        self.ent_amount   = row("Số tiền (VND)",  f"{transaction.amount:,.0f}")
        self.ent_category = row("Danh mục",        transaction.category)
        self.ent_date     = row("Ngày (YYYY-MM-DD)", transaction.date)
        self.ent_note     = row("Ghi chú",          transaction.note)

        ctk.CTkButton(self, text="💾  Lưu thay đổi",
                      command=self._save,
                      fg_color=CLR_BLUE, hover_color="#2563eb").pack(pady=16)

    def _save(self):
        """Thu thập giá trị từ form và gọi callback để lưu"""
        try:
            amount = float(self.ent_amount.get().replace(",", ""))
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Lỗi", "Số tiền không hợp lệ.", parent=self)
            return

        date_str = self.ent_date.get().strip()
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Lỗi", "Ngày không đúng định dạng YYYY-MM-DD.", parent=self)
            return

        # Cập nhật trực tiếp vào đối tượng Transaction trong DSLK
        self.transaction.type     = "thu" if self.seg_type.get() == "Thu nhập" else "chi"
        self.transaction.amount   = amount
        self.transaction.category = self.ent_category.get().strip().capitalize()
        self.transaction.date     = date_str
        self.transaction.note     = self.ent_note.get().strip()

        self.on_save()      # Gọi callback refresh dashboard
        self.destroy()


# ══════════════════════════════════════════════════════════════
#  WIDGET TIỆN ÍCH
# ══════════════════════════════════════════════════════════════
def make_label_pair(parent, top_text, bottom_text="—",
                    top_color=CLR_SUBTEXT, bottom_color=CLR_TEXT,
                    bottom_font=FONT_TITLE):
    """Tạo cặp label tiêu đề nhỏ + giá trị lớn dùng trong thẻ thống kê."""
    ctk.CTkLabel(parent, text=top_text, font=FONT_SMALL,
                 text_color=top_color).pack(anchor="w", padx=14, pady=(10, 2))
    lbl = ctk.CTkLabel(parent, text=bottom_text, font=bottom_font,
                       text_color=bottom_color)
    lbl.pack(anchor="w", padx=14, pady=(0, 10))
    return lbl


# ══════════════════════════════════════════════════════════════
#  LỚP ỨNG DỤNG CHÍNH
# ══════════════════════════════════════════════════════════════
class ExpenseApp(ctk.CTk):
    """
    Lớp ứng dụng chính.
    Toàn bộ giao diện được xây dựng trong __init__ và các phương thức _build_*.
    Dữ liệu backend được lưu trong self.transaction_list và self.budget_list.
    """

    def __init__(self):
        super().__init__()

        # ── Cấu hình cửa sổ chính ────────────────────────────
        self.title("Quản Lý Chi Tiêu Cá Nhân")
        self.geometry("1200x750")
        self.minsize(1000, 650)
        self.configure(fg_color=CLR_BG)

        # ── Nạp dữ liệu từ backend ───────────────────────────
        self.transaction_list, self.budget_list = self._load_data()

        # ── Biến trạng thái giao diện ────────────────────────
        self._filter_type    = ctk.StringVar(value="Tất cả")
        self._search_keyword = ctk.StringVar()
        self._search_keyword.trace_add("write", lambda *_: self.refresh_transaction_table())

        # ── Xây dựng bố cục ──────────────────────────────────
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()       # Cột trái: nav + form
        self._build_main_area()     # Cột phải: dashboard

        # ── Cập nhật dữ liệu lần đầu ─────────────────────────
        self.update_dashboard()

    # ──────────────────────────────────────────────────────────
    #  BACKEND BRIDGE  (nhúng logic duyệt DSLK vào đây)
    # ──────────────────────────────────────────────────────────

    def _load_data(self):
        """
        Nạp dữ liệu từ file.
        Trả về (transaction_list, budget_list).
        """
        tl = loadDataFromFile(TRANS_FILE)
        bl = loadDataFromFile(BUDGET_FILE)
        return tl, bl

    def _save_data(self):
        """Ghi toàn bộ dữ liệu xuống file."""
        saveDataToFile(self.transaction_list, TRANS_FILE)
        saveDataToFile(self.budget_list,      BUDGET_FILE)

    def on_add_click(self):
        """
        Xử lý nút 'Thêm giao dịch'.
        Đọc form → tạo Transaction → kiểm tra ngân sách → thêm vào DSLK → lưu file.
        """
        # 1. Thu thập và kiểm tra dữ liệu form
        trans_type = "thu" if self.seg_type.get() == "Thu nhập" else "chi"
        raw_amount = self.ent_amount.get().replace(",", "").strip()
        category   = self.opt_category.get().strip()
        date_str   = self.ent_date.get().strip()
        note       = self.ent_note.get().strip()

        if not raw_amount:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập số tiền.", parent=self)
            return
        try:
            amount = float(raw_amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Lỗi", "Số tiền phải là số dương.", parent=self)
            return

        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Lỗi", "Ngày không đúng định dạng YYYY-MM-DD.", parent=self)
            return

        # 2. Tạo đối tượng Transaction
        new_trans = Transaction(
            trans_id   = _generateId("T"),
            date       = date_str,
            trans_type = trans_type,
            amount     = amount,
            category   = category,
            note       = note
        )

        # 3. Kiểm tra vượt ngân sách (chỉ với khoản chi)
        if trans_type == "chi":
            exceeded, spent, budget_limit = checkBudgetExceeded(
                self.transaction_list, self.budget_list, new_trans)
            if exceeded:
                # Hiện popup cảnh báo; người dùng vẫn có thể thêm
                BudgetWarningPopup(self, category, spent, budget_limit, amount)

        # 4. Thêm vào DSLK và lưu file
        self.transaction_list.addNode(new_trans)
        self._save_data()

        # 5. Làm sạch form và cập nhật giao diện
        self._clear_transaction_form()
        self.update_dashboard()

    def on_add_budget_click(self):
        """
        Xử lý nút 'Đặt ngân sách'.
        Đọc form ngân sách → gọi updateBudget() → lưu file → refresh.
        """
        category  = self.opt_budget_cat.get().strip()
        raw_limit = self.ent_budget_limit.get().replace(",", "").strip()
        raw_month = self.ent_budget_month.get().strip()
        raw_year  = self.ent_budget_year.get().strip()

        if not raw_limit:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập hạn mức.", parent=self)
            return
        try:
            limit = float(raw_limit)
            month = int(raw_month)
            year  = int(raw_year)
            if not (1 <= month <= 12):
                raise ValueError
        except ValueError:
            messagebox.showerror("Lỗi", "Hạn mức / tháng / năm không hợp lệ.", parent=self)
            return

        updateBudget(self.budget_list, category, limit, month, year)
        self._save_data()
        self.update_dashboard()
        messagebox.showinfo("Thành công",
                            f"Đã đặt ngân sách {category} tháng {month:02d}/{year}:\n{limit:,.0f} VND",
                            parent=self)

    def on_edit_click(self, transaction):
        """Mở popup sửa giao dịch."""
        EditTransactionPopup(self, transaction, on_save=lambda: (
            self._save_data(), self.update_dashboard()
        ))

    def on_delete_click(self, trans_id):
        """Xóa giao dịch sau khi xác nhận."""
        if messagebox.askyesno("Xác nhận xóa",
                               f"Bạn có chắc muốn xóa giao dịch [{trans_id}]?",
                               parent=self):
            self.transaction_list.deleteNode(trans_id)
            self._save_data()
            self.update_dashboard()

    def update_dashboard(self):
        """
        Hàm trung tâm: cập nhật toàn bộ dashboard sau mỗi thay đổi dữ liệu.
        Gọi hàm này bất cứ khi nào DSLK thay đổi.
        """
        now = datetime.today()
        self._update_summary_cards(now.month, now.year)
        self._update_budget_tracker(now.month, now.year)
        self.refresh_transaction_table()

    # ──────────────────────────────────────────────────────────
    #  XÂY DỰNG GIAO DIỆN
    # ──────────────────────────────────────────────────────────

    def _build_sidebar(self):
        """Xây dựng cột sidebar bên trái."""
        sidebar = ctk.CTkFrame(self, fg_color=CLR_SIDEBAR, width=300,
                               corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_columnconfigure(0, weight=1)

        # ── Tiêu đề ứng dụng ───────────────────────────
        title_frame = ctk.CTkFrame(sidebar, fg_color=CLR_CARD, corner_radius=12)
        title_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(20, 8))
        ctk.CTkLabel(title_frame, text="💰", font=("Segoe UI", 28)).pack(pady=(10, 2))
        ctk.CTkLabel(title_frame, text="QUẢN LÝ\nCHI TIÊU",
                     font=("Segoe UI", 17, "bold"),
                     text_color=CLR_BLUE, justify="center").pack(pady=(0, 10))

        # ── Cuộn nội dung sidebar ───────────────────────
        scroll = ctk.CTkScrollableFrame(sidebar, fg_color="transparent",
                                        scrollbar_button_color=CLR_BORDER)
        scroll.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        sidebar.grid_rowconfigure(1, weight=1)

        self._build_transaction_form(scroll)
        self._build_budget_form(scroll)

    def _build_transaction_form(self, parent):
        """Form nhập giao dịch trong sidebar."""
        frame = ctk.CTkFrame(parent, fg_color=CLR_ROW_ODD, corner_radius=12)
        frame.pack(fill="x", padx=12, pady=(8, 4))

        ctk.CTkLabel(frame, text="➕  Thêm Giao Dịch",
                     font=FONT_HEADING, text_color=CLR_TEXT).pack(anchor="w", padx=12, pady=(12, 6))

        # Loại giao dịch (CTkSegmentedButton)
        self.seg_type = ctk.CTkSegmentedButton(
            frame, values=["Thu nhập", "Chi tiêu"],
            font=FONT_BODY,
            selected_color=CLR_BLUE,
            selected_hover_color="#2563eb",
            unselected_color=CLR_SIDEBAR,
            fg_color=CLR_SIDEBAR)
        self.seg_type.set("Chi tiêu")
        self.seg_type.pack(fill="x", padx=12, pady=4)

        # Số tiền
        ctk.CTkLabel(frame, text="Số tiền (VND)",
                     font=FONT_SMALL, text_color=CLR_SUBTEXT,
                     anchor="w").pack(fill="x", padx=12)
        self.ent_amount = ctk.CTkEntry(
            frame, placeholder_text="0", font=FONT_BODY,
            fg_color=CLR_SIDEBAR, border_color=CLR_BORDER)
        self.ent_amount.pack(fill="x", padx=12, pady=(2, 6))

        # Danh mục (CTkOptionMenu)
        ctk.CTkLabel(frame, text="Danh mục",
                     font=FONT_SMALL, text_color=CLR_SUBTEXT,
                     anchor="w").pack(fill="x", padx=12)
        self.opt_category = ctk.CTkOptionMenu(
            frame, values=CATEGORIES, font=FONT_BODY,
            fg_color=CLR_SIDEBAR, button_color=CLR_BLUE,
            dropdown_fg_color=CLR_SIDEBAR)
        self.opt_category.set(CATEGORIES[0])
        self.opt_category.pack(fill="x", padx=12, pady=(2, 6))

        # Ngày
        ctk.CTkLabel(frame, text="Ngày (YYYY-MM-DD)",
                     font=FONT_SMALL, text_color=CLR_SUBTEXT,
                     anchor="w").pack(fill="x", padx=12)
        self.ent_date = ctk.CTkEntry(
            frame, font=FONT_BODY,
            fg_color=CLR_SIDEBAR, border_color=CLR_BORDER)
        self.ent_date.insert(0, datetime.today().strftime("%Y-%m-%d"))
        self.ent_date.pack(fill="x", padx=12, pady=(2, 6))

        # Ghi chú
        ctk.CTkLabel(frame, text="Ghi chú",
                     font=FONT_SMALL, text_color=CLR_SUBTEXT,
                     anchor="w").pack(fill="x", padx=12)
        self.ent_note = ctk.CTkEntry(
            frame, placeholder_text="(tùy chọn)", font=FONT_BODY,
            fg_color=CLR_SIDEBAR, border_color=CLR_BORDER)
        self.ent_note.pack(fill="x", padx=12, pady=(2, 6))

        # Nút thêm
        ctk.CTkButton(frame, text="✔  Thêm giao dịch",
                      command=self.on_add_click,
                      font=FONT_BODY, fg_color=CLR_BLUE,
                      hover_color="#2563eb", height=36).pack(
            fill="x", padx=12, pady=(6, 14))

    def _build_budget_form(self, parent):
        """Form đặt ngân sách trong sidebar."""
        frame = ctk.CTkFrame(parent, fg_color=CLR_ROW_ODD, corner_radius=12)
        frame.pack(fill="x", padx=12, pady=(4, 12))

        ctk.CTkLabel(frame, text="🎯  Đặt Ngân Sách",
                     font=FONT_HEADING, text_color=CLR_TEXT).pack(anchor="w", padx=12, pady=(12, 6))

        # Danh mục ngân sách
        ctk.CTkLabel(frame, text="Danh mục",
                     font=FONT_SMALL, text_color=CLR_SUBTEXT,
                     anchor="w").pack(fill="x", padx=12)
        self.opt_budget_cat = ctk.CTkOptionMenu(
            frame, values=CATEGORIES, font=FONT_BODY,
            fg_color=CLR_SIDEBAR, button_color=CLR_BLUE,
            dropdown_fg_color=CLR_SIDEBAR)
        self.opt_budget_cat.set(CATEGORIES[0])
        self.opt_budget_cat.pack(fill="x", padx=12, pady=(2, 6))

        # Hạn mức
        ctk.CTkLabel(frame, text="Hạn mức (VND)",
                     font=FONT_SMALL, text_color=CLR_SUBTEXT,
                     anchor="w").pack(fill="x", padx=12)
        self.ent_budget_limit = ctk.CTkEntry(
            frame, placeholder_text="0", font=FONT_BODY,
            fg_color=CLR_SIDEBAR, border_color=CLR_BORDER)
        self.ent_budget_limit.pack(fill="x", padx=12, pady=(2, 6))

        # Tháng / Năm (2 cột)
        row_frame = ctk.CTkFrame(frame, fg_color="transparent")
        row_frame.pack(fill="x", padx=12)
        row_frame.columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(row_frame, text="Tháng", font=FONT_SMALL,
                     text_color=CLR_SUBTEXT).grid(row=0, column=0, sticky="w", padx=(0, 4))
        ctk.CTkLabel(row_frame, text="Năm", font=FONT_SMALL,
                     text_color=CLR_SUBTEXT).grid(row=0, column=1, sticky="w")

        self.ent_budget_month = ctk.CTkEntry(
            row_frame, font=FONT_BODY,
            fg_color=CLR_SIDEBAR, border_color=CLR_BORDER)
        self.ent_budget_month.insert(0, str(datetime.today().month))
        self.ent_budget_month.grid(row=1, column=0, sticky="ew", padx=(0, 4), pady=(2, 6))

        self.ent_budget_year = ctk.CTkEntry(
            row_frame, font=FONT_BODY,
            fg_color=CLR_SIDEBAR, border_color=CLR_BORDER)
        self.ent_budget_year.insert(0, str(datetime.today().year))
        self.ent_budget_year.grid(row=1, column=1, sticky="ew", pady=(2, 6))

        # Nút đặt ngân sách
        ctk.CTkButton(frame, text="💾  Lưu ngân sách",
                      command=self.on_add_budget_click,
                      font=FONT_BODY, fg_color="#7c3aed",
                      hover_color="#6d28d9", height=36).pack(
            fill="x", padx=12, pady=(6, 14))

    def _build_main_area(self):
        """Xây dựng khu vực dashboard chính bên phải."""
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=0, column=1, sticky="nsew", padx=12, pady=12)
        main.grid_rowconfigure(2, weight=1)   # bảng giao dịch dãn đầy
        main.grid_columnconfigure(0, weight=1)

        self._build_summary_cards(main)       # Hàng 0: 3 thẻ thống kê
        self._build_budget_tracker(main)      # Hàng 1: thanh ngân sách
        self._build_transaction_table(main)   # Hàng 2: bảng giao dịch

    # ── HÀNG 0: Thẻ thống kê ──────────────────────────────────

    def _build_summary_cards(self, parent):
        """Tạo 3 thẻ thống kê ngang: Số dư | Tổng Thu | Tổng Chi."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        row.grid_columnconfigure((0, 1, 2), weight=1)

        def make_card(col, icon, title, attr_name, color):
            card = ctk.CTkFrame(row, fg_color=CLR_CARD, corner_radius=14,
                                border_width=1, border_color=CLR_BORDER)
            card.grid(row=0, column=col, sticky="ew",
                      padx=(0 if col == 0 else 8, 0))
            ctk.CTkLabel(card, text=icon, font=("Segoe UI", 24)).pack(
                anchor="w", padx=14, pady=(12, 0))
            ctk.CTkLabel(card, text=title, font=FONT_SMALL,
                         text_color=CLR_SUBTEXT).pack(anchor="w", padx=14)
            lbl = ctk.CTkLabel(card, text="—", font=("Segoe UI", 20, "bold"),
                               text_color=color)
            lbl.pack(anchor="w", padx=14, pady=(4, 14))
            setattr(self, attr_name, lbl)

        make_card(0, "⚖", "Số dư hiện tại",    "lbl_balance",  CLR_BLUE)
        make_card(1, "📈", "Tổng Thu tháng này", "lbl_income",   CLR_GREEN)
        make_card(2, "📉", "Tổng Chi tháng này", "lbl_expense",  CLR_RED)

    def _update_summary_cards(self, month, year):
        """Tính toán và cập nhật 3 thẻ thống kê."""
        # Số dư tổng thể
        balance, total_income, total_expense = calculateBalance(self.transaction_list)

        # Thu/Chi trong tháng hiện tại
        inc_month = 0.0
        exp_month = 0.0
        current = self.transaction_list.head
        while current is not None:
            t = current.data
            try:
                dt = datetime.strptime(t.date, "%Y-%m-%d")
                if dt.month == month and dt.year == year:
                    if t.type == "thu":
                        inc_month += t.amount
                    else:
                        exp_month += t.amount
            except ValueError:
                pass
            current = current.next

        # Cập nhật label
        sign  = "+" if balance >= 0 else ""
        color = CLR_GREEN if balance >= 0 else CLR_RED
        self.lbl_balance.configure(
            text=f"{sign}{balance:,.0f} ₫", text_color=color)
        self.lbl_income.configure(
            text=f"+{inc_month:,.0f} ₫")
        self.lbl_expense.configure(
            text=f"-{exp_month:,.0f} ₫")

    # ── HÀNG 1: Theo dõi ngân sách ────────────────────────────

    def _build_budget_tracker(self, parent):
        """Tạo CTkScrollableFrame chứa các thanh tiến độ ngân sách."""
        wrapper = ctk.CTkFrame(parent, fg_color=CLR_CARD,
                               corner_radius=14, border_width=1,
                               border_color=CLR_BORDER)
        wrapper.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        wrapper.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(wrapper, text="📊  Theo dõi Ngân sách tháng này",
                     font=FONT_HEADING, text_color=CLR_TEXT).grid(
            row=0, column=0, sticky="w", padx=14, pady=(10, 4))

        self.budget_scroll = ctk.CTkScrollableFrame(
            wrapper, fg_color="transparent", height=130,
            scrollbar_button_color=CLR_BORDER)
        self.budget_scroll.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 10))
        self.budget_scroll.grid_columnconfigure(0, weight=1)

    def _update_budget_tracker(self, month, year):
        """Xóa và vẽ lại các thanh tiến độ ngân sách."""
        # Xóa widget cũ
        for w in self.budget_scroll.winfo_children():
            w.destroy()

        # Tính tổng chi từng danh mục trong tháng
        cat_spent = {}      # { category: spent_amount }
        current = self.transaction_list.head
        while current is not None:
            t = current.data
            if t.type == "chi":
                try:
                    dt = datetime.strptime(t.date, "%Y-%m-%d")
                    if dt.month == month and dt.year == year:
                        cat_spent[t.category] = cat_spent.get(t.category, 0.0) + t.amount
                except ValueError:
                    pass
            current = current.next

        # Duyệt DSLK ngân sách, vẽ từng thanh
        has_budget = False
        current = self.budget_list.head
        idx = 0
        while current is not None:
            b = current.data
            if b.month == month and b.year == year:
                has_budget = True
                spent = cat_spent.get(b.category, 0.0)
                ratio = min(spent / b.limit, 1.0) if b.limit > 0 else 0.0

                # Màu thanh theo mức độ
                if ratio >= 1.0:
                    bar_color = CLR_RED
                elif ratio >= 0.8:
                    bar_color = CLR_YELLOW
                else:
                    bar_color = CLR_GREEN

                row_bg = CLR_ROW_ODD if idx % 2 == 0 else CLR_ROW_EVEN
                item = ctk.CTkFrame(self.budget_scroll, fg_color=row_bg,
                                    corner_radius=8)
                item.pack(fill="x", pady=2, padx=4)
                item.grid_columnconfigure(0, weight=1)

                # Dòng chữ: tên + số tiền
                text_row = ctk.CTkFrame(item, fg_color="transparent")
                text_row.pack(fill="x", padx=10, pady=(6, 2))

                ctk.CTkLabel(text_row,
                             text=b.category,
                             font=FONT_BODY,
                             text_color=CLR_TEXT).pack(side="left")

                status = "⚠ VƯỢT" if ratio >= 1.0 else f"{ratio*100:.0f}%"
                status_color = CLR_RED if ratio >= 1.0 else (
                    CLR_YELLOW if ratio >= 0.8 else CLR_GREEN)
                ctk.CTkLabel(text_row,
                             text=f"{spent:,.0f} / {b.limit:,.0f} ₫  ({status})",
                             font=FONT_SMALL,
                             text_color=status_color).pack(side="right")

                # Thanh tiến độ
                prog = ctk.CTkProgressBar(item, height=8,
                                          progress_color=bar_color,
                                          fg_color=CLR_BORDER)
                prog.set(ratio)
                prog.pack(fill="x", padx=10, pady=(0, 8))
                idx += 1

            current = current.next

        if not has_budget:
            ctk.CTkLabel(self.budget_scroll,
                         text="Chưa đặt ngân sách nào cho tháng này.",
                         font=FONT_SMALL, text_color=CLR_SUBTEXT).pack(pady=12)

    # ── HÀNG 2: Bảng giao dịch ────────────────────────────────

    def _build_transaction_table(self, parent):
        """Tạo bộ lọc và bảng lịch sử giao dịch."""
        wrapper = ctk.CTkFrame(parent, fg_color=CLR_CARD,
                               corner_radius=14, border_width=1,
                               border_color=CLR_BORDER)
        wrapper.grid(row=2, column=0, sticky="nsew")
        wrapper.grid_rowconfigure(1, weight=1)
        wrapper.grid_columnconfigure(0, weight=1)

        # ── Thanh bộ lọc ─────────────────────────────────
        filter_row = ctk.CTkFrame(wrapper, fg_color="transparent")
        filter_row.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 6))
        filter_row.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(filter_row, text="📋  Lịch sử Giao dịch",
                     font=FONT_HEADING, text_color=CLR_TEXT).grid(
            row=0, column=0, sticky="w")

        filter_right = ctk.CTkFrame(filter_row, fg_color="transparent")
        filter_right.grid(row=0, column=1, sticky="e")

        # Ô tìm kiếm
        self.ent_search = ctk.CTkEntry(
            filter_right,
            placeholder_text="🔍  Tìm kiếm...",
            textvariable=self._search_keyword,
            font=FONT_BODY, width=180,
            fg_color=CLR_SIDEBAR, border_color=CLR_BORDER)
        self.ent_search.pack(side="left", padx=(0, 8))

        # Menu lọc loại
        self.opt_filter = ctk.CTkOptionMenu(
            filter_right,
            values=["Tất cả", "Thu nhập", "Chi tiêu"],
            variable=self._filter_type,
            command=lambda _: self.refresh_transaction_table(),
            font=FONT_BODY, width=120,
            fg_color=CLR_SIDEBAR, button_color=CLR_BLUE,
            dropdown_fg_color=CLR_SIDEBAR)
        self.opt_filter.pack(side="left")

        # ── Header cột ───────────────────────────────────
        COL_WIDTHS = [110, 60, 120, 130, 160, 120]
        COL_LABELS = ["Ngày", "Loại", "Danh mục", "Số tiền", "Ghi chú", "Hành động"]

        header = ctk.CTkFrame(wrapper, fg_color=CLR_BORDER, height=34,
                              corner_radius=0)
        header.grid(row=1, column=0, sticky="ew", padx=14)
        for i, (lbl, w) in enumerate(zip(COL_LABELS, COL_WIDTHS)):
            ctk.CTkLabel(header, text=lbl, font=("Segoe UI", 11, "bold"),
                         text_color=CLR_SUBTEXT, width=w,
                         anchor="center").pack(side="left", padx=2)

        # ── Vùng cuộn bảng ───────────────────────────────
        self.table_scroll = ctk.CTkScrollableFrame(
            wrapper, fg_color="transparent",
            scrollbar_button_color=CLR_BORDER)
        self.table_scroll.grid(row=2, column=0, sticky="nsew", padx=14, pady=(0, 12))
        wrapper.grid_rowconfigure(2, weight=1)

        # Lưu độ rộng cột để dùng khi vẽ hàng
        self._col_widths = COL_WIDTHS

    def refresh_transaction_table(self):
        """Xóa và vẽ lại toàn bộ bảng dựa trên bộ lọc hiện tại."""
        # Xóa tất cả widget hàng cũ
        for w in self.table_scroll.winfo_children():
            w.destroy()

        # Xác định bộ lọc
        keyword   = self._search_keyword.get().strip().lower() or None
        ftype_map = {"Thu nhập": "thu", "Chi tiêu": "chi", "Tất cả": None}
        ftype     = ftype_map.get(self._filter_type.get())

        # Lọc bằng hàm backend searchTransactions
        results = searchTransactions(
            self.transaction_list,
            keyword    = keyword,
            trans_type = ftype
        )

        if not results:
            ctk.CTkLabel(self.table_scroll,
                         text="Không có giao dịch nào phù hợp.",
                         font=FONT_BODY, text_color=CLR_SUBTEXT).pack(pady=20)
            return

        cw = self._col_widths
        for idx, t in enumerate(results):
            row_bg = CLR_ROW_ODD if idx % 2 == 0 else CLR_ROW_EVEN
            row = ctk.CTkFrame(self.table_scroll, fg_color=row_bg,
                               corner_radius=6, height=36)
            row.pack(fill="x", pady=1)

            is_thu   = (t.type == "thu")
            amt_sign = "+" if is_thu else "−"
            amt_clr  = CLR_GREEN if is_thu else CLR_RED
            type_txt = "THU" if is_thu else "CHI"

            # Ngày
            ctk.CTkLabel(row, text=t.date, font=FONT_SMALL,
                         text_color=CLR_TEXT, width=cw[0], anchor="center").pack(
                side="left", padx=2)
            # Loại
            ctk.CTkLabel(row, text=type_txt, font=("Segoe UI", 11, "bold"),
                         text_color=amt_clr, width=cw[1], anchor="center").pack(
                side="left", padx=2)
            # Danh mục
            ctk.CTkLabel(row, text=t.category, font=FONT_SMALL,
                         text_color=CLR_TEXT, width=cw[2], anchor="center").pack(
                side="left", padx=2)
            # Số tiền (màu theo loại)
            ctk.CTkLabel(row, text=f"{amt_sign}{t.amount:,.0f} ₫",
                         font=("Segoe UI", 11, "bold"),
                         text_color=amt_clr, width=cw[3], anchor="e").pack(
                side="left", padx=2)
            # Ghi chú (cắt nếu dài)
            note_txt = (t.note[:20] + "…") if len(t.note) > 20 else t.note
            ctk.CTkLabel(row, text=note_txt, font=FONT_SMALL,
                         text_color=CLR_SUBTEXT, width=cw[4], anchor="w").pack(
                side="left", padx=2)

            # Nút Sửa / Xóa — dùng default arg để capture đúng biến
            btn_row = ctk.CTkFrame(row, fg_color="transparent", width=cw[5])
            btn_row.pack(side="left", padx=4)

            ctk.CTkButton(btn_row, text="✏",  width=36, height=26,
                          font=FONT_SMALL, fg_color="#1d4ed8",
                          hover_color="#1e40af", corner_radius=6,
                          command=lambda tr=t: self.on_edit_click(tr)).pack(
                side="left", padx=2)
            ctk.CTkButton(btn_row, text="🗑",  width=36, height=26,
                          font=FONT_SMALL, fg_color="#be123c",
                          hover_color="#9f1239", corner_radius=6,
                          command=lambda tid=t.id: self.on_delete_click(tid)).pack(
                side="left", padx=2)

    # ──────────────────────────────────────────────────────────
    #  TIỆN ÍCH NỘI BỘ
    # ──────────────────────────────────────────────────────────

    def _clear_transaction_form(self):
        """Xóa sạch form nhập giao dịch sau khi thêm thành công."""
        self.ent_amount.delete(0, "end")
        self.ent_note.delete(0, "end")
        self.ent_date.delete(0, "end")
        self.ent_date.insert(0, datetime.today().strftime("%Y-%m-%d"))
        self.seg_type.set("Chi tiêu")
        self.opt_category.set(CATEGORIES[0])


# ══════════════════════════════════════════════════════════════
#  ĐIỂM KHỞI CHẠY
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = ExpenseApp()
    app.mainloop()