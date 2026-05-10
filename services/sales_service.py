from sale import Sale
from sale_item import SaleItem
from payment import Payment
from invoice import Invoice
from inventory import Inventory


class SalesService:
    def __init__(
        self,
        medicine_repo,
        sale_repo,
        prescription_repo,
        payment_repo,
        inventory_repo=None,
        invoice_repo=None
    ):
        self.medicine_repo = medicine_repo
        self.sale_repo = sale_repo
        self.prescription_repo = prescription_repo
        self.payment_repo = payment_repo
        self.inventory_repo = inventory_repo
        self.invoice_repo = invoice_repo

    def get_all_medicines(self):
        return self.medicine_repo.get_all()

    def get_all_prescriptions(self):
        return self.prescription_repo.get_all()

    def get_prescription_by_id(self, prescription_id):
        if prescription_id is None:
            return None
        return self.prescription_repo.get_by_id(prescription_id)

    def validate_medicine_for_cart(self, medicine, quantity, prescription_id):
        quantity = int(quantity)

        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0.")

        if medicine is None:
            raise ValueError("Medicine not found.")

        if not medicine.is_available(quantity):
            raise ValueError("Medicine is expired or stock is insufficient.")

        if medicine.requires_prescription:
            if prescription_id is None:
                raise ValueError("This medicine requires a prescription.")

            prescription = self.get_prescription_by_id(prescription_id)

            if prescription is None:
                raise ValueError("Prescription not found.")

            if not prescription.has_medicine(medicine.id):
                raise ValueError("This medicine is not in the selected prescription.")

            if not prescription.allows_quantity(medicine.id, quantity):
                raise ValueError("Quantity exceeds prescription limit.")

        return True

    def add_to_cart(self, cart, medicine, quantity, prescription_id):
        quantity = int(quantity)

        self.validate_medicine_for_cart(medicine, quantity, prescription_id)

        for item in cart:
            if item["medicine"].id == medicine.id:
                new_quantity = item["quantity"] + quantity

                self.validate_medicine_for_cart(
                    medicine,
                    new_quantity,
                    prescription_id
                )

                item["quantity"] = new_quantity
                item["subtotal"] = medicine.unit_price * new_quantity
                return cart

        cart.append({
            "medicine": medicine,
            "quantity": quantity,
            "unit_price": medicine.unit_price,
            "subtotal": medicine.unit_price * quantity,
            "prescription_id": prescription_id
        })

        return cart

    def get_total(self, cart):
        return sum(item["subtotal"] for item in cart)

    def get_prescription_id_from_cart(self, cart):
        for item in cart:
            if item.get("prescription_id") is not None:
                return item["prescription_id"]
        return None

    def validate_payment(self, total, paid, method):
        method = method.strip().upper()

        if method in ("CARD", "TRANSFER"):
            paid = total

        payment = Payment(None, 1, paid, method)
        change = payment.calculate_change(total)

        return paid, change

    def complete_sale(self, cart, paid_amount, method, cashier_name):
        if not cart:
            raise ValueError("Sale is empty.")

        total = self.get_total(cart)
        paid_amount, change = self.validate_payment(total, paid_amount, method)

        prescription_id = self.get_prescription_id_from_cart(cart)

        customer_id = None
        customer_name = "Walk-in Customer"

        if prescription_id is not None:
            prescription = self.get_prescription_by_id(prescription_id)

            if prescription is not None:
                customer_id = prescription.customer_id
                customer_name = f"Customer ID: {customer_id}"

        sale = Sale(
            None,
            customer_id=customer_id,
            prescription_id=prescription_id
        )

        self.sale_repo.add(sale)

        for cart_item in cart:
            medicine = self.medicine_repo.get_by_id(cart_item["medicine"].id)

            if medicine is None:
                raise ValueError("Medicine not found.")

            if not medicine.is_available(cart_item["quantity"]):
                raise ValueError(f"{medicine.name} stock is insufficient.")

            sale_item = SaleItem(
                None,
                sale.id,
                medicine.id,
                cart_item["quantity"],
                cart_item["unit_price"]
            )

            sale.add_item(sale_item)

            medicine.reduce_stock(cart_item["quantity"])
            self.medicine_repo.update(medicine.id, medicine)

            if self.inventory_repo is not None:
                inventory = Inventory(
                    None,
                    medicine.id,
                    -cart_item["quantity"],
                    "OUT",
                    sale_id=sale.id
                )
                self.inventory_repo.add(inventory)

        sale.complete_sale()
        self.sale_repo.update(sale.id, sale)

        payment = Payment(None, sale.id, paid_amount, method)
        self.payment_repo.add(payment)

        if prescription_id is not None:
            self.prescription_repo.remove_by_id(prescription_id)

        invoice_items = [
            {
                "name": item["medicine"].name,
                "quantity": item["quantity"],
                "subtotal": item["subtotal"]
            }
            for item in cart
        ]

        invoice = Invoice(
            invoice_id=None,
            sale_id=sale.id,
            invoice_number=f"INV-{sale.id}",
            customer_name=customer_name,
            cashier_name=cashier_name,
            items=invoice_items,
            total_amount=total,
            paid_amount=paid_amount,
            change_amount=change,
            payment_method=method
        )

        if self.invoice_repo is not None:
            self.invoice_repo.add(invoice)

        return invoice