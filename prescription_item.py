class PrescriptionItem:
    def __init__(self, item_id, prescription_id, medicine_id, quantity):
        self.id = item_id
        self.prescription_id = int(prescription_id)
        self.medicine_id = int(medicine_id)
        self.quantity = int(quantity)
        self._validate()

    def _validate(self):
        if self.prescription_id <= 0:
            raise ValueError("Prescription ID must be positive.")
        if self.medicine_id <= 0:
            raise ValueError("Medicine ID must be positive.")
        if self.quantity <= 0:
            raise ValueError("The amount must be greater than 0.")

    def increase_quantity(self, amount):
        amount = int(amount)
        if amount <= 0:
            raise ValueError("The amount to be increased must be greater than 0.")
        self.quantity += amount

    def set_quantity(self, new_quantity):
        new_quantity = int(new_quantity)
        if new_quantity <= 0:
            raise ValueError("The new amount must be greater than 0.")
        self.quantity = new_quantity

    def display_info(self):
        return (
            f"Prescription Item ID: {self.id}, Prescription ID: {self.prescription_id}, "
            f"Medicine ID: {self.medicine_id}, Quantity: {self.quantity}"
        )
