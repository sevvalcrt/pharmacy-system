import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from prescription import Prescription
from prescription_item import PrescriptionItem

from repositories.prescription_repository import PrescriptionRepository
from repositories.medicine_repository import MedicineRepository


class PrescriptionFrame:
    def __init__(self, root, current_user, db):
        self.root = root
        self.current_user = current_user
        self.db = db

        self.prescription_repo = PrescriptionRepository(self.db)
        self.medicine_repo = MedicineRepository(self.db)

        self.frame = tk.Frame(self.root, padx=20, pady=15)
        self.frame.pack(expand=True, fill="both")

        top_bar = tk.Frame(self.frame)
        top_bar.pack(fill="x")

        tk.Button(top_bar, text="← Back", width=8, command=self.back).pack(side="left")
        tk.Button(top_bar, text="Logout", width=8, command=self.logout).pack(side="left", padx=5)

        tk.Label(
            self.frame,
            text="Manage Prescriptions",
            font=("Arial", 20, "bold")
        ).pack(pady=10)

        content = tk.Frame(self.frame)
        content.pack(expand=True, fill="both")

        left = tk.LabelFrame(content, text="Prescription Form", padx=15, pady=15)
        left.pack(side="left", fill="y", padx=(0, 15))

        right = tk.LabelFrame(content, text="Prescription List", padx=10, pady=10)
        right.pack(side="right", expand=True, fill="both")

        # CREATE PRESCRIPTION
        tk.Label(left, text="Customer ID").grid(row=0, column=0, sticky="w", pady=6)
        self.customer_id_entry = tk.Entry(left, width=25)
        self.customer_id_entry.grid(row=0, column=1, pady=6)

        tk.Label(left, text="Doctor Name").grid(row=1, column=0, sticky="w", pady=6)
        self.doctor_entry = tk.Entry(left, width=25)
        self.doctor_entry.grid(row=1, column=1, pady=6)

        tk.Button(
            left,
            text="Create Prescription",
            width=22,
            command=self.create_prescription
        ).grid(row=2, column=0, columnspan=2, pady=10)

        ttk.Separator(left, orient="horizontal").grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=10
        )

        # ADD MEDICINE TO PRESCRIPTION
        tk.Label(left, text="Prescription").grid(row=4, column=0, sticky="w", pady=6)
        self.prescription_combo = ttk.Combobox(left, state="readonly", width=28)
        self.prescription_combo.grid(row=4, column=1, pady=6)

        tk.Label(left, text="Medicine").grid(row=5, column=0, sticky="w", pady=6)
        self.medicine_combo = ttk.Combobox(left, state="readonly", width=28)
        self.medicine_combo.grid(row=5, column=1, pady=6)

        tk.Label(left, text="Quantity").grid(row=6, column=0, sticky="w", pady=6)
        self.quantity_entry = tk.Entry(left, width=31)
        self.quantity_entry.grid(row=6, column=1, pady=6)

        tk.Button(
            left,
            text="Add Medicine",
            width=22,
            command=self.add_item_to_prescription
        ).grid(row=7, column=0, columnspan=2, pady=10)

        tk.Button(
            left,
            text="Delete Selected Prescription",
            width=22,
            command=self.delete_selected_prescription
        ).grid(row=8, column=0, columnspan=2, pady=5)

        # PRESCRIPTION TABLE WITH SCROLL
        columns = ("id", "customer", "doctor", "date", "count")

        prescription_table_frame = tk.Frame(right)
        prescription_table_frame.pack(fill="x", pady=5)

        self.table = ttk.Treeview(
            prescription_table_frame,
            columns=columns,
            show="headings",
            height=8
        )

        y_scroll_pre = ttk.Scrollbar(
            prescription_table_frame,
            orient="vertical",
            command=self.table.yview
        )

        x_scroll_pre = ttk.Scrollbar(
            prescription_table_frame,
            orient="horizontal",
            command=self.table.xview
        )

        self.table.configure(
            yscrollcommand=y_scroll_pre.set,
            xscrollcommand=x_scroll_pre.set
        )

        self.table.grid(row=0, column=0, sticky="nsew")
        y_scroll_pre.grid(row=0, column=1, sticky="ns")
        x_scroll_pre.grid(row=1, column=0, sticky="ew")

        prescription_table_frame.rowconfigure(0, weight=1)
        prescription_table_frame.columnconfigure(0, weight=1)

        self.table.heading("id", text="ID")
        self.table.heading("customer", text="Customer")
        self.table.heading("doctor", text="Doctor")
        self.table.heading("date", text="Date")
        self.table.heading("count", text="Medicine Count")

        self.table.column("id", width=40, anchor="center")
        self.table.column("customer", width=80, anchor="center")
        self.table.column("doctor", width=120)
        self.table.column("date", width=150, anchor="center")
        self.table.column("count", width=100, anchor="center")

        self.table.bind("<<TreeviewSelect>>", self.select_prescription_from_table)

        # ITEM TABLE WITH SCROLL
        item_frame = tk.LabelFrame(right, text="Prescription Items", padx=10, pady=10)
        item_frame.pack(expand=True, fill="both", pady=10)

        item_table_frame = tk.Frame(item_frame)
        item_table_frame.pack(expand=True, fill="both")

        item_columns = ("item_id", "prescription_id", "medicine_id", "quantity")

        self.item_table = ttk.Treeview(
            item_table_frame,
            columns=item_columns,
            show="headings"
        )

        y_scroll_item = ttk.Scrollbar(
            item_table_frame,
            orient="vertical",
            command=self.item_table.yview
        )

        x_scroll_item = ttk.Scrollbar(
            item_table_frame,
            orient="horizontal",
            command=self.item_table.xview
        )

        self.item_table.configure(
            yscrollcommand=y_scroll_item.set,
            xscrollcommand=x_scroll_item.set
        )

        self.item_table.grid(row=0, column=0, sticky="nsew")
        y_scroll_item.grid(row=0, column=1, sticky="ns")
        x_scroll_item.grid(row=1, column=0, sticky="ew")

        item_table_frame.rowconfigure(0, weight=1)
        item_table_frame.columnconfigure(0, weight=1)

        self.item_table.heading("item_id", text="Item ID")
        self.item_table.heading("prescription_id", text="Prescription ID")
        self.item_table.heading("medicine_id", text="Medicine ID")
        self.item_table.heading("quantity", text="Quantity")

        self.item_table.column("item_id", width=70, anchor="center")
        self.item_table.column("prescription_id", width=110, anchor="center")
        self.item_table.column("medicine_id", width=100, anchor="center")
        self.item_table.column("quantity", width=80, anchor="center")

        self.load_prescriptions()
        self.load_medicines()

    def load_prescription_combo(self):
        prescriptions = self.prescription_repo.get_all()

        self.prescription_map = {
            f"ID:{p.id} | Customer:{p.customer_id} | {p.doctor_name}": p.id
            for p in prescriptions
        }

        self.prescription_combo["values"] = list(self.prescription_map.keys())

        if self.prescription_map:
            self.prescription_combo.current(0)

    def load_medicines(self):
        medicines = self.medicine_repo.get_all()

        self.medicine_map = {
            f"{m.name} (ID:{m.id})": m.id
            for m in medicines
        }

        self.medicine_combo["values"] = list(self.medicine_map.keys())

        if self.medicine_map:
            self.medicine_combo.current(0)

    def create_prescription(self):
        try:
            customer_id = int(self.customer_id_entry.get())
            doctor_name = self.doctor_entry.get()

            prescription = Prescription(None, customer_id, doctor_name)
            self.prescription_repo.add(prescription)

            messagebox.showinfo("Success", "Prescription created.")

            self.customer_id_entry.delete(0, tk.END)
            self.doctor_entry.delete(0, tk.END)

            self.load_prescriptions()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_item_to_prescription(self):
        try:
            selected_prescription = self.prescription_combo.get()
            selected_medicine = self.medicine_combo.get()

            if not selected_prescription:
                messagebox.showerror("Error", "Select a prescription.")
                return

            if not selected_medicine:
                messagebox.showerror("Error", "Select a medicine.")
                return

            prescription_id = self.prescription_map[selected_prescription]
            medicine_id = self.medicine_map[selected_medicine]
            quantity = int(self.quantity_entry.get())

            prescription = self.prescription_repo.get_by_id(prescription_id)

            if prescription is None:
                messagebox.showerror("Error", "Prescription not found.")
                return

            item = PrescriptionItem(None, prescription_id, medicine_id, quantity)
            prescription.add_item(item)

            self.prescription_repo.update(prescription_id, prescription)

            messagebox.showinfo("Success", "Medicine added to prescription.")

            self.quantity_entry.delete(0, tk.END)
            self.load_prescriptions()
            self.load_items(prescription_id)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_prescriptions(self):
        for row in self.table.get_children():
            self.table.delete(row)

        prescriptions = self.prescription_repo.get_all()

        for p in prescriptions:
            self.table.insert(
                "",
                "end",
                values=(
                    p.id,
                    p.customer_id,
                    p.doctor_name,
                    p.created_at,
                    p.total_medicines()
                )
            )

        self.load_prescription_combo()

    def load_items(self, prescription_id):
        for row in self.item_table.get_children():
            self.item_table.delete(row)

        prescription = self.prescription_repo.get_by_id(prescription_id)

        if prescription is None:
            return

        for item in prescription.items:
            self.item_table.insert(
                "",
                "end",
                values=(
                    item.id,
                    item.prescription_id,
                    item.medicine_id,
                    item.quantity
                )
            )

    def select_prescription_from_table(self, event=None):
        selected = self.table.selection()

        if not selected:
            return

        values = self.table.item(selected[0], "values")
        prescription_id = int(values[0])

        for text, pid in self.prescription_map.items():
            if pid == prescription_id:
                self.prescription_combo.set(text)
                break

        self.load_items(prescription_id)

    def delete_selected_prescription(self):
        selected = self.table.selection()

        if not selected:
            messagebox.showwarning("Warning", "Select a prescription.")
            return

        prescription_id = int(self.table.item(selected[0], "values")[0])

        confirm = messagebox.askyesno("Confirm", "Delete this prescription?")
        if not confirm:
            return

        try:
            self.prescription_repo.remove_by_id(prescription_id)
            messagebox.showinfo("Success", "Prescription deleted.")
            self.load_prescriptions()

            for row in self.item_table.get_children():
                self.item_table.delete(row)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def back(self):
        self.frame.destroy()
        from gui.pharmacist_dashboard import PharmacistDashboard
        PharmacistDashboard(self.root, self.current_user, self.db)

    def logout(self):
        self.frame.destroy()
        from gui.login_window import LoginWindow
        LoginWindow(self.root, self.db)