from invoice import Invoice
from .base_repository import BaseRepository


class InvoiceRepository(BaseRepository):
    def __init__(self, db_manager=None):
        super().__init__(
            table_name="invoices",
            model_class=Invoice,
            columns=[
                "id",
                "sale_id",
                "invoice_number",
                "customer_name",
                "cashier_name",
                "total_amount",
                "paid_amount",
                "change_amount",
                "payment_method",
                "issued_at"
            ],
            db_manager=db_manager
        )

    def _row_to_object(self, row):
        return Invoice(
            invoice_id=row["id"],
            sale_id=row["sale_id"],
            invoice_number=row["invoice_number"],
            customer_name=row["customer_name"],
            cashier_name=row["cashier_name"],
            items=[],
            total_amount=row["total_amount"],
            paid_amount=row["paid_amount"],
            change_amount=row["change_amount"],
            payment_method=row["payment_method"],
            issued_at=row["issued_at"]
        )

    def _object_to_dict(self, item):
        return {
            "id": item.id,
            "sale_id": item.sale_id,
            "invoice_number": item.invoice_number,
            "customer_name": item.customer_name,
            "cashier_name": item.cashier_name,
            "total_amount": item.total_amount,
            "paid_amount": item.paid_amount,
            "change_amount": item.change_amount,
            "payment_method": item.payment_method,
            "issued_at": item.issued_at
        }

    def get_by_sale_id(self, sale_id):
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM invoices WHERE sale_id = ?",
                (sale_id,)
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return self._row_to_object(row)