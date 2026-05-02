from database.connection import DatabaseManager
from database.schema import initialize_schema
from datetime import datetime


def line(title):
    print('\n' + '=' * 12, title, '=' * 12)


def show_row(row):
    if row is None:
        return None
    return dict(row)


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)
    print('OK -', message)


def select_by_id(cursor, table, row_id):
    cursor.execute(f"SELECT * FROM {table} WHERE id = ?", (row_id,))
    return cursor.fetchone()


def clean_old_test_data(cursor):
    # Önce child tablolar, sonra parent tablolar silinir. Foreign key hatası olmasın diye bu sıra önemli.
    cursor.execute("DELETE FROM sale_items WHERE sale_id IN (SELECT id FROM sales WHERE customer_id IN (SELECT id FROM customers WHERE full_name LIKE 'CRUD Test%'))")
    cursor.execute("DELETE FROM sales WHERE customer_id IN (SELECT id FROM customers WHERE full_name LIKE 'CRUD Test%')")

    cursor.execute("DELETE FROM prescription_items WHERE prescription_id IN (SELECT id FROM prescriptions WHERE doctor_name LIKE 'CRUD Test%')")
    cursor.execute("DELETE FROM prescriptions WHERE doctor_name LIKE 'CRUD Test%'")

    cursor.execute("DELETE FROM medicines WHERE name LIKE 'CRUD Test%'")
    cursor.execute("DELETE FROM customers WHERE full_name LIKE 'CRUD Test%'")
    cursor.execute("DELETE FROM users WHERE username LIKE 'crud_test_%'")
    cursor.execute("DELETE FROM categories WHERE name LIKE 'CRUD Test%'")
    cursor.execute("DELETE FROM roles WHERE name LIKE 'crud_test_%'")


def test_roles(cursor):
    line('ROLES')
    cursor.execute("INSERT INTO roles(name) VALUES (?)", ('crud_test_role',))
    role_id = cursor.lastrowid
    assert_true(select_by_id(cursor, 'roles', role_id) is not None, 'role SAVE + SELECT çalıştı')

    cursor.execute("UPDATE roles SET name = ? WHERE id = ?", ('crud_test_role_updated', role_id))
    row = select_by_id(cursor, 'roles', role_id)
    print('SELECT:', show_row(row))
    assert_true(row['name'] == 'crud_test_role_updated', 'role UPDATE çalıştı')

    cursor.execute("DELETE FROM roles WHERE id = ?", (role_id,))
    assert_true(select_by_id(cursor, 'roles', role_id) is None, 'role DELETE çalıştı')


def test_categories(cursor):
    line('CATEGORIES')
    cursor.execute("INSERT INTO categories(name) VALUES (?)", ('CRUD Test Category',))
    category_id = cursor.lastrowid
    assert_true(select_by_id(cursor, 'categories', category_id) is not None, 'category SAVE + SELECT çalıştı')

    cursor.execute("UPDATE categories SET name = ? WHERE id = ?", ('CRUD Test Category Updated', category_id))
    row = select_by_id(cursor, 'categories', category_id)
    print('SELECT:', show_row(row))
    assert_true(row['name'] == 'CRUD Test Category Updated', 'category UPDATE çalıştı')

    cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    assert_true(select_by_id(cursor, 'categories', category_id) is None, 'category DELETE çalıştı')


def test_users(cursor):
    line('USERS')
    cursor.execute(
        "INSERT INTO users(full_name, username, password, role_id) VALUES (?, ?, ?, ?)",
        ('CRUD Test User', 'crud_test_user', '123456', 2)
    )
    user_id = cursor.lastrowid
    assert_true(select_by_id(cursor, 'users', user_id) is not None, 'user SAVE + SELECT çalıştı')

    cursor.execute("UPDATE users SET full_name = ?, password = ?, role_id = ? WHERE id = ?", ('CRUD Test User Updated', '654321', 3, user_id))
    row = select_by_id(cursor, 'users', user_id)
    print('SELECT:', show_row(row))
    assert_true(row['full_name'] == 'CRUD Test User Updated' and row['role_id'] == 3, 'user UPDATE çalıştı')

    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    assert_true(select_by_id(cursor, 'users', user_id) is None, 'user DELETE çalıştı')


