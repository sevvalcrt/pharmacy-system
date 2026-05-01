class Category:
    def __init__(self, category_id, name):
        self.id = category_id
        self.name = name.strip()
        self._validate()

    def _validate(self):
        if not self.name:
            raise ValueError("The category name cannot be empty.")
        if len(self.name) < 2:
            raise ValueError("The category name must be at least two characters long.")

    def rename(self, new_name):
        new_name = new_name.strip()
        if not new_name:
            raise ValueError("The new category name cannot be empty.")
        if len(new_name) < 2:
            raise ValueError("The new category name must be at least two characters long.")
        self.name = new_name

    def display_info(self):
        return f"Category ID: {self.id}, Category Name: {self.name}"
