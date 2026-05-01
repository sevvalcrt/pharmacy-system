from sale_item import SaleItem


class SalesService:
    def __init__(self, medicine_repo, sale_repo, prescription_repo=None, pharmacist=None):
        self.medicine_repo = medicine_repo
        self.sale_repo = sale_repo
        self.prescription_repo = prescription_repo
        self.pharmacist = pharmacist

    def add_medicine_to_sale(self, sale, medicine_id, quantity):
        if sale is None:
            raise ValueError("Sale cannot be empty.")

        if sale.is_completed:
            raise ValueError("Completed sale cannot be changed.")

        quantity = int(quantity)

        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0.")

        medicine = self.medicine_repo.get_by_id(medicine_id)

        if medicine is None:
            raise ValueError("Medicine not found.")

        if not medicine.is_available(quantity):
            raise ValueError("Medicine is expired or stock is insufficient.")

        if medicine.requires_prescription:
            if self.prescription_repo is None:
                raise ValueError("Prescription repository is required for prescription medicines.")

            if sale.prescription_id is None:
                raise ValueError("This medicine requires a prescription.")

            prescription = self.prescription_repo.get_by_id(sale.prescription_id)

            if prescription is None:
                raise ValueError("Prescription not found.")

            temp_item = SaleItem(None, sale.id, medicine.id, quantity, medicine.unit_price)

            if self.pharmacist is not None:
                self.pharmacist.validate_prescription(
                    prescription,
                    [temp_item],
                    self.medicine_repo
                )

        sale_item = SaleItem(None, sale.id, medicine.id, quantity, medicine.unit_price)
        sale.add_item(sale_item)
        return sale_item

    def complete_sale(self, sale):
        if sale is None:
            raise ValueError("Sale cannot be empty.")

        if sale.is_empty():
            raise ValueError("Cannot complete an empty sale.")

        if sale.is_completed:
            raise ValueError("Sale is already completed.")

        for item in sale.items:
            medicine = self.medicine_repo.get_by_id(item.medicine_id)

            if medicine is None:
                raise ValueError("Medicine not found.")

            medicine.reduce_stock(item.quantity)

        sale.complete_sale()
        self.sale_repo.add(sale)
        return sale