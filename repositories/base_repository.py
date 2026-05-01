from database.connection import DatabaseManager


class BaseRepository:
    def __init__(self, table_name, model_class, columns, db_manager=None):
        self.table_name = table_name
        self.model_class = model_class
        self.columns = columns
        self.db_manager = db_manager or DatabaseManager()

    def _row_to_object(self, row):
        raise NotImplementedError("Subclasses must implement _row_to_object().")

    def _object_to_dict(self, item):
        raise NotImplementedError("Subclasses must implement _object_to_dict().")

    def add(self, item):
        if item is None:
            raise ValueError("Item cannot be empty.")

        data = self._object_to_dict(item)
        insert_data = {key: value for key, value in data.items() if key != "id" or value is not None}

        columns_text = ", ".join(insert_data.keys())
        placeholders = ", ".join(["?"] * len(insert_data))
        values = tuple(insert_data.values())

        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"INSERT INTO {self.table_name} ({columns_text}) VALUES ({placeholders})",
                values
            )
            if getattr(item, "id", None) is None:
                item.id = cursor.lastrowid

        return item

    def get_all(self):
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {self.table_name} ORDER BY id")
            rows = cursor.fetchall()

        return [self._row_to_object(row) for row in rows]

    def get_by_id(self, item_id):
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {self.table_name} WHERE id = ?", (item_id,))
            row = cursor.fetchone()

        if row is None:
            return None
        return self._row_to_object(row)

    def remove_by_id(self, item_id):
        item = self.get_by_id(item_id)
        if item is None:
            raise ValueError("Item not found.")

        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {self.table_name} WHERE id = ?", (item_id,))

        return item

    def update(self, item_id, new_item):
        if new_item is None:
            raise ValueError("New item cannot be empty.")

        if getattr(new_item, "id", None) != item_id:
            raise ValueError("Item ID mismatch.")

        if self.get_by_id(item_id) is None:
            raise ValueError("Item not found.")

        data = self._object_to_dict(new_item)
        update_data = {key: value for key, value in data.items() if key != "id"}
        set_text = ", ".join([f"{key} = ?" for key in update_data.keys()])
        values = tuple(update_data.values()) + (item_id,)

        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE {self.table_name} SET {set_text} WHERE id = ?",
                values
            )

        return new_item

    def exists(self, item_id):
        return self.get_by_id(item_id) is not None

    def count(self):
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) AS count FROM {self.table_name}")
            row = cursor.fetchone()
        return row["count"]

    def is_empty(self):
        return self.count() == 0

    def clear(self):
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {self.table_name}")
