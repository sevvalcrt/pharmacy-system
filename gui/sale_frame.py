import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from repositories.medicine_repository import MedicineRepository
from repositories.sales_repository import SaleRepository
from repositories.prescription_repository import PrescriptionRepository
from repositories.payment_repository import PaymentRepository
from repositories.inventory_repository import InventoryRepository
from repositories.customer_repository import CustomerRepository

from services.sales_service import SalesService
from gui.navigation import go_to_login, go_to_cashier_dashboard


class SaleFrame:
    def __init__(self, root, user, db):
        self.root = root
        self.user = user
        self.db = db

        medicine_repo = MedicineRepository(self.db)
        sale_repo = SaleRepository(self.db)
        prescription_repo = PrescriptionRepository(self.db)
        payment_repo = PaymentRepository(self.db)
        inventory_repo = InventoryRepository(self.db)

        self.customer_repo = CustomerRepository(self.db)

        self.sales_service = SalesService(
            medicine_repo,
            sale_repo,
            prescription_repo,
            payment_repo,
            inventory_repo
        )

        self.cart = []
        self.prescription_map = {}
        self.medicine_map = {}

        self.frame = tk.Frame(self.root, padx=10, pady=8)
        self.frame.pack(expand=True, fill="both")

        self.create_top_bar()
        self.create_form()
        self.create_table()
        self.create_payment_area()

        self.load_prescriptions()
        self.load_medicines()

    def create_top_bar(self):
        top = tk.Frame(self.frame)
        top.pack(fill="x")

        tk.Button(top, text="← Back", width=8, command=self.back).pack(side="left")
        tk.Button(top, text="Logout", width=8, command=self.logout).pack(side="left", padx=5)

        tk.Label(
            self.frame,
            text="New Sale",
            font=("Arial", 16, "bold")
        ).pack(pady=5)

    def create_form(self):
        form = tk.LabelFrame(self.frame, text="Sale Form", padx=8, pady=6)
        form.pack(fill="x", pady=5)

        tk.Label(form, text="Prescription").grid(row=0, column=0, sticky="w", pady=3)
        self.prescription_combo = ttk.Combobox(form, state="readonly", width=45)
        self.prescription_combo.grid(row=0, column=1, pady=3)
        self.prescription_combo.bind("<<ComboboxSelected>>", self.prescription_changed)

        tk.Label(form, text="Medicine").grid(row=1, column=0, sticky="w", pady=3)
        self.medicine_combo = ttk.Combobox(form, state="readonly", width=45)
        self.medicine_combo.grid(row=1, column=1, pady=3)

        tk.Label(form, text="Quantity").grid(row=2, column=0, sticky="w", pady=3)
        self.qty_entry = tk.Entry(form, width=48)
        self.qty_entry.grid(row=2, column=1, pady=3)

        tk.Button(
            form,
            text="Add to Sale",
            width=18,
            command=self.add_item
        ).grid(row=3, column=0, columnspan=2, pady=6)

        prescription_items_frame = tk.LabelFrame(
            form,
            text="Selected Prescription Items",
            padx=8,
            pady=6
        )
        prescription_items_frame.grid(row=0, column=2, rowspan=4, padx=15, sticky="n")

        columns = ("medicine", "quantity")

        self.prescription_items_table = ttk.Treeview(
            prescription_items_frame,
            columns=columns,
            show="headings",
            height=5
        )

        self.prescription_items_table.heading("medicine", text="Medicine")
        self.prescription_items_table.heading("quantity", text="Allowed Qty")

        self.prescription_items_table.column("medicine", width=170)
        self.prescription_items_table.column("quantity", width=90, anchor="center")

        self.prescription_items_table.pack()

    def create_table(self):
        table_frame = tk.LabelFrame(self.frame, text="Sale Items", padx=8, pady=6)
        table_frame.pack(fill="both", expand=True, pady=5)

        columns = ("medicine", "qty", "unit_price", "subtotal", "rx")

        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=6
        )

        self.table.heading("medicine", text="Medicine")
        self.table.heading("qty", text="Qty")
        self.table.heading("unit_price", text="Unit Price")
        self.table.heading("subtotal", text="Subtotal")
        self.table.heading("rx", text="Rx")

        self.table.column("medicine", width=150)
        self.table.column("qty", width=50, anchor="center")
        self.table.column("unit_price", width=80, anchor="center")
        self.table.column("subtotal", width=80, anchor="center")
        self.table.column("rx", width=50, anchor="center")

        self.table.pack(fill="both", expand=True)

        self.total_label = tk.Label(
            self.frame,
            text="Total: 0.00 TL",
            font=("Arial", 11, "bold")
        )
        self.total_label.pack(pady=4)

    def create_payment_area(self):
        payment_frame = tk.LabelFrame(self.frame, text="Payment", padx=8, pady=6)
        payment_frame.pack(fill="x", pady=4)

        tk.Label(payment_frame, text="Method").grid(row=0, column=0, padx=4)

        self.method_combo = ttk.Combobox(
            payment_frame,
            values=["CASH", "CARD", "TRANSFER"],
            state="readonly",
            width=12
        )
        self.method_combo.grid(row=0, column=1, padx=4)
        self.method_combo.current(0)
        self.method_combo.bind("<<ComboboxSelected>>", self.payment_method_changed)

        tk.Label(payment_frame, text="Paid").grid(row=0, column=2, padx=4)

        self.paid_entry = tk.Entry(payment_frame, width=12)
        self.paid_entry.grid(row=0, column=3, padx=4)
        self.paid_entry.bind("<KeyRelease>", self.calculate_change)

        self.change_label = tk.Label(
            payment_frame,
            text="Change: 0.00 TL",
            font=("Arial", 10, "bold")
        )
        self.change_label.grid(row=0, column=4, padx=8)

        tk.Button(
            payment_frame,
            text="Complete Sale",
            width=15,
            command=self.complete_sale
        ).grid(row=0, column=5, padx=6)

    def load_prescriptions(self):
        prescriptions = self.sales_service.get_all_prescriptions()
        self.prescription_map = {"No Prescription": None}

        for prescription in prescriptions:
            customer = self.customer_repo.get_by_id(prescription.customer_id)

            if customer is not None:
                customer_name = customer.full_name
            else:
                customer_name = f"Customer ID:{prescription.customer_id}"

            text = (
                f"ID:{prescription.id} | "
                f"{customer_name} | "
                f"Doctor: {prescription.doctor_name}"
            )

            self.prescription_map[text] = prescription.id

        self.prescription_combo["values"] = list(self.prescription_map.keys())
        self.prescription_combo.current(0)
        self.load_prescription_items(None)

    def prescription_changed(self, event=None):
        selected_prescription = self.prescription_combo.get()
        prescription_id = self.prescription_map.get(selected_prescription)

        self.load_prescription_items(prescription_id)

    def load_prescription_items(self, prescription_id):
        for row in self.prescription_items_table.get_children():
            self.prescription_items_table.delete(row)

        if prescription_id is None:
            return

        prescription = self.sales_service.get_prescription_by_id(prescription_id)

        if prescription is None:
            return

        for item in prescription.items:
            medicine = self.sales_service.medicine_repo.get_by_id(item.medicine_id)

            if medicine is not None:
                medicine_name = medicine.name
            else:
                medicine_name = f"Medicine ID:{item.medicine_id}"

            self.prescription_items_table.insert(
                "",
                "end",
                values=(medicine_name, item.quantity)
            )

    def load_medicines(self):
        medicines = self.sales_service.get_all_medicines()

        self.medicine_map = {
            f"{medicine.name} (ID:{medicine.id}) | "
            f"Rx:{'Yes' if medicine.requires_prescription else 'No'}": medicine
            for medicine in medicines
        }

        self.medicine_combo["values"] = list(self.medicine_map.keys())

        if self.medicine_map:
            self.medicine_combo.current(0)

    def add_item(self):
        try:
            selected_medicine = self.medicine_combo.get()
            selected_prescription = self.prescription_combo.get()

            if not selected_medicine:
                messagebox.showerror("Error", "Select a medicine.")
                return

            quantity = int(self.qty_entry.get())

            medicine = self.medicine_map[selected_medicine]
            prescription_id = self.prescription_map[selected_prescription]

            self.cart = self.sales_service.add_to_cart(
                self.cart,
                medicine,
                quantity,
                prescription_id
            )

            self.qty_entry.delete(0, tk.END)
            self.refresh_table()
            self.update_total()
            self.calculate_change()
            self.payment_method_changed()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh_table(self):
        for row in self.table.get_children():
            self.table.delete(row)

        for item in self.cart:
            medicine = item["medicine"]

            self.table.insert(
                "",
                "end",
                values=(
                    medicine.name,
                    item["quantity"],
                    f"{item['unit_price']:.2f}",
                    f"{item['subtotal']:.2f}",
                    "Yes" if medicine.requires_prescription else "No"
                )
            )

    def update_total(self):
        total = self.sales_service.get_total(self.cart)
        self.total_label.config(text=f"Total: {total:.2f} TL")

    def payment_method_changed(self, event=None):
        method = self.method_combo.get()
        total = self.sales_service.get_total(self.cart)

        if method in ("CARD", "TRANSFER"):
            self.paid_entry.config(state="normal")
            self.paid_entry.delete(0, tk.END)
            self.paid_entry.insert(0, f"{total:.2f}")
            self.paid_entry.config(state="disabled")
            self.change_label.config(text="Change: 0.00 TL")
        else:
            self.paid_entry.config(state="normal")
            self.change_label.config(text="Change: 0.00 TL")

    def calculate_change(self, event=None):
        method = self.method_combo.get()
        total = self.sales_service.get_total(self.cart)

        if method in ("CARD", "TRANSFER"):
            self.change_label.config(text="Change: 0.00 TL")
            return

        paid_text = self.paid_entry.get().strip()

        if not paid_text:
            self.change_label.config(text="Change: 0.00 TL")
            return

        try:
            paid = float(paid_text)
            _, change = self.sales_service.validate_payment(total, paid, method)
            self.change_label.config(text=f"Change: {change:.2f} TL")

        except Exception:
            try:
                paid = float(paid_text)
                missing = total - paid

                if missing > 0:
                    self.change_label.config(text=f"Missing: {missing:.2f} TL")
                else:
                    self.change_label.config(text="Change: 0.00 TL")

            except Exception:
                self.change_label.config(text="Change: 0.00 TL")

    def complete_sale(self):
        try:
            if not self.cart:
                messagebox.showerror("Error", "Sale is empty.")
                return

            method = self.method_combo.get()
            total = self.sales_service.get_total(self.cart)

            if method == "CASH":
                paid_text = self.paid_entry.get().strip()

                if not paid_text:
                    messagebox.showerror("Error", "Enter paid amount.")
                    return

                paid = float(paid_text)
            else:
                paid = total

            invoice = self.sales_service.complete_sale(
                cart=self.cart,
                paid_amount=paid,
                method=method,
                cashier_name=self.user.full_name
            )

            messagebox.showinfo("Invoice", invoice.generate_text())

            self.back()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def back(self):
        go_to_cashier_dashboard(
            self.root,
            self.user,
            self.db,
            self.frame
        )

    def logout(self):
        go_to_login(
            self.root,
            self.db,
            self.frame
        )