import tkinter as tk
from tkinter import messagebox


class AdminDashboard:
    def __init__(self, root, user, db):
        self.root = root
        self.user = user
        self.db = db

        self.frame = tk.Frame(self.root)
        self.frame.pack(expand=True, fill="both")

        tk.Label(
            self.frame,
            text=f"Admin Dashboard - Welcome {user.full_name}",
            font=("Arial", 18, "bold")
        ).pack(pady=20)

        tk.Button(
            self.frame,
            text="Manage Users",
            width=25,
            command=self.open_users
        ).pack(pady=5)

        tk.Button(
            self.frame,
            text="Manage Medicines",
            width=25,
            command=self.open_medicines
        ).pack(pady=5)

        tk.Button(
            self.frame,
            text="Manage Categories",
            width=25,
            command=self.open_categories
        ).pack(pady=5)

        tk.Button(
            self.frame,
            text="Reports",
            width=25,
            command=self.open_reports
        ).pack(pady=5)

        tk.Button(
            self.frame,
            text="Logout",
            width=25,
            command=self.logout
        ).pack(pady=20)

    def open_users(self):
        self.frame.destroy()
        from gui.user_frame import UserFrame
        UserFrame(self.root, self.user, self.db)

    def open_medicines(self):
        self.frame.destroy()
        from gui.medicine_frame import MedicineFrame
        MedicineFrame(self.root, self.user, self.db)

    def open_categories(self):
        self.frame.destroy()
        from gui.category_frame import CategoryFrame
        CategoryFrame(self.root, self.user, self.db)

    def open_reports(self):
        self.frame.destroy()
        from gui.report_frame import ReportFrame
        ReportFrame(self.root, self.user, self.db)

    def logout(self):
        self.frame.destroy()
        from gui.login_window import LoginWindow
        LoginWindow(self.root, self.db)