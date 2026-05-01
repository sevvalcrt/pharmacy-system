from datetime import datetime


class Batch:
    def __init__(self, batch_id, medicine_id, supplier_id, lot_number, expiry_date):
        self.id = batch_id
        self.medicine_id = medicine_id
        self.supplier_id = supplier_id
        self.lot_number = lot_number.strip()
        self.expiry_date = expiry_date.strip()
        self._validate()

    def _validate(self):
        if self.medicine_id <= 0:
            raise ValueError("Medicine ID must be positive.")
        if self.supplier_id <= 0:
            raise ValueError("Supplier ID must be positive.")
        if not self.lot_number:
            raise ValueError("Lot numbers cannot be empty.")
        self._validate_expiry_date(self.expiry_date)

    def _validate_expiry_date(self, date_text):
        try:
            datetime.strptime(date_text, "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError("The expiration date must be in the format YYYY-MM-DD.") from exc

    def set_expiry_date(self, new_expiry_date):
        new_expiry_date = new_expiry_date.strip()
        self._validate_expiry_date(new_expiry_date)
        self.expiry_date = new_expiry_date

    def is_expired(self):
        expiry = datetime.strptime(self.expiry_date, "%Y-%m-%d").date()
        return expiry < datetime.now().date()

    def display_info(self):
        return (
            f"Batch ID: {self.id}, Medicine ID: {self.medicine_id}, "
            f"Supplier ID: {self.supplier_id}, Lot No: {self.lot_number}, "
            f"EXP: {self.expiry_date}"
        )
