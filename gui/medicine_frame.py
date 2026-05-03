import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from medicine import Medicine
from repositories.medicine_repository import MedicineRepository


class MedicineFrame:
    def __init__(self, root, current_user, db):
        self.root = root
        self.current_user = current_user
        self.db = db
        self.repo = MedicineRepository(self.db)

        self.frame = tk.Frame(self.root, padx=20, pady=15)
        self.frame.pack(expand=True, fill="both")

        top_bar = tk.Frame(self.frame)
        top_bar.pack(fill="x")

        tk.Button(top_bar, text="← Back", width=8, command=self.back).pack(side="left")
        tk.Button(top_bar, text="Logout", width=8, command=self.logout).pack(side="left", padx=5)

        tk.Label(
            self.frame,
            text="Manage Medicines",
            font=("Arial", 20, "bold")
        ).pack(pady=10)

        content = tk.Frame(self.frame)
        content.pack(expand=True, fill="both")

        left = tk.LabelFrame(content, text="Medicine Form", padx=15, pady=15)
        left.pack(side="left", fill="y", padx=(0, 15))

        right = tk.LabelFrame(content, text="Medicine List", padx=10, pady=10)
        right.pack(side="right", expand=True, fill="both")

        tk.Label(left, text="Name").grid(row=0, column=0, sticky="w", pady=6)
        self.name = tk.Entry(left, width=25)
        self.name.grid(row=0, column=1, pady=6)

        tk.Label(left, text="Category ID").grid(row=1, column=0, sticky="w", pady=6)
        self.category = tk.Entry(left, width=25)
        self.category.grid(row=1, column=1, pady=6)

        tk.Label(left, text="Price").grid(row=2, column=0, sticky="w", pady=6)
        self.price = tk.Entry(left, width=25)
        self.price.grid(row=2, column=1, pady=6)

        tk.Label(left, text="Stock").grid(row=3, column=0, sticky="w", pady=6)
        self.stock = tk.Entry(left, width=25)
        self.stock.grid(row=3, column=1, pady=6)

        tk.Label(left, text="Expiry Date").grid(row=4, column=0, sticky="w", pady=6)
        self.expiry = tk.Entry(left, width=25)
        self.expiry.grid(row=4, column=1, pady=6)
        self.expiry.insert(0, "YYYY-MM-DD")

        self.prescription_var = tk.BooleanVar()
        tk.Checkbutton(
            left,
            text="Requires Prescription",
            variable=self.prescription_var
        ).grid(row=5, column=0, columnspan=2, sticky="w", pady=8)

        tk.Button(
            left,
            text="Add / Update Medicine",
            width=22,
            command=self.add_medicine
        ).grid(row=6, column=0, columnspan=2, pady=10)

        tk.Button(
            left,
            text="Delete Selected",
            width=22,
            command=self.delete_selected
        ).grid(row=7, column=0, columnspan=2, pady=5)

        table_frame = tk.Frame(right)
        table_frame.pack(expand=True, fill="both")

        columns = ("id", "name", "price", "stock", "expiry", "rx", "status")

        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        x_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.table.xview)

        self.table.configure(
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )

        self.table.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        self.table.heading("id", text="ID")
        self.table.heading("name", text="Name")
        self.table.heading("price", text="Price")
        self.table.heading("stock", text="Stock")
        self.table.heading("expiry", text="Expiry")
        self.table.heading("rx", text="Rx")
        self.table.heading("status", text="Status")

        self.table.column("id", width=40, anchor="center")
        self.table.column("name", width=120)
        self.table.column("price", width=70, anchor="center")
        self.table.column("stock", width=60, anchor="center")
        self.table.column("expiry", width=100, anchor="center")
        self.table.column("rx", width=50, anchor="center")
        self.table.column("status", width=90, anchor="center")

        self.load_data()

    def add_medicine(self):
        try:
            name = self.name.get().strip()
            category_id = int(self.category.get())
            price = float(self.price.get())
            stock = int(self.stock.get())

            expiry = self.expiry.get().strip()
            if expiry == "YYYY-MM-DD":
                expiry = None

            requires_prescription = self.prescription_var.get()

            existing_medicine = None

            for medicine in self.repo.get_all():
                if medicine.name.lower() == name.lower():
                    existing_medicine = medicine
                    break

            if existing_medicine:
                existing_medicine.stock += stock
                existing_medicine.unit_price = price
                existing_medicine.category_id = category_id
                existing_medicine.expiry_date = expiry
                existing_medicine.requires_prescription = requires_prescription

                self.repo.update(existing_medicine.id, existing_medicine)

                messagebox.showinfo(
                    "Updated",
                    "Medicine already exists. Stock and details updated."
                )
            else:
                med = Medicine(
                    None,
                    name,
                    category_id,
                    price,
                    stock,
                    expiry,
                    requires_prescription
                )

                self.repo.add(med)

                messagebox.showinfo("Success", "Medicine added.")

            self.clear_inputs()
            self.load_data()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_data(self):
        for row in self.table.get_children():
            self.table.delete(row)

        for m in self.repo.get_all():
            self.table.insert(
                "",
                "end",
                values=(
                    m.id,
                    m.name,
                    f"{m.unit_price:.2f}",
                    m.stock,
                    m.expiry_date if m.expiry_date else "-",
                    "Yes" if m.requires_prescription else "No",
                    m.get_status()
                )
            )

    def delete_selected(self):
        selected = self.table.selection()

        if not selected:
            messagebox.showwarning("Warning", "Select a medicine.")
            return

        med_id = int(self.table.item(selected[0], "values")[0])

        confirm = messagebox.askyesno("Confirm", "Delete this medicine?")
        if not confirm:
            return

        try:
            self.repo.remove_by_id(med_id)
            messagebox.showinfo("Success", "Medicine deleted.")
            self.load_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_inputs(self):
        self.name.delete(0, tk.END)
        self.category.delete(0, tk.END)
        self.price.delete(0, tk.END)
        self.stock.delete(0, tk.END)
        self.expiry.delete(0, tk.END)
        self.expiry.insert(0, "YYYY-MM-DD")
        self.prescription_var.set(False)

    def back(self):
        self.frame.destroy()
        from gui.admin_dashboard import AdminDashboard
        AdminDashboard(self.root, self.current_user, self.db)

    def logout(self):
        self.frame.destroy()
        from gui.login_window import LoginWindow
        LoginWindow(self.root, self.db)