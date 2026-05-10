import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from services.prescription_service import PrescriptionService
from gui.navigation import go_to_login, go_to_pharmacist_dashboard


class PrescriptionFrame:
    def __init__(self, root, current_user, db):
        self.root = root
        self.current_user = current_user
        self.db = db

        self.service = PrescriptionService(self.db)

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

        tk.Label(left, text="Customer").grid(row=0, column=0, sticky="w", pady=6)
        self.customer_combo = ttk.Combobox(left, state="readonly", width=28)
        self.customer_combo.grid(row=0, column=1, pady=6)

        tk.Label(left, text="Doctor Name").grid(row=1, column=0, sticky="w", pady=6)
        self.doctor_entry = tk.Entry(left, width=31)
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
        self.table.column("customer", width=150)
        self.table.column("doctor", width=120)
        self.table.column("date", width=150, anchor="center")
        self.table.column("count", width=100, anchor="center")

        self.table.bind("<<TreeviewSelect>>", self.select_prescription_from_table)

        item_frame = tk.LabelFrame(right, text="Prescription Items", padx=10, pady=10)
        item_frame.pack(expand=True, fill="both", pady=10)

        item_table_frame = tk.Frame(item_frame)
        item_table_frame.pack(expand=True, fill="both")

        item_columns = ("item_id", "prescription_id", "medicine", "quantity")

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
        self.item_table.heading("medicine", text="Medicine")
        self.item_table.heading("quantity", text="Quantity")

        self.item_table.column("item_id", width=70, anchor="center")
        self.item_table.column("prescription_id", width=110, anchor="center")
        self.item_table.column("medicine", width=160)
        self.item_table.column("quantity", width=80, anchor="center")

        self.load_customers()
        self.load_medicines()
        self.load_prescriptions()

    def load_customers(self):
        customers = self.service.get_customers()

        self.customer_map = {
            f"{c.full_name} (ID:{c.id})": c.id
            for c in customers
        }

        self.customer_combo["values"] = list(self.customer_map.keys())

        if self.customer_map:
            self.customer_combo.current(0)

    def get_customer_name_by_id(self, customer_id):
        for text, cid in self.customer_map.items():
            if cid == customer_id:
                return text.split(" (ID:")[0]

        return f"Customer {customer_id}"

    def load_prescription_combo(self):
        prescriptions = self.service.get_prescriptions()

        self.prescription_map = {
            f"{self.get_customer_name_by_id(p.customer_id)} | {p.doctor_name}": p.id
            for p in prescriptions
        }

        self.prescription_combo["values"] = list(self.prescription_map.keys())

        if self.prescription_map:
            self.prescription_combo.current(0)

    def load_medicines(self):
        medicines = self.service.get_medicines()

        self.medicine_map = {
            m.name: m.id
            for m in medicines
        }

        self.medicine_name_map = {
            m.id: m.name
            for m in medicines
        }

        self.medicine_combo["values"] = list(self.medicine_map.keys())

        if self.medicine_map:
            self.medicine_combo.current(0)

    def create_prescription(self):
        try:
            selected_customer = self.customer_combo.get()

            if not selected_customer:
                messagebox.showerror("Error", "Select a customer.")
                return

            customer_id = self.customer_map[selected_customer]
            doctor_name = self.doctor_entry.get()

            self.service.create_prescription(customer_id, doctor_name)

            messagebox.showinfo("Success", "Prescription created.")

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

            self.service.add_medicine_to_prescription(
                prescription_id,
                medicine_id,
                quantity
            )

            messagebox.showinfo("Success", "Medicine added to prescription.")

            self.quantity_entry.delete(0, tk.END)
            self.load_prescriptions()
            self.load_items(prescription_id)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_prescriptions(self):
        for row in self.table.get_children():
            self.table.delete(row)

        prescriptions = self.service.get_prescriptions()

        for p in prescriptions:
            self.table.insert(
                "",
                "end",
                values=(
                    p.id,
                    self.get_customer_name_by_id(p.customer_id),
                    p.doctor_name,
                    p.created_at,
                    p.total_medicines()
                )
            )

        self.load_prescription_combo()

    def load_items(self, prescription_id):
        for row in self.item_table.get_children():
            self.item_table.delete(row)

        prescription = self.service.get_prescription_by_id(prescription_id)

        if prescription is None:
            return

        for item in prescription.items:
            medicine_name = self.medicine_name_map.get(
                item.medicine_id,
                f"Medicine {item.medicine_id}"
            )

            self.item_table.insert(
                "",
                "end",
                values=(
                    item.id,
                    item.prescription_id,
                    medicine_name,
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
            self.service.delete_prescription(prescription_id)

            messagebox.showinfo("Success", "Prescription deleted.")

            self.load_prescriptions()

            for row in self.item_table.get_children():
                self.item_table.delete(row)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def back(self):
        go_to_pharmacist_dashboard(
            self.root,
            self.current_user,
            self.db,
            self.frame
        )

    def logout(self):
        go_to_login(
            self.root,
            self.db,
            self.frame
        )