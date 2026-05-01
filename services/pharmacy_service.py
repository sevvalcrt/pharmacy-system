from repositories.medicine_repository import MedicineRepository
from repositories.sales_repository import SalesRepository


class PharmacyService:
    def __init__(
        self, medicine_repository: MedicineRepository, sales_repository: SalesRepository
    ) -> None:
        self.medicine_repository = medicine_repository
        self.sales_repository = sales_repository

    def add_medicine(
        self, name: str, unit_price: float, stock: int, expiry_date: str | None
    ) -> None:
        if unit_price <= 0:
            raise ValueError("Fiyat 0'dan buyuk olmali.")
        if stock < 0:
            raise ValueError("Stok negatif olamaz.")
        self.medicine_repository.add_medicine(name, unit_price, stock, expiry_date)

    def sell_medicine(self, medicine_id: int, quantity: int) -> int:
        medicine = self.medicine_repository.get_by_id(medicine_id)
        if medicine is None:
            raise ValueError("Ilac bulunamadi.")
        if quantity <= 0:
            raise ValueError("Miktar 0'dan buyuk olmali.")

        _, _, unit_price, _ = medicine
        self.medicine_repository.decrease_stock(medicine_id, quantity)
        return self.sales_repository.create_sale(medicine_id, quantity, unit_price)
