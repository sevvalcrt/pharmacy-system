import tkinter as tk


class PharmacistDashboard:
    def __init__(self, root, user, db):
        self.root = root
        self.user = user
        self.db = db

        self.frame = tk.Frame(self.root)
        self.frame.pack(expand=True, fill="both")

        tk.Label(
            self.frame,
            text=f"Pharmacist Dashboard - Welcome {user.full_name}",
            font=("Arial", 18, "bold")
        ).pack(pady=20)

        tk.Button(
            self.frame,
            text="Manage Prescriptions",
            width=25,
            command=self.open_prescriptions
        ).pack(pady=5)

        tk.Button(
            self.frame,
            text="Medicine Status",
            width=25,
            command=self.open_status
        ).pack(pady=5)

        tk.Button(
            self.frame,
            text="Logout",
            width=25,
            command=self.logout
        ).pack(pady=20)

    def open_prescriptions(self):
        self.frame.destroy()
        from gui.prescription_frame import PrescriptionFrame
        PrescriptionFrame(self.root, self.user, self.db)

    def open_status(self):
        self.frame.destroy()
        from gui.medicine_status_frame import MedicineStatusFrame
        MedicineStatusFrame(self.root, self.user, self.db)

    def logout(self):
        self.frame.destroy()
        from gui.login_window import LoginWindow
        LoginWindow(self.root, self.db)