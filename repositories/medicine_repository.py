from medicine import Medicine
from .base_repository import BaseRepository


class MedicineRepository(BaseRepository):
    def __init__(self, db_manager=None):
        super().__init__(
            table_name="medicines",
            model_class=Medicine,
            columns=["id", "name", "category_id", "unit_price", "stock", "expiry_date", "requires_prescription"],
            db_manager=db_manager
        )

    def _row_to_object(self, row):
        return Medicine(
            medicine_id=row["id"],
            name=row["name"],
            category_id=row["category_id"],
            unit_price=row["unit_price"],
            stock=row["stock"],
            expiry_date=row["expiry_date"],
            requires_prescription=bool(row["requires_prescription"])
        )

    def _object_to_dict(self, item):
        return {
            "id": item.id,
            "name": item.name,
            "category_id": item.category_id,
            "unit_price": item.unit_price,
            "stock": item.stock,
            "expiry_date": item.expiry_date,
            "requires_prescription": 1 if item.requires_prescription else 0
        }

    def search_by_name(self, keyword):
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM medicines WHERE name LIKE ? ORDER BY name",
                (f"%{keyword}%",)
            )
            rows = cursor.fetchall()
        return [self._row_to_object(row) for row in rows]
