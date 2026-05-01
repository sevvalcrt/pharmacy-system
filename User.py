class User:

    def __init__(self, user_id, full_name, username, password, role_id):
        self.id = user_id
        self.full_name = full_name.strip()
        self.username = username.strip()
        self.password = password.strip()
        self.role_id = role_id
        self._validate()

    def _validate(self):
        if not self.full_name:
            raise ValueError("Username and surname cannot be empty.")
        if len(self.username) < 3:
            raise ValueError("The username must be at least 3 characters long.")
        if len(self.password) < 6:
            raise ValueError("The password must be at least 6 characters long.")
        if self.role_id not in (1, 2, 3):
            raise ValueError("Invalid role ID.")
        
    def check_password(self, raw_password):
        return self.password == raw_password


