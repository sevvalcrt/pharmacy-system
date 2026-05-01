import tkinter as tk
from datetime import datetime
from tkinter import messagebox

from database.connection import DatabaseManager
from gui.medicine_window import MedicineWindow
from gui.sales_window import SalesWindow
from services.report_service import ReportService


class DashboardWindow:
    def __init__(self, db_manager: DatabaseManager) -> None:
        self.db_manager = db_manager
        self.report_service = ReportService(db_manager)
        self.root = tk.Tk()
        self.root.title("Pharmacy System - Dashboard")
        self.root.geometry("420x260")

        tk.Label(
            self.root,
            text="Pharmacy Medicine Sales System",
            font=("Arial", 14, "bold"),
        ).pack(pady=15)

        tk.Button(self.root, text="Ilac Yonetimi", width=25, command=self._open_medicine).pack(
            pady=5
        )
        tk.Button(self.root, text="Satis Ekrani", width=25, command=self._open_sales).pack(
            pady=5
        )
        tk.Button(self.root, text="Gunluk Ciro Goster", width=25, command=self._show_daily_total).pack(
            pady=5
        )
        tk.Button(self.root, text="Cikis", width=25, command=self.root.destroy).pack(pady=5)

    def _open_medicine(self) -> None:
        MedicineWindow(self.db_manager)

    def _open_sales(self) -> None:
        SalesWindow(self.db_manager)

    def _show_daily_total(self) -> None:
        today = datetime.now().strftime("%Y-%m-%d")
        total = self.report_service.get_daily_total_sales(today)
        messagebox.showinfo("Gunluk Ciro", f"{today} tarihi icin toplam: {total:.2f} TL")

    def run(self) -> None:
        self.root.mainloop()
