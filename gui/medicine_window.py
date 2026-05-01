import tkinter as tk
from tkinter import messagebox, ttk

from database.connection import DatabaseManager
from repositories.medicine_repository import MedicineRepository
from repositories.sales_repository import SalesRepository
from services.pharmacy_service import PharmacyService


class MedicineWindow:
    def __init__(self, db_manager: DatabaseManager) -> None:
        self.db_manager = db_manager
        self.service = PharmacyService(
            MedicineRepository(db_manager), SalesRepository(db_manager)
        )
        self.repo = MedicineRepository(db_manager)

        self.window = tk.Toplevel()
        self.window.title("Ilac Yonetimi")
        self.window.geometry("700x400")

        form = tk.Frame(self.window)
        form.pack(pady=10)

        tk.Label(form, text="Ilac Adi").grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = tk.Entry(form, width=20)
        self.name_entry.grid(row=0, column=1, padx=5)

        tk.Label(form, text="Birim Fiyat").grid(row=0, column=2, padx=5)
        self.price_entry = tk.Entry(form, width=10)
        self.price_entry.grid(row=0, column=3, padx=5)

        tk.Label(form, text="Stok").grid(row=0, column=4, padx=5)
        self.stock_entry = tk.Entry(form, width=10)
        self.stock_entry.grid(row=0, column=5, padx=5)

        tk.Label(form, text="SKT (YYYY-MM-DD)").grid(row=1, column=0, padx=5, pady=5)
        self.expiry_entry = tk.Entry(form, width=20)
        self.expiry_entry.grid(row=1, column=1, padx=5)

        tk.Button(form, text="Ilac Ekle", command=self._add_medicine).grid(
            row=1, column=3, padx=5
        )
        tk.Button(form, text="Yenile", command=self._load_medicines).grid(
            row=1, column=4, padx=5
        )

        self.tree = ttk.Treeview(
            self.window,
            columns=("id", "name", "price", "stock", "expiry"),
            show="headings",
        )
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Ilac")
        self.tree.heading("price", text="Fiyat")
        self.tree.heading("stock", text="Stok")
        self.tree.heading("expiry", text="SKT")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self._load_medicines()

    def _add_medicine(self) -> None:
        try:
            name = self.name_entry.get().strip()
            price = float(self.price_entry.get().strip())
            stock = int(self.stock_entry.get().strip())
            expiry = self.expiry_entry.get().strip() or None
            if not name:
                raise ValueError("Ilac adi bos olamaz.")
            self.service.add_medicine(name, price, stock, expiry)
            self._clear_form()
            self._load_medicines()
            messagebox.showinfo("Basarili", "Ilac eklendi.")
        except ValueError as exc:
            messagebox.showerror("Hata", str(exc))

    def _load_medicines(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in self.repo.list_medicines():
            self.tree.insert("", tk.END, values=row)

    def _clear_form(self) -> None:
        self.name_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.stock_entry.delete(0, tk.END)
        self.expiry_entry.delete(0, tk.END)
