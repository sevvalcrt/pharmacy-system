from medicine import Medicine
from sale import Sale
from prescription import Prescription
from prescription_item import PrescriptionItem
from pharmacist import Pharmacist

from repositories.medicine_repository import MedicineRepository
from repositories.sales_repository import SaleRepository
from repositories.prescription_repository import PrescriptionRepository

from services.sales_service import SalesService


def main():
    # 🔹 Repositories
    medicine_repo = MedicineRepository()
    sale_repo = SaleRepository()
    prescription_repo = PrescriptionRepository()

    # 🔹 Pharmacist
    pharmacist = Pharmacist(1, "Ayşe", "ayse", "123456")

    # 🔹 Service
    sales_service = SalesService(
        medicine_repo,
        sale_repo,
        prescription_repo,
        pharmacist
    )

    # 🔹 Medicine oluştur
    med1 = Medicine(1, "Parol", 1, 50, 100, "2026-12-31", False)
    med2 = Medicine(2, "Antibiyotik", 1, 100, 50, "2026-12-31", True)

    medicine_repo.add(med1)
    medicine_repo.add(med2)

    # 🔹 Prescription oluştur
    prescription = Prescription(1, 1, "Dr. Ahmet")
    item = PrescriptionItem(1, prescription.id, med2.id, 2)
    prescription.add_item(item)

    prescription_repo.add(prescription)

    # 🔹 Sale oluştur
    sale = Sale(1, customer_id=1, prescription_id=1)

    # 🔹 Satış işlemleri
    sales_service.add_medicine_to_sale(sale, 1, 2)  # reçetesiz
    sales_service.add_medicine_to_sale(sale, 2, 2)  # reçeteli

    # 🔹 Satışı tamamla
    sales_service.complete_sale(sale)

    # 🔹 Sonuç
    print("=== SALE INFO ===")
    print(sale.display_info())

    print("\n=== MEDICINE STOCK ===")
    for med in medicine_repo.get_all():
        print(med.display_info())


if __name__ == "__main__":
    main()