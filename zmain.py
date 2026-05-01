from database.connection import DatabaseManager
from database.schema import initialize_schema

from User import User
from medicine import Medicine
from prescription import Prescription
from prescription_item import PrescriptionItem
from sale import Sale
from sale_item import SaleItem

from repositories.user_repository import UserRepository
from repositories.medicine_repository import MedicineRepository
from repositories.prescription_repository import PrescriptionRepository
from repositories.sales_repository import SaleRepository


def main():
    db = DatabaseManager()
    initialize_schema(db)

    user_repo = UserRepository(db)
    medicine_repo = MedicineRepository(db)
    prescription_repo = PrescriptionRepository(db)
    sale_repo = SaleRepository(db)

    print("Database bağlantısı başarılı.")

    # CUSTOMER yoksa prescription için elle customer ekliyoruz
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO customers(id, full_name, phone) VALUES (?, ?, ?)",
            (1, "Test Customer", "05551234567")
        )

    print("\n--- USER TEST ---")
    user = User(None, "Test User", "testuser", "123456", 2)
    user_repo.add(user)
    print("Eklendi:", user.display_info() if hasattr(user, "display_info") else user.username)

    user.full_name = "Updated Test User"
    user_repo.update(user.id, user)
    print("Güncellendi:", user_repo.get_by_id(user.id).full_name)

    deleted_user = user_repo.remove_by_id(user.id)
    print("Silindi:", deleted_user.username)

    print("\n--- MEDICINE TEST ---")
    medicine = Medicine(None, "Parol", 1, 50, 100, "2026-12-31", False)
    medicine_repo.add(medicine)
    print("Eklendi:", medicine.display_info())

    medicine.unit_price = 75
    medicine.stock = 80
    medicine_repo.update(medicine.id, medicine)
    print("Güncellendi:", medicine_repo.get_by_id(medicine.id).display_info())

    print("\n--- PRESCRIPTION TEST ---")
    prescription = Prescription(None, 1, "Dr. Ayşe")
    prescription_repo.add(prescription)
    print("Prescription eklendi:", prescription.display_info())

    item = PrescriptionItem(None, prescription.id, medicine.id, 2)
    prescription.add_item(item)
    prescription_repo.update(prescription.id, prescription)

    updated_prescription = prescription_repo.get_by_id(prescription.id)
    print("Prescription item eklendi:", updated_prescription.display_info())
    for item in updated_prescription.items:
        print(item.display_info())

    print("\n--- SALE TEST ---")
    sale = Sale(None, customer_id=1, prescription_id=prescription.id)
    sale_repo.add(sale)
    print("Sale eklendi:", sale.display_info())

    sale_item = SaleItem(None, sale.id, medicine.id, 2, medicine.unit_price)
    sale.add_item(sale_item)
    sale.complete_sale()
    sale_repo.update(sale.id, sale)

    updated_sale = sale_repo.get_by_id(sale.id)
    print("Sale güncellendi:", updated_sale.display_info())
    for item in updated_sale.items:
        print(item.display_info())

    print("\n--- DELETE TEST ---")
    deleted_sale = sale_repo.remove_by_id(sale.id)
    print("Sale silindi:", deleted_sale.id)

    deleted_prescription = prescription_repo.remove_by_id(prescription.id)
    print("Prescription silindi:", deleted_prescription.id)

    deleted_medicine = medicine_repo.remove_by_id(medicine.id)
    print("Medicine silindi:", deleted_medicine.name)

    print("\nTüm mevcut repository CRUD testleri başarılı.")


if __name__ == "__main__":
    main()