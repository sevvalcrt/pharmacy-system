import os
from contextlib import contextmanager

import mysql.connector


class DatabaseManager:
    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        user: str | None = None,
        password: str | None = None,
        database: str | None = None,
    ) -> None:
        self.config = {
            "host": host or os.getenv("DB_HOST", "127.0.0.1"),
            "port": int(port or os.getenv("DB_PORT", "3306")),
            "user": user or os.getenv("DB_USER", "root"),
            "password": password or os.getenv("DB_PASSWORD", ""),
            "database": database or os.getenv("DB_NAME", "pharmacy_db"),
        }

    @contextmanager
    def get_connection(self):
        connection = mysql.connector.connect(**self.config)
        try:
            yield connection
        finally:
            if connection.is_connected():
                connection.close()
