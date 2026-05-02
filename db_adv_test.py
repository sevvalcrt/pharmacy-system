"""
Advanced Database Test - Pharmacy System

Bu dosyayı proje ana klasörüne koy ve çalıştır:
    python advanced_database_test.py

Kontrol eder:
- Duplicate kayıtlar
- Olmayan ID / foreign key hataları
- Child kayıtlı parent silme senaryoları
- Sale / prescription item silme sırası
- Model validation kontrolleri
- Repository kritik metot kontrolleri

Not: Bu test kendi oluşturduğu 'ADV Test...' verilerini sonunda temizler.
"""

import os
import sys
import sqlite3
from datetime import datetime

# Dosya proje kökünde çalıştırılırsa importlar direkt çalışır.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.connection import DatabaseManager
from database.schema import initialize_schema


TOTAL = 0
PASSED = 0
FAILED = 0
WARNINGS = 0


def title(text):
    print("\n" + "=" * 14 + f" {text} " + "=" * 14)


def ok(message):
    global TOTAL, PASSED
    TOTAL += 1
    PASSED += 1
    print(f"PASS  - {message}")


def fail(message, error=None):
    global TOTAL, FAILED
    TOTAL += 1
    FAILED += 1
    print(f"FAIL  - {message}")
    if error:
        print(f"        Hata: {type(error).__name__}: {error}")


def warn(message):
    global TOTAL, WARNINGS
    TOTAL += 1
    WARNINGS += 1
    print(f"WARN  - {message}")


def expect_success(message, func):
    try:
        func()
        ok(message)
    except Exception as exc:
        fail(message, exc)


def expect_error(message, func, expected_exception=Exception):
    try:
        func()
        fail(message + " | Hata bekleniyordu ama hata gelmedi")
    except expected_exception:
        ok(message)
    except Exception as exc:
        fail(message + " | Yanlış hata tipi geldi", exc)


def fetch_one(cursor, sql, params=()):
    cursor.execute(sql, params)
    return cursor.fetchone()


def cleanup(cursor):
    """Önce child tabloları temizliyoruz ki foreign key hatası olmasın."""
    cursor.execute("""
        DELETE FROM sale_items
        WHERE sale_id IN (
            SELECT id FROM sales
            WHERE customer_id IN (SELECT id FROM customers WHERE full_name LIKE 'ADV Test%')
        )
        OR medicine_id IN (SELECT id FROM medicines WHERE name LIKE 'ADV Test%')
    """)
    cursor.execute("""
        DELETE FROM sales
        WHERE customer_id IN (SELECT id FROM customers WHERE full_name LIKE 'ADV Test%')
        OR prescription_id IN (SELECT id FROM prescriptions WHERE doctor_name LIKE 'ADV Test%')
    """)
    cursor.execute("""
        DELETE FROM prescription_items
        WHERE prescription_id IN (SELECT id FROM prescriptions WHERE doctor_name LIKE 'ADV Test%')
        OR medicine_id IN (SELECT id FROM medicines WHERE name LIKE 'ADV Test%')
    """)
    cursor.execute("DELETE FROM prescriptions WHERE doctor_name LIKE 'ADV Test%'")
    cursor.execute("DELETE FROM medicines WHERE name LIKE 'ADV Test%'")
    cursor.execute("DELETE FROM customers WHERE full_name LIKE 'ADV Test%'")
    cursor.execute("DELETE FROM users WHERE username LIKE 'adv_test_%'")
    cursor.execute("DELETE FROM categories WHERE name LIKE 'ADV Test%'")
    cursor.execute("DELETE FROM roles WHERE name LIKE 'adv_test_%'")


