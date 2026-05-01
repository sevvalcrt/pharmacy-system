class Customer:
    def __init__(self, customer_id, full_name, phone):
        self.id = customer_id
        self.full_name = full_name.strip()
        self.phone = phone.strip()
        self._validate()

    def _validate(self):
        if not self.full_name:
            raise ValueError("Customer name and surname cannot be left blank.")
        if self.phone and (not self.phone.isdigit() or len(self.phone) < 10):
            raise ValueError("The phone number must be purely numeric and contain at least 10 digits.")

    def update_contact(self, new_phone):
        new_phone = new_phone.strip()
        if not new_phone.isdigit() or len(new_phone) < 10:
            raise ValueError("The phone number must be purely numeric and have at least 10 digits.")
        self.phone = new_phone

    def display_info(self):
        return f"Customer ID: {self.id}, Name Surname: {self.full_name}, Phone Number: {self.phone}"
