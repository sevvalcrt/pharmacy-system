from User import User


class Cashier(User):
    VALID_PAYMENT_METHODS = {"CASH", "CARD", "TRANSFER"}

    def __init__(self, user_id, full_name, username, password):
        super().__init__(user_id, full_name, username, password, role_id=3)
        self.can_process_payments = True

    def calculate_total(self, unit_price, quantity):
        unit_price = float(unit_price)
        quantity = int(quantity)

        if unit_price <= 0:
            raise ValueError("The unit price must be greater than 0.")
        if quantity <= 0:
            raise ValueError("The quantity must be greater than 0.")

        return unit_price * quantity

    def process_payment(self, total_amount, paid_amount, method="CASH"):
        total_amount = float(total_amount)
        paid_amount = float(paid_amount)
        method = method.strip().upper()

        if total_amount <= 0:
            raise ValueError("The total amount must be greater than 0.")

        if method not in self.VALID_PAYMENT_METHODS:
            raise ValueError("Payment method must be CASH, CARD, or TRANSFER.")

        if method == "CASH" and paid_amount < total_amount:
            raise ValueError("The amount paid is insufficient.")

        if method in ("CARD", "TRANSFER"):
            return 0.0

        return paid_amount - total_amount
    
    def can_process(self, sale):
        if sale is None:
            return False

        if sale.is_empty():
            return False

        if sale.is_completed:
            return False

        return True

    def generate_payment_summary(self, sale, paid_amount, method="CASH"):
        if sale is None:
            raise ValueError("Sale cannot be empty.")

        method = method.strip().upper()  

        change = self.process_payment(sale.total_amount, paid_amount, method)

        return (
            f"Sale ID: {sale.id}\n"
            f"Total Amount: {sale.total_amount:.2f}\n"
            f"Paid Amount: {float(paid_amount):.2f}\n"
            f"Payment Method: {method}\n"
            f"Change: {change:.2f}"
        )