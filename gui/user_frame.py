import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from services.user_service import UserService
from gui.navigation import go_to_login, go_to_admin_dashboard


class UserFrame:
    def __init__(self, root, current_user, db):
        self.root = root
        self.current_user = current_user
        self.db = db

        self.service = UserService(self.db)

        self.frame = tk.Frame(self.root)
        self.frame.pack(expand=True, fill="both")

        self.create_top_bar()
        self.create_title()
        self.create_form()
        self.create_buttons()
        self.create_table()

        self.load_users()

    def create_top_bar(self):
        top_bar = tk.Frame(self.frame)
        top_bar.pack(anchor="nw", padx=10, pady=10)

        tk.Button(
            top_bar,
            text="← Back",
            width=8,
            command=self.back
        ).grid(row=0, column=0, padx=3)

        tk.Button(
            top_bar,
            text="Logout",
            width=8,
            command=self.logout
        ).grid(row=0, column=1, padx=3)

    def create_title(self):
        tk.Label(
            self.frame,
            text="Manage Users",
            font=("Arial", 18, "bold")
        ).pack(pady=10)

    def create_form(self):
        form_frame = tk.Frame(self.frame)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Full Name").grid(row=0, column=0, padx=5, pady=5)
        self.full_name_entry = tk.Entry(form_frame, width=25)
        self.full_name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Username").grid(row=1, column=0, padx=5, pady=5)
        self.username_entry = tk.Entry(form_frame, width=25)
        self.username_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Password").grid(row=2, column=0, padx=5, pady=5)
        self.password_entry = tk.Entry(form_frame, width=25, show="*")
        self.password_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Role").grid(row=3, column=0, padx=5, pady=5)

        self.role_combo = ttk.Combobox(
            form_frame,
            values=["Admin", "Pharmacist", "Cashier"],
            state="readonly",
            width=22
        )

        self.role_combo.grid(row=3, column=1, padx=5, pady=5)
        self.role_combo.current(2)

    def create_buttons(self):
        button_frame = tk.Frame(self.frame)
        button_frame.pack(pady=5)

        tk.Button(
            button_frame,
            text="Add User",
            width=15,
            command=self.add_user
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            button_frame,
            text="Delete Selected",
            width=15,
            command=self.delete_selected_user
        ).grid(row=0, column=1, padx=5)

    def create_table(self):
        columns = ("id", "full_name", "username", "role")

        self.user_table = ttk.Treeview(
            self.frame,
            columns=columns,
            show="headings",
            height=10
        )

        self.user_table.heading("id", text="ID")
        self.user_table.heading("full_name", text="Full Name")
        self.user_table.heading("username", text="Username")
        self.user_table.heading("role", text="Role")

        self.user_table.column("id", width=50)
        self.user_table.column("full_name", width=180)
        self.user_table.column("username", width=150)
        self.user_table.column("role", width=100)

        self.user_table.pack(pady=10)

    def add_user(self):
        try:
            role_id = self.service.role_text_to_id(
                self.role_combo.get()
            )

            self.service.create_user(
                self.full_name_entry.get(),
                self.username_entry.get(),
                self.password_entry.get(),
                role_id
            )

            messagebox.showinfo(
                "Success",
                "User added."
            )

            self.clear_inputs()
            self.load_users()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_users(self):
        for row in self.user_table.get_children():
            self.user_table.delete(row)

        users = self.service.get_all_users()

        for user in users:
            self.user_table.insert(
                "",
                "end",
                values=(
                    user.id,
                    user.full_name,
                    user.username,
                    self.service.role_id_to_text(user.role_id)
                )
            )

    def delete_selected_user(self):
        selected = self.user_table.selection()

        if not selected:
            messagebox.showwarning(
                "Warning",
                "Select a user."
            )
            return

        values = self.user_table.item(selected[0], "values")
        user_id = int(values[0])

        confirm = messagebox.askyesno(
            "Confirm",
            "Delete this user?"
        )

        if not confirm:
            return

        try:
            self.service.delete_user(
                user_id,
                self.current_user.id
            )

            messagebox.showinfo(
                "Success",
                "User deleted."
            )

            self.load_users()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_inputs(self):
        self.full_name_entry.delete(0, tk.END)
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

        self.role_combo.current(2)

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