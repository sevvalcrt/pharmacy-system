import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from repositories.medicine_repository import MedicineRepository
from repositories.sales_repository import SaleRepository
from repositories.prescription_repository import PrescriptionRepository
from repositories.payment_repository import PaymentRepository

from sale import Sale
from sale_item import SaleItem
from payment import Payment


class SaleFrame:
    def __init__(self, root, user, db):
        self.root = root
        self.user = user
        self.db = db

        self.medicine_repo = MedicineRepository(self.db)
        self.sale_repo = SaleRepository(self.db)
        self.prescription_repo = PrescriptionRepository(self.db)
        self.payment_repo = PaymentRepository(self.db)

        self.cart = []

        self.frame = tk.Frame(self.root, padx=10, pady=8)
        self.frame.pack(expand=True, fill="both")

        top = tk.Frame(self.frame)
        top.pack(fill="x")

        tk.Button(top, text="← Back", width=8, command=self.back).pack(side="left")
        tk.Button(top, text="Logout", width=8, command=self.logout).pack(side="left", padx=5)

        tk.Label(self.frame, text="New Sale", font=("Arial", 16, "bold")).pack(pady=5)

        form = tk.LabelFrame(self.frame, text="Sale Form", padx=8, pady=6)
        form.pack(fill="x", pady=5)

        tk.Label(form, text="Prescription").grid(row=0, column=0, sticky="w", pady=3)
        self.prescription_combo = ttk.Combobox(form, state="readonly", width=42)
        self.prescription_combo.grid(row=0, column=1, pady=3)

        tk.Label(form, text="Medicine").grid(row=1, column=0, sticky="w", pady=3)
        self.medicine_combo = ttk.Combobox(form, state="readonly", width=42)
        self.medicine_combo.grid(row=1, column=1, pady=3)

        tk.Label(form, text="Quantity").grid(row=2, column=0, sticky="w", pady=3)
        self.qty_entry = tk.Entry(form, width=45)
        self.qty_entry.grid(row=2, column=1, pady=3)

        tk.Button(form, text="Add to Sale", width=18, command=self.add_item).grid(
            row=3, column=0, columnspan=2, pady=6
        )

        table_frame = tk.LabelFrame(self.frame, text="Sale Items", padx=8, pady=6)
        table_frame.pack(fill="both", expand=True, pady=5)

        columns = ("medicine", "qty", "unit_price", "subtotal", "rx")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings", height=6)

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

        self.load_prescriptions()
        self.load_medicines()

    def load_prescriptions(self):
        prescriptions = self.prescription_repo.get_all()
        self.prescription_map = {"No Prescription": None}

        for p in prescriptions:
            text = f"ID:{p.id} | Customer:{p.customer_id} | {p.doctor_name}"
            self.prescription_map[text] = p.id

        self.prescription_combo["values"] = list(self.prescription_map.keys())
        self.prescription_combo.current(0)

    def load_medicines(self):
        medicines = self.medicine_repo.get_all()

        self.medicine_map = {
            f"{m.name} (ID:{m.id}) | Rx:{'Yes' if m.requires_prescription else 'No'}": m
            for m in medicines
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

            if quantity <= 0:
                messagebox.showerror("Error", "Quantity must be greater than 0.")
                return

            medicine = self.medicine_map[selected_medicine]
            prescription_id = self.prescription_map[selected_prescription]

            if not medicine.is_available(quantity):
                messagebox.showerror("Error", "Medicine is expired or stock is insufficient.")
                return

            if medicine.requires_prescription:
                if prescription_id is None:
                    messagebox.showerror("Error", "This medicine requires a prescription.")
                    return

                prescription = self.prescription_repo.get_by_id(prescription_id)

                if prescription is None:
                    messagebox.showerror("Error", "Prescription not found.")
                    return

                if not prescription.has_medicine(medicine.id):
                    messagebox.showerror("Error", "This medicine is not in the selected prescription.")
                    return

                if not prescription.allows_quantity(medicine.id, quantity):
                    messagebox.showerror("Error", "Quantity exceeds prescription limit.")
                    return

            for cart_item in self.cart:
                if cart_item["medicine"].id == medicine.id:
                    new_quantity = cart_item["quantity"] + quantity

                    if not medicine.is_available(new_quantity):
                        messagebox.showerror("Error", "Total quantity exceeds stock.")
                        return

                    cart_item["quantity"] = new_quantity
                    cart_item["subtotal"] = medicine.unit_price * new_quantity

                    self.refresh_table()
                    self.qty_entry.delete(0, tk.END)
                    self.update_total()
                    self.calculate_change()
                    return

            subtotal = medicine.unit_price * quantity

            self.cart.append({
                "medicine": medicine,
                "quantity": quantity,
                "unit_price": medicine.unit_price,
                "subtotal": subtotal,
                "prescription_id": prescription_id
            })

            self.refresh_table()
            self.qty_entry.delete(0, tk.END)
            self.update_total()
            self.calculate_change()

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

    def get_total(self):
        return sum(item["subtotal"] for item in self.cart)

    def update_total(self):
        total = self.get_total()
        self.total_label.config(text=f"Total: {total:.2f} TL")

    def payment_method_changed(self, event=None):
        method = self.method_combo.get()

        if method in ("CARD", "TRANSFER"):
            total = self.get_total()
            self.paid_entry.config(state="normal")
            self.paid_entry.delete(0, tk.END)
            self.paid_entry.insert(0, f"{total:.2f}")
            self.paid_entry.config(state="disabled")
            self.change_label.config(text="Change: 0.00 TL")
        else:
            self.paid_entry.config(state="normal")
            self.paid_entry.delete(0, tk.END)
            self.change_label.config(text="Change: 0.00 TL")

    def calculate_change(self, event=None):
        method = self.method_combo.get()
        total = self.get_total()

        if method in ("CARD", "TRANSFER"):
            self.change_label.config(text="Change: 0.00 TL")
            return

        paid_text = self.paid_entry.get().strip()

        if not paid_text:
            self.change_label.config(text="Change: 0.00 TL")
            return

        try:
            paid = float(paid_text)

            temp_payment = Payment(
                None,
                1,
                paid,
                method
            )

            change = temp_payment.calculate_change(total)
            self.change_label.config(text=f"Change: {change:.2f} TL")

        except ValueError:
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

            total = self.get_total()
            method = self.method_combo.get()

            if method == "CASH":
                paid_text = self.paid_entry.get().strip()

                if not paid_text:
                    messagebox.showerror("Error", "Enter paid amount.")
                    return

                paid = float(paid_text)
            else:
                paid = total

            prescription_id = None

            for item in self.cart:
                if item["prescription_id"] is not None:
                    prescription_id = item["prescription_id"]
                    break

            sale = Sale(None, customer_id=None, prescription_id=prescription_id)
            self.sale_repo.add(sale)

            for item in self.cart:
                medicine = item["medicine"]

                sale_item = SaleItem(
                    None,
                    sale.id,
                    medicine.id,
                    item["quantity"],
                    item["unit_price"]
                )

                sale.add_item(sale_item)

                medicine.reduce_stock(item["quantity"])
                self.medicine_repo.update(medicine.id, medicine)

            sale.complete_sale()
            self.sale_repo.update(sale.id, sale)

            payment = Payment(None, sale.id, paid, method)
            change = payment.calculate_change(total)
            self.payment_repo.add(payment)

            messagebox.showinfo(
                "Success",
                f"Sale completed.\n"
                f"Payment saved to database.\n"
                f"Payment Method: {method}\n"
                f"Total: {total:.2f} TL\n"
                f"Paid: {paid:.2f} TL\n"
                f"Change: {change:.2f} TL"
            )

            self.frame.destroy()

            from gui.cashier_dashboard import CashierDashboard
            CashierDashboard(self.root, self.user, self.db)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def back(self):
        self.frame.destroy()

        from gui.cashier_dashboard import CashierDashboard
        CashierDashboard(self.root, self.user, self.db)

    def logout(self):
        self.frame.destroy()

        from gui.login_window import LoginWindow
        LoginWindow(self.root, self.db)