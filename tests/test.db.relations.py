import os
import sqlite3
from datetime import datetime

from database.connection import DatabaseManager
from database.schema import initialize_schema

from User import User
from category import Category
from customer import Customer
from medicine import Medicine
from prescription import Prescription
from prescription_item import PrescriptionItem
from sale import Sale
from sale_item import SaleItem
from payment import Payment
from inventory import Inventory

from repositories.user_repository import UserRepository
from repositories.category_repository import CategoryRepository
from repositories.customer_repository import CustomerRepository
from repositories.medicine_repository import MedicineRepository
from repositories.prescription_repository import PrescriptionRepository
from repositories.sales_repository import SaleRepository
from repositories.payment_repository import PaymentRepository
from repositories.inventory_repository import InventoryRepository
from repositories.invoice_repository import InvoiceRepository

from services.sales_service import SalesService
from services.report_service import ReportService


TEST_DB = "full_db_test_pharmacy.db"


passed_count = 0
failed_count = 0


def ok(name, detail=""):
    global passed_count
    passed_count += 1
    print(f"PASSED: {name}")
    if detail:
        print(f"        {detail}")


def fail(name, detail=""):
    global failed_count
    failed_count += 1
    print(f"FAILED: {name}")
    if detail:
        print(f"        {detail}")


def check(name, condition, detail=""):
    if condition:
        ok(name, detail)
    else:
        fail(name, detail)


def expect_error(name, func):
    try:
        func()
        fail(name, "Hata bekleniyordu ama hata vermedi.")
    except Exception as e:
        ok(name, f"Beklenen hata yakalandı: {type(e).__name__}: {e}")


def reset_db():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

    db = DatabaseManager(TEST_DB)
    initialize_schema(db)
    return db


def fetch_one(db, query, params=()):
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()


def fetch_all(db, query, params=()):
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()


def count_rows(db, table, where="", params=()):
    query = f"SELECT COUNT(*) AS count FROM {table}"
    if where:
        query += f" WHERE {where}"

    row = fetch_one(db, query, params)
    return row["count"]


def table_exists(db, table_name):
    row = fetch_one(
        db,
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,)
    )
    return row is not None


def column_exists(db, table_name, column_name):
    rows = fetch_all(db, f"PRAGMA table_info({table_name})")
    return column_name in [row["name"] for row in rows]


def make_repos(db):
    user_repo = UserRepository(db)
    category_repo = CategoryRepository(db)
    customer_repo = CustomerRepository(db)
    medicine_repo = MedicineRepository(db)
    prescription_repo = PrescriptionRepository(db)
    sale_repo = SaleRepository(db)
    payment_repo = PaymentRepository(db)
    inventory_repo = InventoryRepository(db)
    invoice_repo = InvoiceRepository(db)

    sales_service = SalesService(
        medicine_repo,
        sale_repo,
        prescription_repo,
        payment_repo,
        inventory_repo,
        invoice_repo
    )

    report_service = ReportService(db)

    return {
        "user": user_repo,
        "category": category_repo,
        "customer": customer_repo,
        "medicine": medicine_repo,
        "prescription": prescription_repo,
        "sale": sale_repo,
        "payment": payment_repo,
        "inventory": inventory_repo,
        "invoice": invoice_repo,
        "sales_service": sales_service,
        "report_service": report_service
    }


def test_schema(db):
    print("\n--- 1) SCHEMA TESTS ---")

    tables = [
        "roles",
        "users",
        "categories",
        "customers",
        "medicines",
        "prescriptions",
        "prescription_items",
        "sales",
        "sale_items",
        "payments",
        "inventory",
        "invoices"
    ]

    for table in tables:
        check(f"{table} table exists", table_exists(db, table))

    important_columns = [
        ("users", "role_id"),
        ("medicines", "category_id"),
        ("medicines", "requires_prescription"),
        ("prescriptions", "customer_id"),
        ("prescription_items", "prescription_id"),
        ("prescription_items", "medicine_id"),
        ("sales", "customer_id"),
        ("sales", "prescription_id"),
        ("sale_items", "sale_id"),
        ("sale_items", "medicine_id"),
        ("payments", "sale_id"),
        ("inventory", "medicine_id"),
        ("inventory", "sale_id"),
        ("invoices", "sale_id"),
    ]

    for table, column in important_columns:
        check(f"{table}.{column} exists", column_exists(db, table, column))

    check("default roles seeded", count_rows(db, "roles") >= 3)
    check("default categories seeded", count_rows(db, "categories") >= 3)
    check("default admin user seeded", count_rows(db, "users", "username = ?", ("admin",)) == 1)


