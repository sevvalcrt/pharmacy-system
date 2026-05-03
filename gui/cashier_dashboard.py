import tkinter as tk


class CashierDashboard:
    def __init__(self, root, user, db):
        self.root = root
        self.user = user
        self.db = db

        self.frame = tk.Frame(self.root)
        self.frame.pack(expand=True, fill="both")

        tk.Label(
            self.frame,
            text=f"Cashier Dashboard - Welcome {user.full_name}",
            font=("Arial", 18, "bold")
        ).pack(pady=20)

        tk.Button(
            self.frame,
            text="New Sale",
            width=25,
            command=self.open_sale
        ).pack(pady=5)

        tk.Button(
            self.frame,
            text="Sales History",
            width=25,
            command=self.open_sales_history
        ).pack(pady=5)

        tk.Button(
            self.frame,
            text="Logout",
            width=25,
            command=self.logout
        ).pack(pady=20)

    def open_sale(self):
        self.frame.destroy()
        from gui.sale_frame import SaleFrame
        SaleFrame(self.root, self.user, self.db)

    def open_sales_history(self):
        self.frame.destroy()
        from gui.sales_history_frame import SalesHistoryFrame
        SalesHistoryFrame(self.root, self.user, self.db)

    def logout(self):
        self.frame.destroy()
        from gui.login_window import LoginWindow
        LoginWindow(self.root, self.db)