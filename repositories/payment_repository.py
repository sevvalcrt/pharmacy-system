from payment import Payment
from .base_repository import BaseRepository


class PaymentRepository(BaseRepository):
    def __init__(self, db_manager=None):
        super().__init__(
            table_name="payments",
            model_class=Payment,
            columns=["id", "sale_id", "amount", "method"],
            db_manager=db_manager
        )

    def _row_to_object(self, row):
        return Payment(
            row["id"],
            row["sale_id"],
            row["amount"],
            row["method"]
        )

    def _object_to_dict(self, item):
        return {
            "id": item.id,
            "sale_id": item.sale_id,
            "amount": item.amount,
            "method": item.method
        }

    def get_by_sale_id(self, sale_id):
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM payments WHERE sale_id = ?",
                (sale_id,)
            )
            rows = cursor.fetchall()

        return [self._row_to_object(row) for row in rows]