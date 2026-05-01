from datetime import datetime


class Prescription:
    def __init__(self, prescription_id, customer_id, doctor_name, created_at=None):
        self.id = prescription_id
        self.customer_id = int(customer_id)
        self.doctor_name = doctor_name.strip()
        self.created_at = created_at.strip() if isinstance(created_at, str) else created_at
        self.items = []
        self._validate()

    def add_item(self, prescription_item):
        if prescription_item is None:
            raise ValueError("Prescription medicine cannot be left empty.")

        if prescription_item.prescription_id != self.id:
            raise ValueError("The prescription item does not belong to this prescription.")

        self.items.append(prescription_item)

    def remove_item(self, medicine_id):
        for item in self.items:
            if item.medicine_id == medicine_id:
                self.items.remove(item)
                return item

        raise ValueError("This medication was not available on the prescription.")
    
    def get_item_by_medicine_id(self, medicine_id):
        for item in self.items:
            if item.medicine_id == medicine_id:
                return item
        return None

    def has_medicine(self, medicine_id):
        return any(item.medicine_id == medicine_id for item in self.items)
    
    def allows_quantity(self, medicine_id, quantity):
        quantity = int(quantity)

        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0.")

        item = self.get_item_by_medicine_id(medicine_id)

        if item is None:
            return False

        return quantity <= item.quantity
    
    def _validate(self):
        if self.customer_id <= 0:
            raise ValueError("Customer ID must be positive.")
        if not self.doctor_name:
            raise ValueError("The doctor's name cannot be empty.")

        if self.created_at is None:
            self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            self._validate_created_at(self.created_at)

    def _validate_created_at(self, date_text):
        try:
            datetime.strptime(date_text, "%Y-%m-%d %H:%M:%S")
        except ValueError as exc:
            raise ValueError("Date format must be YYYY-MM-DD HH:MM:SS.") from exc

    def set_doctor_name(self, new_doctor_name):
        new_doctor_name = new_doctor_name.strip()
        if not new_doctor_name:
            raise ValueError("The doctor's name cannot be empty.")
        self.doctor_name = new_doctor_name

    def is_empty(self):
        return len(self.items) == 0
    
    def total_medicines(self):
        return sum(item.quantity for item in self.items)

    def display_info(self):
        return (
            f"Prescription ID: {self.id}, Customer ID: {self.customer_id}, "
            f"Doctor: {self.doctor_name}, Date: {self.created_at}, "
            f"Medicine Count: {self.total_medicines()}"
        )