def test_customers(cursor):
    line('CUSTOMERS')
    cursor.execute("INSERT INTO customers(full_name, phone) VALUES (?, ?)", ('CRUD Test Customer', '05551234567'))
    customer_id = cursor.lastrowid
    assert_true(select_by_id(cursor, 'customers', customer_id) is not None, 'customer SAVE + SELECT çalıştı')

    cursor.execute("UPDATE customers SET phone = ? WHERE id = ?", ('05557654321', customer_id))
    row = select_by_id(cursor, 'customers', customer_id)
    print('SELECT:', show_row(row))
    assert_true(row['phone'] == '05557654321', 'customer UPDATE çalıştı')

    cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
    assert_true(select_by_id(cursor, 'customers', customer_id) is None, 'customer DELETE çalıştı')


def test_medicines(cursor):
    line('MEDICINES')
    cursor.execute(
        "INSERT INTO medicines(name, category_id, unit_price, stock, expiry_date, requires_prescription) VALUES (?, ?, ?, ?, ?, ?)",
        ('CRUD Test Medicine', 1, 50.0, 100, '2027-12-31', 0)
    )
    medicine_id = cursor.lastrowid
    assert_true(select_by_id(cursor, 'medicines', medicine_id) is not None, 'medicine SAVE + SELECT çalıştı')

    cursor.execute("UPDATE medicines SET unit_price = ?, stock = ?, requires_prescription = ? WHERE id = ?", (75.5, 80, 1, medicine_id))
    row = select_by_id(cursor, 'medicines', medicine_id)
    print('SELECT:', show_row(row))
    assert_true(row['unit_price'] == 75.5 and row['stock'] == 80 and row['requires_prescription'] == 1, 'medicine UPDATE çalıştı')

    cursor.execute("DELETE FROM medicines WHERE id = ?", (medicine_id,))
    assert_true(select_by_id(cursor, 'medicines', medicine_id) is None, 'medicine DELETE çalıştı')


def test_prescriptions(cursor):
    line('PRESCRIPTIONS + PRESCRIPTION_ITEMS')
    cursor.execute("INSERT INTO customers(full_name, phone) VALUES (?, ?)", ('CRUD Test Prescription Customer', '05550000001'))
    customer_id = cursor.lastrowid

    cursor.execute(
        "INSERT INTO medicines(name, category_id, unit_price, stock, expiry_date, requires_prescription) VALUES (?, ?, ?, ?, ?, ?)",
        ('CRUD Test Prescription Medicine', 2, 120.0, 40, '2027-10-10', 1)
    )
    medicine_id = cursor.lastrowid

    cursor.execute(
        "INSERT INTO prescriptions(customer_id, doctor_name, created_at) VALUES (?, ?, ?)",
        (customer_id, 'CRUD Test Doctor', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    )
    prescription_id = cursor.lastrowid
    assert_true(select_by_id(cursor, 'prescriptions', prescription_id) is not None, 'prescription SAVE + SELECT çalıştı')

    cursor.execute(
        "INSERT INTO prescription_items(prescription_id, medicine_id, quantity) VALUES (?, ?, ?)",
        (prescription_id, medicine_id, 2)
    )
    item_id = cursor.lastrowid
    assert_true(select_by_id(cursor, 'prescription_items', item_id) is not None, 'prescription_item SAVE + SELECT çalıştı')

    cursor.execute("UPDATE prescriptions SET doctor_name = ? WHERE id = ?", ('CRUD Test Doctor Updated', prescription_id))
    cursor.execute("UPDATE prescription_items SET quantity = ? WHERE id = ?", (5, item_id))

    p_row = select_by_id(cursor, 'prescriptions', prescription_id)
    pi_row = select_by_id(cursor, 'prescription_items', item_id)
    print('PRESCRIPTION SELECT:', show_row(p_row))
    print('ITEM SELECT:', show_row(pi_row))
    assert_true(p_row['doctor_name'] == 'CRUD Test Doctor Updated', 'prescription UPDATE çalıştı')
    assert_true(pi_row['quantity'] == 5, 'prescription_item UPDATE çalıştı')

    cursor.execute("DELETE FROM prescription_items WHERE id = ?", (item_id,))
    assert_true(select_by_id(cursor, 'prescription_items', item_id) is None, 'prescription_item DELETE çalıştı')

    cursor.execute("DELETE FROM prescriptions WHERE id = ?", (prescription_id,))
    assert_true(select_by_id(cursor, 'prescriptions', prescription_id) is None, 'prescription DELETE çalıştı')

    cursor.execute("DELETE FROM medicines WHERE id = ?", (medicine_id,))
    cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))


