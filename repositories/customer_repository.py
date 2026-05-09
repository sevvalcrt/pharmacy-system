from customer import Customer
from .base_repository import BaseRepository


class CustomerRepository(BaseRepository):
    def __init__(self, db_manager=None):
        super().__init__(
            table_name="customers",
            model_class=Customer,
            columns=["id", "full_name", "phone"],
            db_manager=db_manager
        )

    def _row_to_object(self, row):
        return Customer(
            customer_id=row["id"],
            full_name=row["full_name"],
            phone=row["phone"] if row["phone"] else ""
        )

    def _object_to_dict(self, item):
        return {
            "id": item.id,
            "full_name": item.full_name,
            "phone": item.phone
        }