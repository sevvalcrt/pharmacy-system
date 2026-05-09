from prescription import Prescription
from prescription_item import PrescriptionItem

from repositories.prescription_repository import PrescriptionRepository
from repositories.medicine_repository import MedicineRepository
from repositories.customer_repository import CustomerRepository


class PrescriptionService:
    def __init__(self, db):
        self.prescription_repo = PrescriptionRepository(db)
        self.medicine_repo = MedicineRepository(db)
        self.customer_repo = CustomerRepository(db)

    def get_customers(self):
        return self.customer_repo.get_all()

    def get_medicines(self):
        return self.medicine_repo.get_all()

    def get_prescriptions(self):
        return self.prescription_repo.get_all()

    def get_prescription_by_id(self, prescription_id):
        return self.prescription_repo.get_by_id(prescription_id)

    def create_prescription(self, customer_id, doctor_name):
        prescription = Prescription(None, customer_id, doctor_name)
        self.prescription_repo.add(prescription)

    def add_medicine_to_prescription(self, prescription_id, medicine_id, quantity):
        prescription = self.prescription_repo.get_by_id(prescription_id)

        if prescription is None:
            raise Exception("Prescription not found.")

        item = PrescriptionItem(None, prescription_id, medicine_id, quantity)
        prescription.add_item(item)

        self.prescription_repo.update(prescription_id, prescription)

    def delete_prescription(self, prescription_id):
        self.prescription_repo.remove_by_id(prescription_id)