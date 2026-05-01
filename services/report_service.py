from database.connection import DatabaseManager


class ReportService:
    def __init__(self, db_manager: DatabaseManager) -> None:
        self.db_manager = db_manager

    def get_daily_total_sales(self, date_prefix: str) -> float:
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COALESCE(SUM(total_amount), 0) FROM sales WHERE sale_date LIKE ?",
                (f"{date_prefix}%",),
            )
            row = cursor.fetchone()
            return float(row[0]) if row else 0.0

    def get_monthly_total_sales(self, month_prefix: str) -> float:
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COALESCE(SUM(total_amount), 0) FROM sales WHERE sale_date LIKE ?",
                (f"{month_prefix}%",),
            )
            row = cursor.fetchone()
            return float(row[0]) if row else 0.0

    def get_sales_count_by_date(self, date_prefix: str) -> int:
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM sales WHERE sale_date LIKE ?",
                (f"{date_prefix}%",),
            )
            row = cursor.fetchone()
            return int(row[0]) if row else 0

    def get_top_selling_medicines(self, limit: int = 5) -> list[tuple]:
        if limit <= 0:
            raise ValueError("Limit 0'dan buyuk olmali.")

        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT m.name, COALESCE(SUM(si.quantity), 0) AS total_quantity
                FROM sale_items si
                JOIN medicines m ON m.id = si.medicine_id
                GROUP BY si.medicine_id, m.name
                ORDER BY total_quantity DESC
                LIMIT ?
                """,
                (limit,),
            )
            rows = cursor.fetchall()
            return [tuple(row) for row in rows]
