import tkinter as tk
from tkinter import ttk

from repositories.sales_repository import SaleRepository


class SalesHistoryFrame:
    def __init__(self, root, current_user, db):
        self.root = root
        self.current_user = current_user
        self.db = db
        self.sale_repo = SaleRepository(self.db)

        self.frame = tk.Frame(self.root, padx=20, pady=15)
        self.frame.pack(expand=True, fill="both")

        top_bar = tk.Frame(self.frame)
        top_bar.pack(fill="x")

        tk.Button(
            top_bar,
            text="← Back",
            width=8,
            command=self.back
        ).pack(side="left")

        tk.Button(
            top_bar,
            text="Logout",
            width=8,
            command=self.logout
        ).pack(side="left", padx=5)

        tk.Label(
            self.frame,
            text="Sales History",
            font=("Arial", 18, "bold")
        ).pack(pady=10)

        table_frame = tk.Frame(self.frame)
        table_frame.pack(expand=True, fill="both")

        columns = ("id", "customer", "prescription", "total", "date", "status")

        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        y_scroll = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.table.yview
        )

        x_scroll = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.table.xview
        )

        self.table.configure(
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )

        self.table.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        self.table.heading("id", text="Sale ID")
        self.table.heading("customer", text="Customer")
        self.table.heading("prescription", text="Prescription")
        self.table.heading("total", text="Total")
        self.table.heading("date", text="Date")
        self.table.heading("status", text="Status")

        self.table.column("id", width=70, anchor="center")
        self.table.column("customer", width=90, anchor="center")
        self.table.column("prescription", width=100, anchor="center")
        self.table.column("total", width=90, anchor="center")
        self.table.column("date", width=160, anchor="center")
        self.table.column("status", width=90, anchor="center")

        self.load_sales()

    def load_sales(self):
        for row in self.table.get_children():
            self.table.delete(row)

        sales = self.sale_repo.get_all()

        for sale in sales:
            self.table.insert(
                "",
                "end",
                values=(
                    sale.id,
                    sale.customer_id if sale.customer_id is not None else "Walk-in",
                    sale.prescription_id if sale.prescription_id is not None else "-",
                    f"{sale.total_amount:.2f} TL",
                    sale.sale_date,
                    "Completed" if sale.is_completed else "Pending"
                )
            )

    def back(self):
        self.frame.destroy()
        from gui.cashier_dashboard import CashierDashboard
        CashierDashboard(self.root, self.current_user, self.db)

    def logout(self):
        self.frame.destroy()
        from gui.login_window import LoginWindow
        LoginWindow(self.root, self.db)