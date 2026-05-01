from datetime import datetime


class Medicine:
    def __init__(self, medicine_id, name, category_id, unit_price, stock, expiry_date=None, requires_prescription=False):
        self.id = medicine_id
        self.name = name.strip()
        self.category_id = category_id
        self.unit_price = float(unit_price)
        self.stock = int(stock)
        self.expiry_date = expiry_date.strip() if isinstance(expiry_date, str) else expiry_date
        self.requires_prescription = bool(requires_prescription)
        self._validate()

    def _validate(self):
        if not self.name:
            raise ValueError("The drug name cannot be empty.")

        if self.category_id is not None and self.category_id <= 0:
            raise ValueError("Category ID must be positive.")

        if self.unit_price <= 0:
            raise ValueError("The unit price must be greater than 0.")

        if self.stock < 0:
            raise ValueError("Stock cannot be negative.")

        if self.expiry_date:
            self._validate_expiry_date(self.expiry_date)

    def _validate_expiry_date(self, date_text):
        try:
            datetime.strptime(date_text, "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError("The expiration date must be in the format YYYY-MM-DD.") from exc

    def update_price(self, new_price):
        new_price = float(new_price)

        if new_price <= 0:
            raise ValueError("The new price must be greater than 0.")

        self.unit_price = new_price

    def add_stock(self, quantity):
        quantity = int(quantity)

        if quantity <= 0:
            raise ValueError("The stock to be added must be greater than 0.")

        self.stock += quantity

    def reduce_stock(self, quantity):
        quantity = int(quantity)

        if quantity <= 0:
            raise ValueError("The stock to be deducted must be greater than 0.")

        if self.is_expired():
            raise ValueError("Expired medication cannot be removed from stock or sold.")

        if quantity > self.stock:
            raise ValueError("Insufficient stock.")

        self.stock -= quantity

    def is_available(self, quantity=1):
        quantity = int(quantity)

        if quantity <= 0:
            raise ValueError("The amount to be checked must be greater than 0.")

        return (not self.is_expired()) and self.stock >= quantity

    def set_expiry_date(self, new_expiry_date):
        new_expiry_date = new_expiry_date.strip()
        self._validate_expiry_date(new_expiry_date)
        self.expiry_date = new_expiry_date

    def is_expired(self):
        if not self.expiry_date:
            return False

        expiry = datetime.strptime(self.expiry_date, "%Y-%m-%d").date()
        return expiry < datetime.now().date()

    def display_info(self):
        expiry_text = self.expiry_date if self.expiry_date else "-"
        prescription_text = "Required" if self.requires_prescription else "Not Required"

        return (
            f"Medicine ID: {self.id}, Name: {self.name}, "
            f"Category ID: {self.category_id}, Price: {self.unit_price:.2f}, "
            f"Stock: {self.stock}, EXP: {expiry_text}, "
            f"Prescription: {prescription_text}"
        )
    
    def mark_as_prescription_required(self):
        self.requires_prescription = True


    def mark_as_non_prescription(self):
        self.requires_prescription = False

    def can_be_sold(self, quantity):
        if not self.is_available(quantity):
            return False

        if self.requires_prescription:
            return False  # reçete kontrolü service'te yapılacak

        return True
    
    def is_low_stock(self, threshold=10):
        return self.stock <= threshold
    
    def get_status(self):
        if self.is_expired():
            return "Expired"
        elif self.is_low_stock():
            return "Low Stock"
        else:
            return "Available"