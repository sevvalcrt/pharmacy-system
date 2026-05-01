from User import User


class Pharmacist(User):
    def __init__(self, user_id, full_name, username, password):
        super().__init__(user_id, full_name, username, password, role_id=2)
        self.can_validate_prescriptions = True

    def validate_prescription(self, prescription, sale_items, medicine_repo=None):
        if prescription is None:
            raise ValueError("Prescription information cannot be empty.")

        if not sale_items:
            raise ValueError("Sale list cannot be empty.")

        for sale_item in sale_items:

            if not prescription.has_medicine(sale_item.medicine_id):
                raise ValueError("This medicine is not in the prescription.")

            if not prescription.allows_quantity(sale_item.medicine_id, sale_item.quantity):
                raise ValueError("Requested quantity exceeds prescription limit.")

            if medicine_repo:
                medicine = medicine_repo.get_by_id(sale_item.medicine_id)

                if medicine is None:
                    raise ValueError("Medicine not found.")

                if not medicine.is_available(sale_item.quantity):
                    raise ValueError("Medicine is not available or insufficient stock.")

        return True

    def suggest_alternative_medicine(self, medicine):
        if medicine is None:
            raise ValueError("Medicine cannot be empty.")

        if medicine.is_expired():
            return "This medicine is expired. Please choose another."

        if medicine.is_low_stock():
            return "Low stock. Consider alternative medicine."

        return "Medicine is available."