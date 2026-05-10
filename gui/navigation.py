def clear_frame(frame):
    frame.destroy()


def go_to_login(root, db, current_frame):
    clear_frame(current_frame)
    from gui.login_window import LoginWindow
    LoginWindow(root, db)


def go_to_admin_dashboard(root, user, db, current_frame):
    clear_frame(current_frame)
    from gui.admin_dashboard import AdminDashboard
    AdminDashboard(root, user, db)


def go_to_cashier_dashboard(root, user, db, current_frame):
    clear_frame(current_frame)
    from gui.cashier_dashboard import CashierDashboard
    CashierDashboard(root, user, db)


def go_to_pharmacist_dashboard(root, user, db, current_frame):
    clear_frame(current_frame)
    from gui.pharmacist_dashboard import PharmacistDashboard
    PharmacistDashboard(root, user, db)
