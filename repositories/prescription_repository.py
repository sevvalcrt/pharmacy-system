from prescription import Prescription
from prescription_item import PrescriptionItem
from .base_repository import BaseRepository


class PrescriptionRepository(BaseRepository):
    def __init__(self, db_manager=None):
        super().__init__(
            table_name="prescriptions",
            model_class=Prescription,
            columns=["id", "customer_id", "doctor_name", "created_at"],
            db_manager=db_manager
        )

    def _row_to_object(self, row):
        prescription = Prescription(
            prescription_id=row["id"],
            customer_id=row["customer_id"],
            doctor_name=row["doctor_name"],
            created_at=row["created_at"]
        )
        prescription.items = self.get_items_by_prescription_id(prescription.id)
        return prescription

    def _object_to_dict(self, item):
        return {
            "id": item.id,
            "customer_id": item.customer_id,
            "doctor_name": item.doctor_name,
            "created_at": item.created_at
        }

    def add(self, prescription):
        super().add(prescription)
        self._save_prescription_items(prescription)
        return prescription

    def update(self, item_id, new_item):
        super().update(item_id, new_item)
        self._delete_prescription_items(item_id)
        self._save_prescription_items(new_item)
        return new_item

    def _save_prescription_items(self, prescription):
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            for item in prescription.items:
                cursor.execute(
                    """
                    INSERT INTO prescription_items(prescription_id, medicine_id, quantity)
                    VALUES (?, ?, ?)
                    """,
                    (prescription.id, item.medicine_id, item.quantity)
                )
                item.id = cursor.lastrowid

    def _delete_prescription_items(self, prescription_id):
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM prescription_items WHERE prescription_id = ?", (prescription_id,))

    def get_items_by_prescription_id(self, prescription_id):
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM prescription_items WHERE prescription_id = ? ORDER BY id",
                (prescription_id,)
            )
            rows = cursor.fetchall()

        return [
            PrescriptionItem(
                item_id=row["id"],
                prescription_id=row["prescription_id"],
                medicine_id=row["medicine_id"],
                quantity=row["quantity"]
            )
            for row in rows
        ]
