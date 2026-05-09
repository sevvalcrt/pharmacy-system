from medicine import Medicine


class MedicineService:
    def __init__(self, medicine_repo):
        self.medicine_repo = medicine_repo

    def save_medicine(self, name, category_id, price, stock, expiry, requires_prescription):
        name = name.strip()
        category_id = int(category_id)
        price = float(price)
        stock = int(stock)

        expiry = expiry.strip()
        if expiry == "YYYY-MM-DD" or expiry == "":
            expiry = None

        existing_medicine = None

        for medicine in self.medicine_repo.get_all():
            if medicine.name.lower() == name.lower():
                existing_medicine = medicine
                break

        if existing_medicine:
            existing_medicine.stock += stock
            existing_medicine.unit_price = price
            existing_medicine.category_id = category_id
            existing_medicine.expiry_date = expiry
            existing_medicine.requires_prescription = requires_prescription

            self.medicine_repo.update(existing_medicine.id, existing_medicine)
            return "updated"

        medicine = Medicine(
            None,
            name,
            category_id,
            price,
            stock,
            expiry,
            requires_prescription
        )

        self.medicine_repo.add(medicine)
        return "created"

    def delete_medicine(self, medicine_id):
        return self.medicine_repo.remove_by_id(int(medicine_id))

    def get_all_medicines(self):
        return self.medicine_repo.get_all()