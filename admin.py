from User import User


class Admin(User):
    def __init__(self, user_id, full_name, username, password):
        super().__init__(user_id, full_name, username, password, role_id=1)
        self.can_manage_users = True

    def create_user(self, full_name, username, password, role_id):
        return User(None, full_name, username, password, role_id)

    def reset_user_password(self, user, new_password):
        if len(new_password.strip()) < 6:
            raise ValueError("The new password must be at least 6 characters long.")
        user.password = new_password.strip()