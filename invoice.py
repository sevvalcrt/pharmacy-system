from datetime import datetime


class Invoice:
    def __init__(
        self,
        invoice_id,
        sale_id,
        invoice_number,
        customer_name,
        cashier_name,
        items,
        total_amount,
        paid_amount,
        change_amount,
        payment_method,
        issued_at=None
    ):
        self.id = invoice_id
        self.sale_id = int(sale_id)
        self.invoice_number = invoice_number.strip().upper()
        self.customer_name = customer_name
        self.cashier_name = cashier_name
        self.items = items
        self.total_amount = float(total_amount)
        self.paid_amount = float(paid_amount)
        self.change_amount = float(change_amount)
        self.payment_method = payment_method.strip().upper()
        self.issued_at = issued_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self._validate()

    def _validate(self):
        if self.sale_id <= 0:
            raise ValueError("Sale ID must be positive.")

        if not self.invoice_number:
            raise ValueError("Invoice number cannot be empty.")

        if self.total_amount < 0:
            raise ValueError("Total amount cannot be negative.")

        if self.paid_amount < 0:
            raise ValueError("Paid amount cannot be negative.")

    def generate_text(self):
        item_lines = ""

        for item in self.items:
            item_lines += (
                f"{item['name']} x{item['quantity']} "
                f"= {item['subtotal']:.2f} TL\n"
            )

        return (
            "========== PHARMACY INVOICE ==========\n\n"
            f"Invoice No: {self.invoice_number}\n"
            f"Sale ID: {self.sale_id}\n"
            f"Date: {self.issued_at}\n\n"
            f"Customer: {self.customer_name}\n"
            f"Cashier: {self.cashier_name}\n\n"
            "Items:\n"
            f"{item_lines}"
            "\n--------------------------------------\n"
            f"Payment Method: {self.payment_method}\n"
            f"Total: {self.total_amount:.2f} TL\n"
            f"Paid: {self.paid_amount:.2f} TL\n"
            f"Change: {self.change_amount:.2f} TL\n"
            "======================================"
        )