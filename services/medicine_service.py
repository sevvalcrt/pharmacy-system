from medicine import Medicine


class MedicineService:
    def __init__(self, medicine_repo):
        self.medicine_repo = medicine_repo

    def save_medicine(self, name, category_id, price, stock, expiry, requires_prescription):
        name, category_id, price, stock, expiry = self._prepare_medicine_data(
            name,
            category_id,
            price,
            stock,
            expiry
        )

        existing_medicine = self._find_medicine_by_name(name)

        if existing_medicine is not None:
            existing_medicine.stock += stock
            existing_medicine.unit_price = price
            existing_medicine.category_id = category_id
            existing_medicine.expiry_date = expiry
            existing_medicine.requires_prescription = bool(requires_prescription)

            self.medicine_repo.update(existing_medicine.id, existing_medicine)
            return "updated"

        medicine = Medicine(
            None,
            name,
            category_id,
            price,
            stock,
            expiry,
            bool(requires_prescription)
        )

        self.medicine_repo.add(medicine)
        return "created"

    def update_medicine(self, medicine_id, name, category_id, price, stock, expiry, requires_prescription):
        medicine_id = int(medicine_id)

        existing_medicine = self.medicine_repo.get_by_id(medicine_id)
        if existing_medicine is None:
            raise ValueError("Medicine not found.")

        name, category_id, price, stock, expiry = self._prepare_medicine_data(
            name,
            category_id,
            price,
            stock,
            expiry
        )

        medicine = Medicine(
            medicine_id,
            name,
            category_id,
            price,
            stock,
            expiry,
            bool(requires_prescription)
        )

        self.medicine_repo.update(medicine_id, medicine)
        return medicine

    def delete_medicine(self, medicine_id):
        medicine_id = int(medicine_id)

        medicine = self.medicine_repo.get_by_id(medicine_id)
        if medicine is None:
            raise ValueError("Medicine not found.")

        return self.medicine_repo.remove_by_id(medicine_id)

    def get_all_medicines(self):
        return self.medicine_repo.get_all()

    def get_medicine_by_id(self, medicine_id):
        return self.medicine_repo.get_by_id(int(medicine_id))

    def _prepare_medicine_data(self, name, category_id, price, stock, expiry):
        name = name.strip()
        category_id = int(category_id)
        price = float(price)
        stock = int(stock)

        expiry = expiry.strip()
        if expiry == "YYYY-MM-DD" or expiry == "":
            expiry = None

        return name, category_id, price, stock, expiry

    def _find_medicine_by_name(self, name):
        for medicine in self.medicine_repo.get_all():
            if medicine.name.lower() == name.lower():
                return medicine

        return None