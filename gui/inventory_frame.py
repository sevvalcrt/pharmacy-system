import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from services.inventory_service import InventoryService
from gui.navigation import go_to_login, go_to_admin_dashboard


class InventoryFrame:
    def __init__(self, root, current_user, db):
        self.root = root
        self.current_user = current_user
        self.db = db
        self.service = InventoryService(self.db)

        self.frame = tk.Frame(self.root, padx=20, pady=15)
        self.frame.pack(expand=True, fill="both")

        top_bar = tk.Frame(self.frame)
        top_bar.pack(fill="x")

        tk.Button(top_bar, text="← Back", width=8, command=self.back).pack(side="left")
        tk.Button(top_bar, text="Logout", width=8, command=self.logout).pack(side="left", padx=5)

        tk.Label(
            self.frame,
            text="Inventory Movements",
            font=("Arial", 20, "bold")
        ).pack(pady=10)

        content = tk.Frame(self.frame)
        content.pack(expand=True, fill="both")

        left = tk.LabelFrame(content, text="Inventory Form", padx=15, pady=15)
        left.pack(side="left", fill="y", padx=(0, 15))

        right = tk.LabelFrame(content, text="Inventory List", padx=10, pady=10)
        right.pack(side="right", expand=True, fill="both")

        tk.Label(left, text="Medicine ID").grid(row=0, column=0, sticky="w", pady=6)
        self.medicine_id_entry = tk.Entry(left, width=25)
        self.medicine_id_entry.grid(row=0, column=1, pady=6)

        tk.Label(left, text="Quantity Change").grid(row=1, column=0, sticky="w", pady=6)
        self.quantity_entry = tk.Entry(left, width=25)
        self.quantity_entry.grid(row=1, column=1, pady=6)

        tk.Label(left, text="Action Type").grid(row=2, column=0, sticky="w", pady=6)
        self.action_combo = ttk.Combobox(
            left,
            values=["IN", "OUT", "RETURN", "ADJUST"],
            state="readonly",
            width=22
        )
        self.action_combo.grid(row=2, column=1, pady=6)
        self.action_combo.current(0)

        tk.Button(
            left,
            text="Add Movement",
            width=22,
            command=self.add_movement
        ).grid(row=3, column=0, columnspan=2, pady=10)

        tk.Button(
            left,
            text="Delete Selected",
            width=22,
            command=self.delete_selected
        ).grid(row=4, column=0, columnspan=2, pady=5)

        columns = ("id", "medicine_id", "quantity", "action", "date")

        self.table = ttk.Treeview(
            right,
            columns=columns,
            show="headings"
        )

        self.table.heading("id", text="ID")
        self.table.heading("medicine_id", text="Medicine ID")
        self.table.heading("quantity", text="Quantity")
        self.table.heading("action", text="Action")
        self.table.heading("date", text="Date")

        self.table.column("id", width=40, anchor="center")
        self.table.column("medicine_id", width=90, anchor="center")
        self.table.column("quantity", width=80, anchor="center")
        self.table.column("action", width=80, anchor="center")
        self.table.column("date", width=160, anchor="center")

        self.table.pack(expand=True, fill="both")

        self.load_data()

    def add_movement(self):
        try:
            self.service.add_movement(
                self.medicine_id_entry.get(),
                self.quantity_entry.get(),
                self.action_combo.get()
            )

            messagebox.showinfo("Success", "Inventory movement added.")

            self.clear_inputs()
            self.load_data()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_data(self):
        for row in self.table.get_children():
            self.table.delete(row)

        for item in self.service.get_all_movements():
            self.table.insert(
                "",
                "end",
                values=(
                    item.id,
                    item.medicine_id,
                    item.quantity_change,
                    item.action_type,
                    item.action_date
                )
            )

    def delete_selected(self):
        selected = self.table.selection()

        if not selected:
            messagebox.showwarning("Warning", "Select a movement.")
            return

        movement_id = int(self.table.item(selected[0], "values")[0])

        confirm = messagebox.askyesno(
            "Confirm",
            "Delete this inventory record?"
        )

        if not confirm:
            return

        try:
            self.service.delete_movement(movement_id)

            messagebox.showinfo(
                "Success",
                "Inventory record deleted."
            )

            self.load_data()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_inputs(self):
        self.medicine_id_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.action_combo.current(0)

    def back(self):
        go_to_admin_dashboard(
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