def test_user_category_customer_crud(repos):
    print("\n--- 2) USER / CATEGORY / CUSTOMER CRUD TESTS ---")

    user_repo = repos["user"]
    category_repo = repos["category"]
    customer_repo = repos["customer"]

    admin = user_repo.login("admin", "123456")
    check("admin login works", admin is not None and admin.username == "admin")

    wrong_login = user_repo.login("admin", "wrong-password")
    check("wrong password blocked", wrong_login is None)

    user = User(None, "Test Cashier", "cashier_test", "123456", 3)
    user_repo.add(user)
    check("user add/get", user_repo.get_by_id(user.id).username == "cashier_test")

    loaded_by_username = user_repo.get_by_username("cashier_test")
    check("user get_by_username", loaded_by_username is not None and loaded_by_username.id == user.id)

    user.full_name = "Updated Cashier"
    user_repo.update(user.id, user)
    check("user update", user_repo.get_by_id(user.id).full_name == "Updated Cashier")

    category = Category(None, "Test Category")
    category_repo.add(category)
    check("category add/get", category_repo.get_by_id(category.id).name == "Test Category")

    category.rename("Updated Category")
    category_repo.update(category.id, category)
    check("category update", category_repo.get_by_id(category.id).name == "Updated Category")

    customer = Customer(None, "Test Customer", "05551234567")
    customer_repo.add(customer)
    check("customer add/get", customer_repo.get_by_id(customer.id).full_name == "Test Customer")

    customer.update_contact("05559876543")
    customer_repo.update(customer.id, customer)
    check("customer update phone", customer_repo.get_by_id(customer.id).phone == "05559876543")

    removed_customer = customer_repo.remove_by_id(customer.id)
    check("customer delete", removed_customer.id == customer.id and customer_repo.get_by_id(customer.id) is None)


def test_model_validations():
    print("\n--- 3) MODEL VALIDATION TESTS ---")

    expect_error("empty category blocked", lambda: Category(None, ""))
    expect_error("short category blocked", lambda: Category(None, "A"))
    expect_error("empty customer name blocked", lambda: Customer(None, "", "05551234567"))
    expect_error("invalid customer phone blocked", lambda: Customer(None, "Ali", "abc"))
    expect_error("empty medicine name blocked", lambda: Medicine(None, "", 1, 10, 5, "2030-01-01", False))
    expect_error("negative medicine stock blocked", lambda: Medicine(None, "X", 1, 10, -1, "2030-01-01", False))
    expect_error("zero medicine price blocked", lambda: Medicine(None, "X", 1, 0, 5, "2030-01-01", False))
    expect_error("wrong medicine expiry date blocked", lambda: Medicine(None, "X", 1, 10, 5, "01-01-2030", False))
    expect_error("invalid payment method blocked", lambda: Payment(None, 1, 100, "BITCOIN"))
    expect_error("zero payment blocked", lambda: Payment(None, 1, 0, "CASH"))
    expect_error("zero inventory movement blocked", lambda: Inventory(None, 1, 0, "IN"))
    expect_error("invalid inventory action blocked", lambda: Inventory(None, 1, 5, "SELL"))
    expect_error("invalid sale item quantity blocked", lambda: SaleItem(None, 1, 1, 0, 10))


def seed_main_data(repos):
    category_repo = repos["category"]
    customer_repo = repos["customer"]
    medicine_repo = repos["medicine"]

    category = Category(None, "DB Test Category")
    category_repo.add(category)

    customer = Customer(None, "Prescription Customer", "05550001122")
    customer_repo.add(customer)

    normal_medicine = Medicine(
        None,
        "DB Test Parol",
        category.id,
        50,
        20,
        "2030-12-31",
        False
    )
    medicine_repo.add(normal_medicine)

    prescription_medicine = Medicine(
        None,
        "DB Test Antibiotic",
        category.id,
        120,
        15,
        "2030-12-31",
        True
    )
    medicine_repo.add(prescription_medicine)

    expired_medicine = Medicine(
        None,
        "DB Test Expired",
        category.id,
        30,
        10,
        "2000-01-01",
        False
    )
    medicine_repo.add(expired_medicine)

    return category, customer, normal_medicine, prescription_medicine, expired_medicine


