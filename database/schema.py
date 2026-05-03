from database.connection import DatabaseManager


def initialize_schema(db_manager: DatabaseManager | None = None) -> None:
    db_manager = db_manager or DatabaseManager()

    with db_manager.get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role_id INTEGER NOT NULL,
                FOREIGN KEY (role_id) REFERENCES roles(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                phone TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medicines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category_id INTEGER,
                unit_price REAL NOT NULL CHECK (unit_price > 0),
                stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
                expiry_date TEXT,
                requires_prescription INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prescriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                doctor_name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prescription_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prescription_id INTEGER NOT NULL,
                medicine_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                FOREIGN KEY (prescription_id) REFERENCES prescriptions(id),
                FOREIGN KEY (medicine_id) REFERENCES medicines(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                prescription_id INTEGER,
                total_amount REAL NOT NULL CHECK (total_amount >= 0),
                sale_date TEXT NOT NULL,
                is_completed INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (customer_id) REFERENCES customers(id),
                FOREIGN KEY (prescription_id) REFERENCES prescriptions(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                medicine_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                unit_price REAL NOT NULL CHECK (unit_price > 0),
                subtotal REAL NOT NULL CHECK (subtotal >= 0),
                FOREIGN KEY (sale_id) REFERENCES sales(id),
                FOREIGN KEY (medicine_id) REFERENCES medicines(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                amount REAL NOT NULL CHECK (amount > 0),
                method TEXT NOT NULL CHECK (method IN ('CASH', 'CARD', 'TRANSFER')),
                FOREIGN KEY (sale_id) REFERENCES sales(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                medicine_id INTEGER NOT NULL,
                quantity_change INTEGER NOT NULL CHECK (quantity_change != 0),
                action_type TEXT NOT NULL CHECK (action_type IN ('IN', 'OUT', 'RETURN', 'ADJUST')),
                action_date TEXT NOT NULL,
                FOREIGN KEY (medicine_id) REFERENCES medicines(id)
            )
        """)

        cursor.executemany(
            "INSERT OR IGNORE INTO roles(id, name) VALUES (?, ?)",
            [(1, "admin"), (2, "pharmacist"), (3, "cashier")]
        )

        cursor.executemany(
            "INSERT OR IGNORE INTO categories(id, name) VALUES (?, ?)",
            [(1, "Painkiller"), (2, "Antibiotic"), (3, "Vitamin")]
        )

        cursor.execute("""
            INSERT OR IGNORE INTO users(id, full_name, username, password, role_id)
            VALUES (1, 'System Admin', 'admin', '123456', 1)
        """)