from sale import Sale
from sale_item import SaleItem
from .base_repository import BaseRepository


class SaleRepository(BaseRepository):
    def __init__(self, db_manager=None):
        super().__init__(
            table_name="sales",
            model_class=Sale,
            columns=["id", "customer_id", "prescription_id", "total_amount", "sale_date", "is_completed"],
            db_manager=db_manager
        )

    def _row_to_object(self, row):
        sale = Sale(
            sale_id=row["id"],
            customer_id=row["customer_id"],
            prescription_id=row["prescription_id"],
            total_amount=row["total_amount"],
            sale_date=row["sale_date"]
        )
        sale.is_completed = bool(row["is_completed"])
        sale.items = self.get_items_by_sale_id(sale.id)
        return sale

    def _object_to_dict(self, item):
        item.calculate_total()
        return {
            "id": item.id,
            "customer_id": item.customer_id,
            "prescription_id": item.prescription_id,
            "total_amount": item.total_amount,
            "sale_date": item.sale_date,
            "is_completed": 1 if item.is_completed else 0
        }

    def add(self, sale):
        super().add(sale)
        self._save_sale_items(sale)
        return sale

    def update(self, item_id, new_item):
        super().update(item_id, new_item)
        self._delete_sale_items(item_id)
        self._save_sale_items(new_item)
        return new_item

    def _save_sale_items(self, sale):
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            for item in sale.items:
                cursor.execute(
                    """
                    INSERT INTO sale_items(sale_id, medicine_id, quantity, unit_price, subtotal)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (sale.id, item.medicine_id, item.quantity, item.unit_price, item.subtotal)
                )
                item.id = cursor.lastrowid
                
    def _delete_sale_items(self, sale_id):
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
            "DELETE FROM sale_items WHERE sale_id = ?",
            (sale_id,)
        )
    def remove_by_id(self, sale_id):
        sale = self.get_by_id(sale_id)

        if sale is None:
            return None

        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM sale_items WHERE sale_id = ?",
                (sale_id,)
            )

            cursor.execute(
                "DELETE FROM sales WHERE id = ?",
                (sale_id,)
            )

        return sale


    def get_items_by_sale_id(self, sale_id):
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sale_items WHERE sale_id = ? ORDER BY id", (sale_id,))
            rows = cursor.fetchall()

        return [
            SaleItem(
                item_id=row["id"],
                sale_id=row["sale_id"],
                medicine_id=row["medicine_id"],
                quantity=row["quantity"],
                unit_price=row["unit_price"]
            )
            for row in rows
        ]
