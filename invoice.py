class Invoice:
    def __init__(self, invoice_id, sale_id, invoice_number):
        self.id = invoice_id
        self.sale_id = int(sale_id)
        self.invoice_number = invoice_number.strip().upper()
        self._validate()

    def _validate(self):
        if self.sale_id <= 0:
            raise ValueError("The sales ID must be positive.")
        if not self.invoice_number:
            raise ValueError("The invoice number cannot be empty.")
        if len(self.invoice_number) < 5:
            raise ValueError("The invoice number must be at least 5 characters long.")

    def set_invoice_number(self, new_invoice_number):
        new_invoice_number = new_invoice_number.strip().upper()
        if not new_invoice_number:
            raise ValueError("The new invoice number cannot be empty.")
        if len(new_invoice_number) < 5:
            raise ValueError("The new invoice number must be at least 5 characters long.")
        self.invoice_number = new_invoice_number

    def display_info(self):
        return (
            f"Invoice ID: {self.id}, Sale ID: {self.sale_id}, "
            f"Invoice No: {self.invoice_number}"
        )
