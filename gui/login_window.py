import tkinter as tk
from tkinter import messagebox

from database.connection import DatabaseManager
from database.schema import initialize_schema
from repositories.user_repository import UserRepository

from gui.admin_dashboard import AdminDashboard
from gui.pharmacist_dashboard import PharmacistDashboard
from gui.cashier_dashboard import CashierDashboard


class LoginWindow:
    def __init__(self, root, db=None):
        self.root = root

        self.db = db or DatabaseManager()
        initialize_schema(self.db)

        # Test customer eklenir.
        # Prescription oluştururken Customer ID = 1 kullanabilmen için.
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO customers(id, full_name, phone) VALUES (?, ?, ?)",
                (1, "Test Customer", "05551234567")
            )

        self.user_repo = UserRepository(self.db)

        self.frame = tk.Frame(self.root)
        self.frame.pack(expand=True)

        tk.Label(
            self.frame,
            text="Pharmacy Medicine System",
            font=("Arial", 20, "bold")
        ).pack(pady=20)

        tk.Label(self.frame, text="Username").pack()
        self.username_entry = tk.Entry(self.frame, width=30)
        self.username_entry.pack(pady=5)

        tk.Label(self.frame, text="Password").pack()
        self.password_entry = tk.Entry(self.frame, width=30, show="*")
        self.password_entry.pack(pady=5)

        tk.Button(
            self.frame,
            text="Login",
            width=20,
            command=self.login
        ).pack(pady=20)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        user = self.user_repo.login(username, password)

        if user is None:
            messagebox.showerror("Error", "Invalid username or password.")
            return

        self.frame.destroy()

        if user.role_id == 1:
            AdminDashboard(self.root, user, self.db)
        elif user.role_id == 2:
            PharmacistDashboard(self.root, user, self.db)
        elif user.role_id == 3:
            CashierDashboard(self.root, user, self.db)
        else:
            messagebox.showerror("Error", "Unknown role.")