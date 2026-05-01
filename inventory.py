from datetime import datetime


class Inventory:
    VALID_ACTIONS = {"IN", "OUT", "RETURN", "ADJUST"}

    def __init__(self, inventory_id, medicine_id, quantity_change, action_type, action_date=None):
        self.id = inventory_id
        self.medicine_id = int(medicine_id)
        self.quantity_change = int(quantity_change)
        self.action_type = action_type.strip().upper()
        self.action_date = action_date.strip() if isinstance(action_date, str) else action_date
        self._validate()

    def _validate(self):
        if self.medicine_id <= 0:
            raise ValueError("Medicine ID must be positive.")
        if self.quantity_change == 0:
            raise ValueError("The quantity change cannot be 0.")
        if self.action_type not in self.VALID_ACTIONS:
            raise ValueError("Invalid movement type. Must be IN, OUT, RETURN, or ADJUST.")

        if self.action_date is None:
            self.action_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            self._validate_action_date(self.action_date)

    def _validate_action_date(self, date_text):
        try:
            datetime.strptime(date_text, "%Y-%m-%d %H:%M:%S")
        except ValueError as exc:
            raise ValueError("Date format must be YYYY-MM-DD HH:MM:SS.") from exc

    def set_action_type(self, new_action_type):
        new_action_type = new_action_type.strip().upper()
        if new_action_type not in self.VALID_ACTIONS:
            raise ValueError("Invalid movement type.")
        self.action_type = new_action_type

    def apply_to_stock(self, current_stock):
        current_stock = int(current_stock)
        new_stock = current_stock + self.quantity_change
        if new_stock < 0:
            raise ValueError("This action is causing the inventory level to become negative.")
        return new_stock

    def display_info(self):
        return (
            f"Inventory ID: {self.id}, Medicine ID: {self.medicine_id}, "
            f"Change: {self.quantity_change}, Action: {self.action_type}, "
            f"Date: {self.action_date}"
        )