def test_medicine_repository(repos, normal_medicine):
    print("\n--- 4) MEDICINE REPOSITORY TESTS ---")

    medicine_repo = repos["medicine"]

    loaded = medicine_repo.get_by_id(normal_medicine.id)
    check("medicine add/get", loaded is not None and loaded.name == "DB Test Parol")

    loaded.update_price(55)
    loaded.add_stock(5)
    medicine_repo.update(loaded.id, loaded)

    updated = medicine_repo.get_by_id(loaded.id)
    check("medicine update price", updated.unit_price == 55)
    check("medicine update stock add", updated.stock == 25)

    results = medicine_repo.search_by_name("Parol")
    check("medicine search_by_name", any(m.id == normal_medicine.id for m in results))

    check("medicine is_available true", updated.is_available(3) is True)

    expect_error("medicine reduce_stock over stock blocked", lambda: updated.reduce_stock(9999))


def test_prescription_repository(repos, customer, prescription_medicine):
    print("\n--- 5) PRESCRIPTION TESTS ---")

    prescription_repo = repos["prescription"]

    prescription = Prescription(None, customer.id, "Dr. Database")
    prescription_repo.add(prescription)

    item = PrescriptionItem(None, prescription.id, prescription_medicine.id, 3)
    prescription.add_item(item)
    prescription_repo.update(prescription.id, prescription)

    loaded = prescription_repo.get_by_id(prescription.id)

    check("prescription add/get", loaded is not None and loaded.customer_id == customer.id)
    check("prescription item saved", len(loaded.items) == 1)
    check("prescription has medicine", loaded.has_medicine(prescription_medicine.id) is True)
    check("prescription allows valid quantity", loaded.allows_quantity(prescription_medicine.id, 2) is True)
    check("prescription blocks excess quantity", loaded.allows_quantity(prescription_medicine.id, 10) is False)

    return loaded


def test_normal_sale_flow(db, repos, normal_medicine):
    print("\n--- 6) NORMAL SALE / PAYMENT / INVOICE / INVENTORY TESTS ---")

    medicine_repo = repos["medicine"]
    sale_repo = repos["sale"]
    payment_repo = repos["payment"]
    invoice_repo = repos["invoice"]
    sales_service = repos["sales_service"]

    before_stock = medicine_repo.get_by_id(normal_medicine.id).stock

    cart = []
    cart = sales_service.add_to_cart(cart, medicine_repo.get_by_id(normal_medicine.id), 2, None)

    invoice = sales_service.complete_sale(cart, 110, "CASH", "Test Cashier")

    check("invoice object returned", invoice is not None and invoice.sale_id is not None)

    sale = sale_repo.get_by_id(invoice.sale_id)
    check("sale saved", sale is not None)
    check("sale completed", sale.is_completed is True)
    check("sale total correct", sale.total_amount == 110)
    check("sale item saved", len(sale.items) == 1)
    check("sale item quantity correct", sale.items[0].quantity == 2)

    payments = payment_repo.get_by_sale_id(sale.id)
    check("payment saved for sale", len(payments) == 1)
    check("payment amount correct", payments[0].amount == 110)
    check("payment method correct", payments[0].method == "CASH")

    saved_invoice = invoice_repo.get_by_sale_id(sale.id)
    check("invoice saved for sale", saved_invoice is not None)
    check("invoice total correct", saved_invoice.total_amount == 110)
    check("invoice number correct", saved_invoice.invoice_number == f"INV-{sale.id}")

    after_stock = medicine_repo.get_by_id(normal_medicine.id).stock
    check("stock decreased after sale", after_stock == before_stock - 2)

    if column_exists(db, "inventory", "sale_id"):
        movement_count = count_rows(
            db,
            "inventory",
            "sale_id = ? AND medicine_id = ? AND quantity_change = ? AND action_type = ?",
            (sale.id, normal_medicine.id, -2, "OUT")
        )
        check("inventory OUT movement connected to sale", movement_count == 1)
    else:
        fail("inventory OUT movement connected to sale", "inventory.sale_id kolonu yok.")

    return sale


