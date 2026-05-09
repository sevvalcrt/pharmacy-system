from inventory import Inventory
from .base_repository import BaseRepository


class InventoryRepository(BaseRepository):
    def __init__(self, db_manager=None):
        super().__init__(
            table_name="inventory",
            model_class=Inventory,
            columns=["id", "medicine_id", "sale_id", "quantity_change", "action_type", "action_date"],
            db_manager=db_manager
        )

    def _row_to_object(self, row):
        return Inventory(
            inventory_id=row["id"],
            medicine_id=row["medicine_id"],
            sale_id=row["sale_id"],
            quantity_change=row["quantity_change"],
            action_type=row["action_type"],
            action_date=row["action_date"]
        )

    def _object_to_dict(self, item):
        return {
            "id": item.id,
            "medicine_id": item.medicine_id,
            "sale_id": item.sale_id,
            "quantity_change": item.quantity_change,
            "action_type": item.action_type,
            "action_date": item.action_date
        }