from datetime import datetime


class Sale:
    def __init__(self, sale_id, customer_id=None, prescription_id=None, total_amount=0.0, sale_date=None):
        self.id = sale_id
        self.customer_id = int(customer_id) if customer_id is not None else None
        self.prescription_id = int(prescription_id) if prescription_id is not None else None
        self.items = []
        self.total_amount = float(total_amount)
        self.sale_date = sale_date.strip() if isinstance(sale_date, str) else sale_date
        self.is_completed = False
        self._validate()

    def _validate(self):
        if self.customer_id is not None and self.customer_id <= 0:
            raise ValueError("Customer ID must be positive or none.")

        if self.total_amount < 0:
            raise ValueError("The total amount cannot be negative.")

        if self.sale_date is None:
            self.sale_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            self._validate_sale_date(self.sale_date)

        if self.prescription_id is not None and self.prescription_id <= 0:
            raise ValueError("Prescription ID must be positive or none.")

    def _validate_sale_date(self, date_text):
        try:
            datetime.strptime(date_text, "%Y-%m-%d %H:%M:%S")
        except ValueError as exc:
            raise ValueError("The sales date must be in the format YYYY-MM-DD HH:MM:SS.") from exc

    def set_customer(self, customer_id):
        if customer_id is None:
            self.customer_id = None
            return

        customer_id = int(customer_id)

        if customer_id <= 0:
            raise ValueError("Customer ID must be positive.")

        self.customer_id = customer_id

    def add_item(self, sale_item):
        if sale_item is None:
            raise ValueError("Sale item cannot be empty.")

        if sale_item.sale_id != self.id:
            raise ValueError("Sale item does not belong to this sale.")

        for existing_item in self.items:
            if existing_item.medicine_id == sale_item.medicine_id:
                existing_item.increase_quantity(sale_item.quantity)
                self.calculate_total()
                return

        self.items.append(sale_item)
        self.calculate_total()

    def remove_item(self, medicine_id):
        for item in self.items:
            if item.medicine_id == medicine_id:
                self.items.remove(item)
                self.calculate_total()
                return item

        raise ValueError("This medication could not be found on the sales list.")

    def calculate_total(self):
        self.total_amount = sum(item.subtotal for item in self.items)
        return self.total_amount

    def is_empty(self):
        return len(self.items) == 0

    def display_info(self):
        customer_text = self.customer_id if self.customer_id is not None else "Walk-in"
        prescription_text = self.prescription_id if self.prescription_id is not None else "No Prescription"
        status_text = "Completed" if self.is_completed else "Pending"

        return (
            f"Sale ID: {self.id}, Customer: {customer_text}, "
            f"Prescription: {prescription_text}, "
            f"Total: {self.total_amount:.2f}, Date: {self.sale_date}, "
            f"Item Count: {len(self.items)}, Status: {status_text}"
        )
    
    def complete_sale(self):
        if self.is_empty():
            raise ValueError("Cannot complete an empty sale.")
        self.is_completed = True