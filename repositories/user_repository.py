from User import User
from .base_repository import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self, db_manager=None):
        super().__init__(
            table_name="users",
            model_class=User,
            columns=["id", "full_name", "username", "password", "role_id"],
            db_manager=db_manager
        )

    def _row_to_object(self, row):
        return User(
            user_id=row["id"],
            full_name=row["full_name"],
            username=row["username"],
            password=row["password"],
            role_id=row["role_id"]
        )

    def _object_to_dict(self, item):
        return {
            "id": item.id,
            "full_name": item.full_name,
            "username": item.username,
            "password": item.password,
            "role_id": item.role_id
        }

    def get_by_username(self, username):
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()

        if row is None:
            return None
        return self._row_to_object(row)

    def login(self, username, password):
        user = self.get_by_username(username)
        if user is None:
            return None
        if not user.check_password(password):
            return None
        return user
