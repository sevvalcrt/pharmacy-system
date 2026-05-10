import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from customer import Customer
from repositories.customer_repository import CustomerRepository
from gui.navigation import go_to_login, go_to_pharmacist_dashboard


class CustomerFrame:
    def __init__(self, root, current_user, db):
        self.root = root
        self.current_user = current_user
        self.db = db
        self.repo = CustomerRepository(self.db)

        self.frame = tk.Frame(self.root, padx=20, pady=15)
        self.frame.pack(expand=True, fill="both")

        top_bar = tk.Frame(self.frame)
        top_bar.pack(fill="x")

        tk.Button(top_bar, text="← Back", width=8, command=self.back).pack(side="left")
        tk.Button(top_bar, text="Logout", width=8, command=self.logout).pack(side="left", padx=5)

        tk.Label(
            self.frame,
            text="Manage Customers",
            font=("Arial", 20, "bold")
        ).pack(pady=15)

        content = tk.Frame(self.frame)
        content.pack(expand=True, fill="both")

        left = tk.LabelFrame(content, text="Customer Form", padx=15, pady=15)
        left.pack(side="left", fill="y", padx=(0, 15))

        right = tk.LabelFrame(content, text="Customer List", padx=10, pady=10)
        right.pack(side="right", expand=True, fill="both")

        tk.Label(left, text="Full Name").grid(row=0, column=0, sticky="w", pady=6)
        self.name_entry = tk.Entry(left, width=25)
        self.name_entry.grid(row=0, column=1, pady=6)

        tk.Label(left, text="Phone").grid(row=1, column=0, sticky="w", pady=6)
        self.phone_entry = tk.Entry(left, width=25)
        self.phone_entry.grid(row=1, column=1, pady=6)

        tk.Button(
            left,
            text="Add Customer",
            width=22,
            command=self.add_customer
        ).grid(row=2, column=0, columnspan=2, pady=10)

        tk.Button(
            left,
            text="Delete Selected",
            width=22,
            command=self.delete_selected
        ).grid(row=3, column=0, columnspan=2, pady=5)

        columns = ("id", "name", "phone")
        self.table = ttk.Treeview(right, columns=columns, show="headings")

        self.table.heading("id", text="ID")
        self.table.heading("name", text="Full Name")
        self.table.heading("phone", text="Phone")

        self.table.column("id", width=50, anchor="center")
        self.table.column("name", width=180)
        self.table.column("phone", width=120, anchor="center")

        self.table.pack(expand=True, fill="both")

        self.load_data()

    def add_customer(self):
        try:
            full_name = self.name_entry.get()
            phone = self.phone_entry.get()

            customer = Customer(None, full_name, phone)
            self.repo.add(customer)

            messagebox.showinfo("Success", "Customer added.")
            self.clear_inputs()
            self.load_data()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_data(self):
        for row in self.table.get_children():
            self.table.delete(row)

        for customer in self.repo.get_all():
            self.table.insert(
                "",
                "end",
                values=(customer.id, customer.full_name, customer.phone)
            )

    def delete_selected(self):
        selected = self.table.selection()

        if not selected:
            messagebox.showwarning("Warning", "Select a customer.")
            return

        customer_id = int(self.table.item(selected[0], "values")[0])

        confirm = messagebox.askyesno("Confirm", "Delete this customer?")
        if not confirm:
            return

        try:
            self.repo.remove_by_id(customer_id)
            messagebox.showinfo("Success", "Customer deleted.")
            self.load_data()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_inputs(self):
        self.name_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)

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