def test_prescription_sale_flow(db, repos, customer, prescription_medicine, prescription):
    print("\n--- 7) PRESCRIPTION SALE TESTS ---")

    medicine_repo = repos["medicine"]
    sale_repo = repos["sale"]
    sales_service = repos["sales_service"]

    before_stock = medicine_repo.get_by_id(prescription_medicine.id).stock

    cart = []
    cart = sales_service.add_to_cart(
        cart,
        medicine_repo.get_by_id(prescription_medicine.id),
        1,
        prescription.id
    )

    invoice = sales_service.complete_sale(cart, 120, "CASH", "Prescription Cashier")
    sale = sale_repo.get_by_id(invoice.sale_id)

    check("prescription sale saved", sale is not None)
    check("sale prescription_id connected", sale.prescription_id == prescription.id)
    check("sale customer_id taken from prescription", sale.customer_id == customer.id)

    after_stock = medicine_repo.get_by_id(prescription_medicine.id).stock
    check("prescription medicine stock decreased", after_stock == before_stock - 1)

    if column_exists(db, "inventory", "sale_id"):
        movement_count = count_rows(
            db,
            "inventory",
            "sale_id = ? AND medicine_id = ? AND quantity_change = ?",
            (sale.id, prescription_medicine.id, -1)
        )
        check("prescription sale inventory connected", movement_count == 1)


def test_manual_sale_repository(repos, normal_medicine):
    print("\n--- 8) MANUAL SALE REPOSITORY TESTS ---")

    sale_repo = repos["sale"]

    sale = Sale(None)
    sale_repo.add(sale)

    item = SaleItem(None, sale.id, normal_medicine.id, 1, 50)
    sale.add_item(item)
    sale.complete_sale()
    sale_repo.update(sale.id, sale)

    loaded = sale_repo.get_by_id(sale.id)

    check("manual sale saved", loaded is not None)
    check("manual sale item saved", len(loaded.items) == 1)
    check("manual sale total correct", loaded.total_amount == 50)

    removed = sale_repo.remove_by_id(sale.id)
    check("manual sale remove", removed is not None and sale_repo.get_by_id(sale.id) is None)


def test_foreign_key_constraints(db):
    print("\n--- 9) FOREIGN KEY CONSTRAINT TESTS ---")

    expect_error(
        "medicine invalid category FK blocked",
        lambda: fetch_one(
            db,
            "INSERT INTO medicines(name, category_id, unit_price, stock, expiry_date, requires_prescription) VALUES (?, ?, ?, ?, ?, ?)",
            ("Bad FK Medicine", 999999, 10, 5, "2030-01-01", 0)
        )
    )

    def insert_bad_sale_item():
        with db.get_connection() as conn:
            conn.execute(
                "INSERT INTO sale_items(sale_id, medicine_id, quantity, unit_price, subtotal) VALUES (?, ?, ?, ?, ?)",
                (999999, 999999, 1, 10, 10)
            )

    expect_error("sale_item invalid FK blocked", insert_bad_sale_item)

    def insert_bad_payment():
        with db.get_connection() as conn:
            conn.execute(
                "INSERT INTO payments(sale_id, amount, method) VALUES (?, ?, ?)",
                (999999, 10, "CASH")
            )

    expect_error("payment invalid sale FK blocked", insert_bad_payment)

    if table_exists(db, "invoices"):
        def insert_bad_invoice():
            with db.get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO invoices(
                        sale_id, invoice_number, customer_name, cashier_name,
                        total_amount, paid_amount, change_amount, payment_method, issued_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (999999, "BAD-INV", "Bad", "Bad", 10, 10, 0, "CASH", "2030-01-01 10:00:00")
                )

        expect_error("invoice invalid sale FK blocked", insert_bad_invoice)


def test_negative_sale_cases(repos, normal_medicine, prescription_medicine, expired_medicine, prescription):
    print("\n--- 10) NEGATIVE SALE CASES ---")

    medicine_repo = repos["medicine"]
    sales_service = repos["sales_service"]

    expect_error(
        "empty sale blocked",
        lambda: sales_service.complete_sale([], 100, "CASH", "Cashier")
    )

    expect_error(
        "insufficient stock blocked",
        lambda: sales_service.add_to_cart([], medicine_repo.get_by_id(normal_medicine.id), 99999, None)
    )

    expect_error(
        "expired medicine blocked",
        lambda: sales_service.add_to_cart([], medicine_repo.get_by_id(expired_medicine.id), 1, None)
    )

    expect_error(
        "prescription medicine without prescription blocked",
        lambda: sales_service.add_to_cart([], medicine_repo.get_by_id(prescription_medicine.id), 1, None)
    )

    expect_error(
        "prescription medicine excess quantity blocked",
        lambda: sales_service.add_to_cart([], medicine_repo.get_by_id(prescription_medicine.id), 999, prescription.id)
    )

    expect_error(
        "cash underpayment blocked",
        lambda: sales_service.complete_sale(
            sales_service.add_to_cart([], medicine_repo.get_by_id(normal_medicine.id), 1, None),
            1,
            "CASH",
            "Cashier"
        )
    )


