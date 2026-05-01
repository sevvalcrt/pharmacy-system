class BaseRepository:
    def __init__(self):
        self.items = []

    def add(self, item):
        if item is None:
            raise ValueError("Item cannot be empty.")
        
        if item.id is None:
            raise ValueError("Item ID cannot be None.")

        if self.get_by_id(item.id) is not None:
            raise ValueError("Item with this ID already exists.")

        self.items.append(item)

    def is_empty(self):
        return len(self.items) == 0

    def get_all(self):
        return list(self.items)

    def get_by_id(self, item_id):
        for item in self.items:
            if item.id == item_id:
                return item
        return None

    def remove_by_id(self, item_id):
        item = self.get_by_id(item_id)

        if item is None:
            raise ValueError("Item not found.")

        self.items.remove(item)
        return item

    def update(self, item_id, new_item):
        if new_item is None:
            raise ValueError("New item cannot be empty.")

        if new_item.id != item_id:
            raise ValueError("Item ID mismatch.")

        for i, item in enumerate(self.items):
            if item.id == item_id:
                self.items[i] = new_item
                return new_item

        raise ValueError("Item not found.")

    def exists(self, item_id):
        return self.get_by_id(item_id) is not None

    def count(self):
        return len(self.items)

    def clear(self):
        self.items.clear()