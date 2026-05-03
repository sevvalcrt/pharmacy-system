import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime

from services.report_service import ReportService


class ReportFrame:
    def __init__(self, root, current_user, db):
        self.root = root
        self.current_user = current_user
        self.db = db
        self.report_service = ReportService(self.db)

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
            text="Reports",
            font=("Arial", 20, "bold")
        ).pack(pady=15)

        form = tk.LabelFrame(self.frame, text="Report Filters", padx=15, pady=15)
        form.pack(fill="x", pady=10)

        tk.Label(form, text="Date").grid(row=0, column=0, padx=5, pady=5)
        self.date_entry = tk.Entry(form, width=20)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        tk.Label(form, text="Month").grid(row=0, column=2, padx=5, pady=5)
        self.month_entry = tk.Entry(form, width=20)
        self.month_entry.grid(row=0, column=3, padx=5, pady=5)
        self.month_entry.insert(0, datetime.now().strftime("%Y-%m"))

        tk.Button(
            form,
            text="Show Reports",
            width=18,
            command=self.load_reports
        ).grid(row=0, column=4, padx=10)

        result = tk.LabelFrame(self.frame, text="Summary", padx=15, pady=15)
        result.pack(fill="x", pady=10)

        self.daily_sales_label = tk.Label(result, text="Daily Total Sales: -", font=("Arial", 11))
        self.daily_sales_label.pack(anchor="w", pady=3)

        self.monthly_sales_label = tk.Label(result, text="Monthly Total Sales: -", font=("Arial", 11))
        self.monthly_sales_label.pack(anchor="w", pady=3)

        self.sales_count_label = tk.Label(result, text="Sales Count: -", font=("Arial", 11))
        self.sales_count_label.pack(anchor="w", pady=3)

        table_frame = tk.LabelFrame(self.frame, text="Top Selling Medicines", padx=10, pady=10)
        table_frame.pack(expand=True, fill="both", pady=10)

        columns = ("medicine", "quantity")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)

        self.table.heading("medicine", text="Medicine")
        self.table.heading("quantity", text="Total Quantity")

        self.table.column("medicine", width=250)
        self.table.column("quantity", width=120, anchor="center")

        self.table.pack(expand=True, fill="both")

        self.load_reports()

    def load_reports(self):
        try:
            date_prefix = self.date_entry.get().strip()
            month_prefix = self.month_entry.get().strip()

            daily_total = self.report_service.get_daily_total_sales(date_prefix)
            monthly_total = self.report_service.get_monthly_total_sales(month_prefix)
            sales_count = self.report_service.get_sales_count_by_date(date_prefix)
            top_medicines = self.report_service.get_top_selling_medicines(5)

            self.daily_sales_label.config(
                text=f"Daily Total Sales: {daily_total:.2f} TL"
            )

            self.monthly_sales_label.config(
                text=f"Monthly Total Sales: {monthly_total:.2f} TL"
            )

            self.sales_count_label.config(
                text=f"Sales Count: {sales_count}"
            )

            for row in self.table.get_children():
                self.table.delete(row)

            for medicine_name, quantity in top_medicines:
                self.table.insert(
                    "",
                    "end",
                    values=(medicine_name, quantity)
                )

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def back(self):
        self.frame.destroy()
        from gui.admin_dashboard import AdminDashboard
        AdminDashboard(self.root, self.current_user, self.db)

    def logout(self):
        self.frame.destroy()
        from gui.login_window import LoginWindow
        LoginWindow(self.root, self.db)