def test_card_transfer_payment(repos, normal_medicine):
    print("\n--- 11) CARD / TRANSFER PAYMENT TESTS ---")

    medicine_repo = repos["medicine"]
    payment_repo = repos["payment"]
    sales_service = repos["sales_service"]

    cart = sales_service.add_to_cart([], medicine_repo.get_by_id(normal_medicine.id), 1, None)
    invoice = sales_service.complete_sale(cart, 0, "CARD", "Card Cashier")
    payments = payment_repo.get_by_sale_id(invoice.sale_id)

    check("CARD payment auto-paid total", len(payments) == 1 and payments[0].amount == invoice.total_amount)
    check("CARD payment change zero", invoice.change_amount == 0)

    cart = sales_service.add_to_cart([], medicine_repo.get_by_id(normal_medicine.id), 1, None)
    invoice = sales_service.complete_sale(cart, 0, "TRANSFER", "Transfer Cashier")
    payments = payment_repo.get_by_sale_id(invoice.sale_id)

    check("TRANSFER payment auto-paid total", len(payments) == 1 and payments[0].amount == invoice.total_amount)
    check("TRANSFER payment change zero", invoice.change_amount == 0)


def test_reports(repos):
    print("\n--- 12) REPORT TESTS ---")

    report_service = repos["report_service"]
    today = datetime.now().strftime("%Y-%m-%d")
    month = datetime.now().strftime("%Y-%m")

    daily_total = report_service.get_daily_total_sales(today)
    monthly_total = report_service.get_monthly_total_sales(month)
    daily_count = report_service.get_sales_count_by_date(today)
    top_medicines = report_service.get_top_selling_medicines(5)

    check("daily total sales works", daily_total > 0)
    check("monthly total sales works", monthly_total >= daily_total)
    check("daily sales count works", daily_count > 0)
    check("top selling medicines works", len(top_medicines) > 0)

    expect_error("top selling limit zero blocked", lambda: report_service.get_top_selling_medicines(0))


def test_orphan_records(db):
    print("\n--- 13) ORPHAN RECORD CHECKS ---")

    orphan_queries = [
        (
            "users.role_id orphan",
            """
            SELECT COUNT(*) AS count
            FROM users u
            LEFT JOIN roles r ON r.id = u.role_id
            WHERE r.id IS NULL
            """
        ),
        (
            "medicines.category_id orphan",
            """
            SELECT COUNT(*) AS count
            FROM medicines m
            LEFT JOIN categories c ON c.id = m.category_id
            WHERE m.category_id IS NOT NULL AND c.id IS NULL
            """
        ),
        (
            "prescriptions.customer_id orphan",
            """
            SELECT COUNT(*) AS count
            FROM prescriptions p
            LEFT JOIN customers c ON c.id = p.customer_id
            WHERE c.id IS NULL
            """
        ),
        (
            "prescription_items.prescription_id orphan",
            """
            SELECT COUNT(*) AS count
            FROM prescription_items pi
            LEFT JOIN prescriptions p ON p.id = pi.prescription_id
            WHERE p.id IS NULL
            """
        ),
        (
            "prescription_items.medicine_id orphan",
            """
            SELECT COUNT(*) AS count
            FROM prescription_items pi
            LEFT JOIN medicines m ON m.id = pi.medicine_id
            WHERE m.id IS NULL
            """
        ),
        (
            "sales.customer_id orphan",
            """
            SELECT COUNT(*) AS count
            FROM sales s
            LEFT JOIN customers c ON c.id = s.customer_id
            WHERE s.customer_id IS NOT NULL AND c.id IS NULL
            """
        ),
        (
            "sales.prescription_id orphan",
            """
            SELECT COUNT(*) AS count
            FROM sales s
            LEFT JOIN prescriptions p ON p.id = s.prescription_id
            WHERE s.prescription_id IS NOT NULL AND p.id IS NULL
            """
        ),
        (
            "sale_items.sale_id orphan",
            """
            SELECT COUNT(*) AS count
            FROM sale_items si
            LEFT JOIN sales s ON s.id = si.sale_id
            WHERE s.id IS NULL
            """
        ),
        (
            "sale_items.medicine_id orphan",
            """
            SELECT COUNT(*) AS count
            FROM sale_items si
            LEFT JOIN medicines m ON m.id = si.medicine_id
            WHERE m.id IS NULL
            """
        ),
        (
            "payments.sale_id orphan",
            """
            SELECT COUNT(*) AS count
            FROM payments p
            LEFT JOIN sales s ON s.id = p.sale_id
            WHERE s.id IS NULL
            """
        ),
        (
            "inventory.medicine_id orphan",
            """
            SELECT COUNT(*) AS count
            FROM inventory i
            LEFT JOIN medicines m ON m.id = i.medicine_id
            WHERE m.id IS NULL
            """
        ),
        (
            "invoices.sale_id orphan",
            """
            SELECT COUNT(*) AS count
            FROM invoices i
            LEFT JOIN sales s ON s.id = i.sale_id
            WHERE s.id IS NULL
            """
        ),
    ]

    if column_exists(db, "inventory", "sale_id"):
        orphan_queries.append(
            (
                "inventory.sale_id orphan",
                """
                SELECT COUNT(*) AS count
                FROM inventory i
                LEFT JOIN sales s ON s.id = i.sale_id
                WHERE i.sale_id IS NOT NULL AND s.id IS NULL
                """
            )
        )

    for name, query in orphan_queries:
        row = fetch_one(db, query)
        check(name, row["count"] == 0, f"orphan count: {row['count']}")