def create_base_data(cursor):
    cursor.execute("INSERT INTO categories(name) VALUES (?)", ("ADV Test Category",))
    category_id = cursor.lastrowid

    cursor.execute("INSERT INTO customers(full_name, phone) VALUES (?, ?)", ("ADV Test Customer", "05551234567"))
    customer_id = cursor.lastrowid

    cursor.execute(
        """
        INSERT INTO medicines(name, category_id, unit_price, stock, expiry_date, requires_prescription)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("ADV Test Medicine", category_id, 50.0, 20, "2028-12-31", 0),
    )
    medicine_id = cursor.lastrowid

    return category_id, customer_id, medicine_id


def test_duplicate_constraints(cursor):
    title("DUPLICATE / UNIQUE KONTROLÜ")

    cursor.execute("INSERT INTO roles(name) VALUES (?)", ("adv_test_role",))
    expect_error(
        "Aynı role name ikinci kez eklenemiyor",
        lambda: cursor.execute("INSERT INTO roles(name) VALUES (?)", ("adv_test_role",)),
        sqlite3.IntegrityError,
    )

    cursor.execute("INSERT INTO categories(name) VALUES (?)", ("ADV Test Duplicate Category",))
    expect_error(
        "Aynı category name ikinci kez eklenemiyor",
        lambda: cursor.execute("INSERT INTO categories(name) VALUES (?)", ("ADV Test Duplicate Category",)),
        sqlite3.IntegrityError,
    )

    cursor.execute(
        "INSERT INTO users(full_name, username, password, role_id) VALUES (?, ?, ?, ?)",
        ("ADV Test User", "adv_test_user", "123456", 2),
    )
    expect_error(
        "Aynı username ikinci kez eklenemiyor",
        lambda: cursor.execute(
            "INSERT INTO users(full_name, username, password, role_id) VALUES (?, ?, ?, ?)",
            ("ADV Test User 2", "adv_test_user", "123456", 2),
        ),
        sqlite3.IntegrityError,
    )


def test_foreign_keys(cursor):
    title("FOREIGN KEY KONTROLÜ")

    expect_error(
        "Olmayan role_id ile user eklenemiyor",
        lambda: cursor.execute(
            "INSERT INTO users(full_name, username, password, role_id) VALUES (?, ?, ?, ?)",
            ("ADV Test Bad User", "adv_test_bad_role", "123456", 999999),
        ),
        sqlite3.IntegrityError,
    )

    expect_error(
        "Olmayan category_id ile medicine eklenemiyor",
        lambda: cursor.execute(
            "INSERT INTO medicines(name, category_id, unit_price, stock, expiry_date, requires_prescription) VALUES (?, ?, ?, ?, ?, ?)",
            ("ADV Test Bad Medicine", 999999, 10.0, 5, "2028-01-01", 0),
        ),
        sqlite3.IntegrityError,
    )

    expect_error(
        "Olmayan customer_id ile prescription eklenemiyor",
        lambda: cursor.execute(
            "INSERT INTO prescriptions(customer_id, doctor_name, created_at) VALUES (?, ?, ?)",
            (999999, "ADV Test Bad Doctor", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        ),
        sqlite3.IntegrityError,
    )

    expect_error(
        "Olmayan sale_id ile sale_item eklenemiyor",
        lambda: cursor.execute(
            "INSERT INTO sale_items(sale_id, medicine_id, quantity, unit_price, subtotal) VALUES (?, ?, ?, ?, ?)",
            (999999, 1, 1, 10.0, 10.0),
        ),
        sqlite3.IntegrityError,
    )

    expect_error(
        "Olmayan prescription_id ile prescription_item eklenemiyor",
        lambda: cursor.execute(
            "INSERT INTO prescription_items(prescription_id, medicine_id, quantity) VALUES (?, ?, ?)",
            (999999, 1, 1),
        ),
        sqlite3.IntegrityError,
    )


def test_child_delete_rules(cursor):
    title("CHILD KAYITLI PARENT SİLME KONTROLÜ")

    category_id, customer_id, medicine_id = create_base_data(cursor)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Sale + sale_item oluştur
    cursor.execute(
        "INSERT INTO sales(customer_id, prescription_id, total_amount, sale_date, is_completed) VALUES (?, ?, ?, ?, ?)",
        (customer_id, None, 100.0, now, 1),
    )
    sale_id = cursor.lastrowid
    cursor.execute(
        "INSERT INTO sale_items(sale_id, medicine_id, quantity, unit_price, subtotal) VALUES (?, ?, ?, ?, ?)",
        (sale_id, medicine_id, 2, 50.0, 100.0),
    )

    expect_error(
        "İçinde sale_item olan sale direkt silinmiyor",
        lambda: cursor.execute("DELETE FROM sales WHERE id = ?", (sale_id,)),
        sqlite3.IntegrityError,
    )

    expect_error(
        "Satışta kullanılmış medicine direkt silinmiyor",
        lambda: cursor.execute("DELETE FROM medicines WHERE id = ?", (medicine_id,)),
        sqlite3.IntegrityError,
    )

    expect_success(
        "Önce sale_items sonra sales silinince çalışıyor",
        lambda: (
            cursor.execute("DELETE FROM sale_items WHERE sale_id = ?", (sale_id,)),
            cursor.execute("DELETE FROM sales WHERE id = ?", (sale_id,)),
        ),
    )

    # Prescription + prescription_item oluştur
    cursor.execute(
        "INSERT INTO prescriptions(customer_id, doctor_name, created_at) VALUES (?, ?, ?)",
        (customer_id, "ADV Test Doctor", now),
    )
    prescription_id = cursor.lastrowid
    cursor.execute(
        "INSERT INTO prescription_items(prescription_id, medicine_id, quantity) VALUES (?, ?, ?)",
        (prescription_id, medicine_id, 3),
    )

    expect_error(
        "İçinde prescription_item olan prescription direkt silinmiyor",
        lambda: cursor.execute("DELETE FROM prescriptions WHERE id = ?", (prescription_id,)),
        sqlite3.IntegrityError,
    )

    expect_success(
        "Önce prescription_items sonra prescriptions silinince çalışıyor",
        lambda: (
            cursor.execute("DELETE FROM prescription_items WHERE prescription_id = ?", (prescription_id,)),
            cursor.execute("DELETE FROM prescriptions WHERE id = ?", (prescription_id,)),
        ),
    )


def test_bad_data_constraints(cursor):
    title("BOZUK VERİ DB SEVİYESİ KONTROLÜ")

    # Bu kontrollerde ideal davranış: DB hata vermeli.
    # Senin schema'da CHECK constraint yoksa hata vermez; bunu WARN olarak yazdırıyoruz.
    try:
        cursor.execute(
            "INSERT INTO medicines(name, category_id, unit_price, stock, expiry_date, requires_prescription) VALUES (?, ?, ?, ?, ?, ?)",
            ("ADV Test Negative Stock", 1, 10.0, -5, "2028-01-01", 0),
        )
        warn("DB negatif stock kaydına izin verdi. Model class engelliyor olabilir ama schema CHECK yok.")
    except sqlite3.IntegrityError:
        ok("DB negatif stock kaydını engelledi")

    try:
        cursor.execute(
            "INSERT INTO medicines(name, category_id, unit_price, stock, expiry_date, requires_prescription) VALUES (?, ?, ?, ?, ?, ?)",
            ("ADV Test Negative Price", 1, -10.0, 5, "2028-01-01", 0),
        )
        warn("DB negatif price kaydına izin verdi. Model class engelliyor olabilir ama schema CHECK yok.")
    except sqlite3.IntegrityError:
        ok("DB negatif price kaydını engelledi")


def test_model_validations():
    title("MODEL VALIDATION KONTROLÜ")

    from User import User
    from medicine import Medicine
    from sale_item import SaleItem
    from prescription_item import PrescriptionItem

    expect_error(
        "User kısa password kabul etmiyor",
        lambda: User(None, "ADV Test User", "advmodel", "123", 2),
        ValueError,
    )

    expect_error(
        "Medicine negatif stock kabul etmiyor",
        lambda: Medicine(None, "ADV Test Model Medicine", 1, 10.0, -1, "2028-01-01", False),
        ValueError,
    )

    expect_error(
        "Medicine negatif price kabul etmiyor",
        lambda: Medicine(None, "ADV Test Model Medicine", 1, -10.0, 5, "2028-01-01", False),
        ValueError,
    )

    expect_error(
        "SaleItem quantity 0 kabul etmiyor",
        lambda: SaleItem(None, 1, 1, 0, 10.0),
        ValueError,
    )

    expect_error(
        "PrescriptionItem quantity 0 kabul etmiyor",
        lambda: PrescriptionItem(None, 1, 1, 0),
        ValueError,
    )


def test_repository_critical_methods(db):
    title("REPOSITORY KRİTİK METOT KONTROLÜ")

    from medicine import Medicine
    from sale import Sale
    from sale_item import SaleItem
    from prescription import Prescription
    from prescription_item import PrescriptionItem
    from repositories.medicine_repository import MedicineRepository
    from repositories.sales_repository import SaleRepository
    from repositories.prescription_repository import PrescriptionRepository

    med_repo = MedicineRepository(db)
    sale_repo = SaleRepository(db)
    prescription_repo = PrescriptionRepository(db)

    # Medicine repository search
    med = Medicine(None, "ADV Test Repo Medicine", 1, 20.0, 15, "2028-01-01", False)
    expect_success("MedicineRepository.add çalışıyor", lambda: med_repo.add(med))
    expect_success("MedicineRepository.get_by_id çalışıyor", lambda: med_repo.get_by_id(med.id))
    expect_success("MedicineRepository.search_by_name çalışıyor", lambda: med_repo.search_by_name("ADV Test Repo"))

    # SaleRepository'de _delete_sale_items var mı?
    if hasattr(sale_repo, "_delete_sale_items"):
        ok("SaleRepository içinde _delete_sale_items metodu var")
    else:
        fail("SaleRepository içinde _delete_sale_items metodu yok. update() bunu çağırdığı için hata verir.")

    # Sale remove_by_id child kayıtla çalışıyor mu?
    sale = Sale(None, customer_id=None, prescription_id=None)
    sale_repo.add(sale)
    item = SaleItem(None, sale.id, med.id, 1, 20.0)
    sale.items = [item]
    sale_repo.update(sale.id, sale) if hasattr(sale_repo, "_delete_sale_items") else None

    if hasattr(sale_repo, "_delete_sale_items"):
        expect_success("SaleRepository.remove_by_id child sale_items ile çalışıyor", lambda: sale_repo.remove_by_id(sale.id))
    else:
        warn("SaleRepository.remove_by_id tam test edilemedi çünkü _delete_sale_items eksik")

    # PrescriptionRepository remove_by_id child kayıtla çalışıyor mu?
    with db.get_connection() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO customers(full_name, phone) VALUES (?, ?)", ("ADV Test Repo Customer", "05550000000"))
        customer_id = cur.lastrowid

    prescription = Prescription(None, customer_id, "ADV Test Repo Doctor")
    prescription_repo.add(prescription)
    p_item = PrescriptionItem(None, prescription.id, med.id, 1)
    prescription.items = [p_item]
    prescription_repo.update(prescription.id, prescription)

    expect_success(
        "PrescriptionRepository.remove_by_id child prescription_items ile çalışmalı",
        lambda: prescription_repo.remove_by_id(prescription.id),
    )

    # Temizlik
    with db.get_connection() as conn:
        cur = conn.cursor()
        cleanup(cur)


def main():
    print("ADVANCED DATABASE TEST BAŞLADI")

    db = DatabaseManager()
    initialize_schema(db)
    print(f"DB path: {db.db_path}")

    with db.get_connection() as conn:
        cursor = conn.cursor()
        cleanup(cursor)

        test_duplicate_constraints(cursor)
        test_foreign_keys(cursor)
        test_child_delete_rules(cursor)
        test_bad_data_constraints(cursor)

    test_model_validations()

    # Repository testleri ayrı connection'larla çalışıyor.
    try:
        test_repository_critical_methods(db)
    except Exception as exc:
        fail("Repository testleri sırasında beklenmeyen genel hata oluştu", exc)

    with db.get_connection() as conn:
        cleanup(conn.cursor())

    title("ÖZET")
    print(f"Toplam kontrol: {TOTAL}")
    print(f"Başarılı:       {PASSED}")
    print(f"Uyarı:          {WARNINGS}")
    print(f"Hatalı:         {FAILED}")

    if FAILED == 0:
        print("\nSONUÇ: Database tarafı genel olarak iyi görünüyor. WARN varsa schema seviyesinde güçlendirme önerisi var.")
    else:
        print("\nSONUÇ: Düzeltilmesi gereken hata var. FAIL satırlarını kontrol et.")


if __name__ == "__main__":
    main()
