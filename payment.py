class Payment:
    VALID_METHODS = {"CASH", "CARD", "TRANSFER"}

    def __init__(self, payment_id, sale_id, amount, method):
        self.id = payment_id
        self.sale_id = int(sale_id)
        self.amount = float(amount)
        self.method = method.strip().upper()
        self._validate()

    def _validate(self):
        if self.sale_id <= 0:
            raise ValueError("The sales ID must be positive.")
        if self.amount <= 0:
            raise ValueError("Payment amount must be greater than 0.")
        if self.method not in self.VALID_METHODS:
            raise ValueError("Payment type must be CASH, CARD, or TRANSFER.")

    def set_method(self, new_method):
        new_method = new_method.strip().upper()
        if new_method not in self.VALID_METHODS:
            raise ValueError("Invalid payment type.")
        self.method = new_method

    def calculate_change(self, total_amount):
        total_amount = float(total_amount)
        if total_amount < 0:
            raise ValueError("The total amount cannot be negative.")
        if self.amount < total_amount:
            raise ValueError("The amount paid is insufficient.")
        return self.amount - total_amount

    def display_info(self):
        return (
            f"Payment ID: {self.id}, Sale ID: {self.sale_id}, "
            f"Amount: {self.amount:.2f}, Method: {self.method}"
        )
