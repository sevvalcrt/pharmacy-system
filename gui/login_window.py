import tkinter as tk
from tkinter import messagebox

from database.connection import DatabaseManager
from gui.dashboard_window import DashboardWindow


class LoginWindow:
    def __init__(self, db_manager: DatabaseManager) -> None:
        self.db_manager = db_manager
        self.root = tk.Tk()
        self.root.title("Pharmacy System - Login")
        self.root.geometry("320x200")

        tk.Label(self.root, text="Username").pack(pady=(20, 5))
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()

        tk.Label(self.root, text="Password").pack(pady=(10, 5))
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()

        tk.Button(self.root, text="Login", command=self._login).pack(pady=20)

    def _login(self) -> None:
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM users WHERE username = ? AND password = ?",
                (username, password),
            )
            user = cursor.fetchone()

        if not user:
            messagebox.showerror("Hata", "Kullanici adi veya sifre hatali.")
            return

        self.root.destroy()
        DashboardWindow(self.db_manager).run()

    def run(self) -> None:
        self.root.mainloop()
