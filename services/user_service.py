from User import User
from repositories.user_repository import UserRepository


class UserService:
    def __init__(self, db):
        self.user_repo = UserRepository(db)

    def get_all_users(self):
        return self.user_repo.get_all()

    def create_user(self, full_name, username, password, role_id):
        if self.user_repo.get_by_username(username) is not None:
            raise ValueError("Username already exists.")

        user = User(None, full_name, username, password, role_id)
        self.user_repo.add(user)

        return user

    def delete_user(self, user_id, current_user_id):
        user_id = int(user_id)

        if user_id == current_user_id:
            raise ValueError("You cannot delete yourself.")

        return self.user_repo.remove_by_id(user_id)

    def role_text_to_id(self, role_text):
        if role_text == "Admin":
            return 1
        if role_text == "Pharmacist":
            return 2
        if role_text == "Cashier":
            return 3
        return 3

    def role_id_to_text(self, role_id):
        if role_id == 1:
            return "Admin"
        if role_id == 2:
            return "Pharmacist"
        if role_id == 3:
            return "Cashier"
        return "Unknown"