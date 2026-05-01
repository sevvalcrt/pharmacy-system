class SaleItem:
    def __init__(self, item_id, sale_id, medicine_id, quantity, unit_price):
        self.id = item_id
        self.sale_id = int(sale_id)
        self.medicine_id = int(medicine_id)
        self.quantity = int(quantity)
        self.unit_price = float(unit_price)
        self.subtotal = 0.0

        self._validate()
        self._recalculate_subtotal()

    def _validate(self):
        if self.sale_id <= 0:
            raise ValueError("The sales ID must be positive.")

        if self.medicine_id <= 0:
            raise ValueError("Medicine ID must be positive.")

        if self.quantity <= 0:
            raise ValueError("The amount must be greater than 0.")

        if self.unit_price <= 0:
            raise ValueError("The unit price must be greater than 0.")

    def _recalculate_subtotal(self):
        self.subtotal = self.quantity * self.unit_price

    def set_quantity(self, new_quantity):
        new_quantity = int(new_quantity)

        if new_quantity <= 0:
            raise ValueError("The new amount must be greater than 0.")

        self.quantity = new_quantity
        self._recalculate_subtotal()

    def increase_quantity(self, amount):
        amount = int(amount)

        if amount <= 0:
            raise ValueError("The amount to be increased must be greater than 0.")

        self.quantity += amount
        self._recalculate_subtotal()

    def set_unit_price(self, new_unit_price):
        new_unit_price = float(new_unit_price)

        if new_unit_price <= 0:
            raise ValueError("The new unit price must be greater than 0.")

        self.unit_price = new_unit_price
        self._recalculate_subtotal()

    def decrease_quantity(self, amount):
        amount = int(amount)

        if amount <= 0:
            raise ValueError("The amount to be decreased must be greater than 0.")

        if amount >= self.quantity:
            raise ValueError("Quantity cannot be zero or negative. Remove the item instead.")

        self.quantity -= amount
        self._recalculate_subtotal()

    def display_info(self):
        return (
            f"SaleItem ID: {self.id}, Sale ID: {self.sale_id}, "
            f"Medicine ID: {self.medicine_id}, Qty: {self.quantity}, "
            f"Unit Price: {self.unit_price:.2f}, Subtotal: {self.subtotal:.2f}"
        )
    