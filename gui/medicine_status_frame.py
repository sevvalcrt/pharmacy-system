import tkinter as tk
from tkinter import ttk

from repositories.medicine_repository import MedicineRepository


class MedicineStatusFrame:
    def __init__(self, root, current_user, db):
        self.root = root
        self.current_user = current_user
        self.db = db
        self.repo = MedicineRepository(self.db)

        self.frame = tk.Frame(self.root, padx=20, pady=15)
        self.frame.pack(expand=True, fill="both")

        # 🔹 TOP BAR
        top_bar = tk.Frame(self.frame)
        top_bar.pack(fill="x")

        tk.Button(top_bar, text="← Back", width=8, command=self.back).pack(side="left")
        tk.Button(top_bar, text="Logout", width=8, command=self.logout).pack(side="left", padx=5)

        # 🔹 TITLE
        tk.Label(
            self.frame,
            text="Medicine Status",
            font=("Arial", 20, "bold")
        ).pack(pady=10)

        # 🔹 TABLE FRAME
        table_frame = tk.Frame(self.frame)
        table_frame.pack(expand=True, fill="both")

        columns = ("id", "name", "stock", "expiry", "rx", "status")

        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        # 🔹 SCROLL
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

        # 🔹 HEADERS
        self.table.heading("id", text="ID")
        self.table.heading("name", text="Name")
        self.table.heading("stock", text="Stock")
        self.table.heading("expiry", text="Expiry")
        self.table.heading("rx", text="Rx")
        self.table.heading("status", text="Status")

        # 🔹 WIDTH
        self.table.column("id", width=40, anchor="center")
        self.table.column("name", width=140)
        self.table.column("stock", width=70, anchor="center")
        self.table.column("expiry", width=110, anchor="center")
        self.table.column("rx", width=50, anchor="center")
        self.table.column("status", width=100, anchor="center")

        self.load_data()

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
                    m.stock,
                    m.expiry_date if m.expiry_date else "-",
                    "Yes" if m.requires_prescription else "No",
                    m.get_status()
                )
            )

    def back(self):
        self.frame.destroy()
        from gui.pharmacist_dashboard import PharmacistDashboard
        PharmacistDashboard(self.root, self.current_user, self.db)

    def logout(self):
        self.frame.destroy()
        from gui.login_window import LoginWindow
        LoginWindow(self.root, self.db)