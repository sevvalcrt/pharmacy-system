from inventory import Inventory
from repositories.inventory_repository import InventoryRepository
from repositories.medicine_repository import MedicineRepository


class InventoryService:
    def __init__(self, db):
        self.inventory_repo = InventoryRepository(db)
        self.medicine_repo = MedicineRepository(db)

    def get_all_movements(self):
        return self.inventory_repo.get_all()

    def add_movement(self, medicine_id, quantity_change, action_type):
        medicine_id = int(medicine_id)
        quantity_change = int(quantity_change)

        medicine = self.medicine_repo.get_by_id(medicine_id)

        if medicine is None:
            raise ValueError("Medicine not found.")

        inventory = Inventory(
            None,
            medicine_id,
            quantity_change,
            action_type
        )

        new_stock = inventory.apply_to_stock(medicine.stock)

        medicine.stock = new_stock

        self.medicine_repo.update(medicine.id, medicine)
        self.inventory_repo.add(inventory)

    def delete_movement(self, movement_id):
        return self.inventory_repo.remove_by_id(int(movement_id))