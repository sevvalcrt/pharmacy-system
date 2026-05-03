import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from category import Category
from repositories.category_repository import CategoryRepository


class CategoryFrame:
    def __init__(self, root, current_user, db):
        self.root = root
        self.current_user = current_user
        self.db = db
        self.repo = CategoryRepository(self.db)

        self.frame = tk.Frame(self.root, padx=20, pady=15)
        self.frame.pack(expand=True, fill="both")

        top_bar = tk.Frame(self.frame)
        top_bar.pack(fill="x")

        tk.Button(top_bar, text="← Back", width=8, command=self.back).pack(side="left")
        tk.Button(top_bar, text="Logout", width=8, command=self.logout).pack(side="left", padx=5)

        tk.Label(
            self.frame,
            text="Manage Categories",
            font=("Arial", 20, "bold")
        ).pack(pady=15)

        content = tk.Frame(self.frame)
        content.pack(expand=True, fill="both")

        left = tk.LabelFrame(content, text="Category Form", padx=15, pady=15)
        left.pack(side="left", fill="y", padx=(0, 15))

        right = tk.LabelFrame(content, text="Category List", padx=10, pady=10)
        right.pack(side="right", expand=True, fill="both")

        tk.Label(left, text="Category Name").grid(row=0, column=0, sticky="w", pady=6)
        self.name_entry = tk.Entry(left, width=25)
        self.name_entry.grid(row=0, column=1, pady=6)

        tk.Button(
            left,
            text="Add Category",
            width=22,
            command=self.add_category
        ).grid(row=1, column=0, columnspan=2, pady=10)

        tk.Button(
            left,
            text="Delete Selected",
            width=22,
            command=self.delete_selected
        ).grid(row=2, column=0, columnspan=2, pady=5)

        columns = ("id", "name")
        self.table = ttk.Treeview(right, columns=columns, show="headings", height=15)

        self.table.heading("id", text="ID")
        self.table.heading("name", text="Category Name")

        self.table.column("id", width=60, anchor="center")
        self.table.column("name", width=250)

        self.table.pack(expand=True, fill="both")

        self.load_data()

    def add_category(self):
        try:
            name = self.name_entry.get()

            category = Category(None, name)
            self.repo.add(category)

            messagebox.showinfo("Success", "Category added.")
            self.clear_inputs()
            self.load_data()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_data(self):
        for row in self.table.get_children():
            self.table.delete(row)

        for category in self.repo.get_all():
            self.table.insert(
                "",
                "end",
                values=(category.id, category.name)
            )

    def delete_selected(self):
        selected = self.table.selection()

        if not selected:
            messagebox.showwarning("Warning", "Select a category.")
            return

        category_id = int(self.table.item(selected[0], "values")[0])

        confirm = messagebox.askyesno("Confirm", "Delete this category?")
        if not confirm:
            return

        try:
            self.repo.remove_by_id(category_id)
            messagebox.showinfo("Success", "Category deleted.")
            self.load_data()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_inputs(self):
        self.name_entry.delete(0, tk.END)

    def back(self):
        self.frame.destroy()
        from gui.admin_dashboard import AdminDashboard
        AdminDashboard(self.root, self.current_user, self.db)

    def logout(self):
        self.frame.destroy()
        from gui.login_window import LoginWindow
        LoginWindow(self.root, self.db)