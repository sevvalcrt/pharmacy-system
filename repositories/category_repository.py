from category import Category
from .base_repository import BaseRepository


class CategoryRepository(BaseRepository):
    def __init__(self, db_manager=None):
        super().__init__(
            table_name="categories",
            model_class=Category,
            columns=["id", "name"],
            db_manager=db_manager
        )

    def _row_to_object(self, row):
        return Category(
            category_id=row["id"],
            name=row["name"]
        )

    def _object_to_dict(self, item):
        return {
            "id": item.id,
            "name": item.name
        }