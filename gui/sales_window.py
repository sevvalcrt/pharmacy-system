import tkinter as tk
from tkinter import messagebox, ttk

from database.connection import DatabaseManager
from repositories.medicine_repository import MedicineRepository
from repositories.sales_repository import SalesRepository
from services.pharmacy_service import PharmacyService


class SalesWindow:
    def __init__(self, db_manager: DatabaseManager) -> None:
        self.repo = MedicineRepository(db_manager)
        self.service = PharmacyService(self.repo, SalesRepository(db_manager))

        self.window = tk.Toplevel()
        self.window.title("Satis Ekrani")
        self.window.geometry("600x380")

        form = tk.Frame(self.window)
        form.pack(pady=10)

        tk.Label(form, text="Ilac ID").grid(row=0, column=0, padx=5)
        self.medicine_id_entry = tk.Entry(form, width=10)
        self.medicine_id_entry.grid(row=0, column=1, padx=5)

        tk.Label(form, text="Miktar").grid(row=0, column=2, padx=5)
        self.quantity_entry = tk.Entry(form, width=10)
        self.quantity_entry.grid(row=0, column=3, padx=5)

        tk.Button(form, text="Satis Yap", command=self._sell).grid(row=0, column=4, padx=10)
        tk.Button(form, text="Ilaclari Yenile", command=self._load_medicines).grid(
            row=0, column=5, padx=5
        )

        self.tree = ttk.Treeview(
            self.window, columns=("id", "name", "price", "stock", "expiry"), show="headings"
        )
        for key, title in [
            ("id", "ID"),
            ("name", "Ilac"),
            ("price", "Fiyat"),
            ("stock", "Stok"),
            ("expiry", "SKT"),
        ]:
            self.tree.heading(key, text=title)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self._load_medicines()

    def _sell(self) -> None:
        try:
            medicine_id = int(self.medicine_id_entry.get().strip())
            quantity = int(self.quantity_entry.get().strip())
            sale_id = self.service.sell_medicine(medicine_id, quantity)
            self._load_medicines()
            messagebox.showinfo("Basarili", f"Satis tamamlandi. Satis ID: {sale_id}")
        except ValueError as exc:
            messagebox.showerror("Hata", str(exc))

    def _load_medicines(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in self.repo.list_medicines():
            self.tree.insert("", tk.END, values=row)