def test_sales(cursor):
    line('SALES + SALE_ITEMS')
    cursor.execute("INSERT INTO customers(full_name, phone) VALUES (?, ?)", ('CRUD Test Sale Customer', '05550000002'))
    customer_id = cursor.lastrowid

    cursor.execute(
        "INSERT INTO medicines(name, category_id, unit_price, stock, expiry_date, requires_prescription) VALUES (?, ?, ?, ?, ?, ?)",
        ('CRUD Test Sale Medicine', 3, 30.0, 200, '2028-01-01', 0)
    )
    medicine_id = cursor.lastrowid

    cursor.execute(
        "INSERT INTO sales(customer_id, prescription_id, total_amount, sale_date, is_completed) VALUES (?, ?, ?, ?, ?)",
        (customer_id, None, 60.0, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 1)
    )
    sale_id = cursor.lastrowid
    assert_true(select_by_id(cursor, 'sales', sale_id) is not None, 'sale SAVE + SELECT çalıştı')

    cursor.execute(
        "INSERT INTO sale_items(sale_id, medicine_id, quantity, unit_price, subtotal) VALUES (?, ?, ?, ?, ?)",
        (sale_id, medicine_id, 2, 30.0, 60.0)
    )
    sale_item_id = cursor.lastrowid
    assert_true(select_by_id(cursor, 'sale_items', sale_item_id) is not None, 'sale_item SAVE + SELECT çalıştı')

    cursor.execute("UPDATE sales SET total_amount = ?, is_completed = ? WHERE id = ?", (90.0, 1, sale_id))
    cursor.execute("UPDATE sale_items SET quantity = ?, subtotal = ? WHERE id = ?", (3, 90.0, sale_item_id))

    s_row = select_by_id(cursor, 'sales', sale_id)
    si_row = select_by_id(cursor, 'sale_items', sale_item_id)
    print('SALE SELECT:', show_row(s_row))
    print('ITEM SELECT:', show_row(si_row))
    assert_true(s_row['total_amount'] == 90.0, 'sale UPDATE çalıştı')
    assert_true(si_row['quantity'] == 3 and si_row['subtotal'] == 90.0, 'sale_item UPDATE çalıştı')

    cursor.execute("DELETE FROM sale_items WHERE id = ?", (sale_item_id,))
    assert_true(select_by_id(cursor, 'sale_items', sale_item_id) is None, 'sale_item DELETE çalıştı')

    cursor.execute("DELETE FROM sales WHERE id = ?", (sale_id,))
    assert_true(select_by_id(cursor, 'sales', sale_id) is None, 'sale DELETE çalıştı')

    cursor.execute("DELETE FROM medicines WHERE id = ?", (medicine_id,))
    cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))


def main():
    db = DatabaseManager()
    initialize_schema(db)

    with db.get_connection() as conn:
        cursor = conn.cursor()
        clean_old_test_data(cursor)

        test_roles(cursor)
        test_categories(cursor)
        test_users(cursor)
        test_customers(cursor)
        test_medicines(cursor)
        test_prescriptions(cursor)
        test_sales(cursor)

    print('\n✅ TÜM DATABASE CRUD TESTLERİ BAŞARILI')
    print('SAVE / SELECT / UPDATE / DELETE işlemleri kontrol edildi.')


if __name__ == '__main__':
    main()
