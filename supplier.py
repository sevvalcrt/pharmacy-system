class Supplier:
    def __init__(self, supplier_id, name, phone, address):
        self.id = supplier_id
        self.name = name.strip()
        self.phone = phone.strip()
        self.address = address.strip()
        self._validate()

    def _validate(self):
        if not self.name:
            raise ValueError("The supplier name cannot be empty.")
        if self.phone and (not self.phone.isdigit() or len(self.phone) < 10):
            raise ValueError("The phone number must be purely numeric and contain at least 10 digits.")
        if not self.address:
            raise ValueError("The address cannot be empty.")

    def update_contact_info(self, new_phone, new_address):
        new_phone = new_phone.strip()
        new_address = new_address.strip()
        if not new_phone.isdigit() or len(new_phone) < 10:
            raise ValueError("The phone number must be purely numeric and have at least 10 digits.")
        if not new_address:
            raise ValueError("The address cannot be empty.")
        self.phone = new_phone
        self.address = new_address

    def display_info(self):
        return (
            f"Supplier ID: {self.id}, Name: {self.name}, "
            f"Telephone: {self.phone}, Address: {self.address}"
        )