def test_delete_behaviors(repos, normal_medicine):
    print("\n--- 14) DELETE BEHAVIOR TESTS ---")

    category_repo = repos["category"]
    customer_repo = repos["customer"]
    sale_repo = repos["sale"]

    temp_category = Category(None, "Delete Test Category")
    category_repo.add(temp_category)
    removed_category = category_repo.remove_by_id(temp_category.id)
    check("category delete", removed_category.id == temp_category.id and category_repo.get_by_id(temp_category.id) is None)

    temp_customer = Customer(None, "Delete Test Customer", "05551112233")
    customer_repo.add(temp_customer)
    removed_customer = customer_repo.remove_by_id(temp_customer.id)
    check("customer delete again", removed_customer.id == temp_customer.id and customer_repo.get_by_id(temp_customer.id) is None)

    sale = Sale(None)
    sale_repo.add(sale)
    sale.add_item(SaleItem(None, sale.id, normal_medicine.id, 1, 50))
    sale.complete_sale()
    sale_repo.update(sale.id, sale)

    removed_sale = sale_repo.remove_by_id(sale.id)
    check("sale delete", removed_sale is not None and sale_repo.get_by_id(sale.id) is None)


def run_all():
    print("\n===================================")
    print("FULL DB TESTS STARTED")
    print("===================================")

    db = reset_db()
    repos = make_repos(db)

    test_schema(db)
    test_user_category_customer_crud(repos)
    test_model_validations()

    category, customer, normal_medicine, prescription_medicine, expired_medicine = seed_main_data(repos)

    test_medicine_repository(repos, normal_medicine)
    prescription = test_prescription_repository(repos, customer, prescription_medicine)

    test_normal_sale_flow(db, repos, normal_medicine)
    test_prescription_sale_flow(db, repos, customer, prescription_medicine, prescription)
    test_manual_sale_repository(repos, normal_medicine)

    test_foreign_key_constraints(db)
    test_negative_sale_cases(repos, normal_medicine, prescription_medicine, expired_medicine, prescription)
    test_card_transfer_payment(repos, normal_medicine)
    test_reports(repos)
    test_orphan_records(db)
    test_delete_behaviors(repos, normal_medicine)

    print("\n===================================")
    print("FULL DB TESTS FINISHED")
    print("===================================")
    print(f"PASSED: {passed_count}")
    print(f"FAILED: {failed_count}")
    print(f"Test database: {TEST_DB}")

    if failed_count == 0:
        print("RESULT: DB tarafı genel olarak sağlam görünüyor.")
    else:
        print("RESULT: Bazı DB testleri fail verdi, yukarıdaki FAILED satırlarına bak.")


if __name__ == "__main__":
    run_all()