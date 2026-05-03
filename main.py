import tkinter as tk

from database.connection import DatabaseManager
from gui.login_window import LoginWindow


def main():
    root = tk.Tk()
    root.title("Pharmacy Medicine System")

    root.geometry("900x650")
    root.minsize(800, 550)
    root.resizable(True, True)

    db = DatabaseManager()

    LoginWindow(root, db)

    root.mainloop()


if __name__ == "__main__":
    main()