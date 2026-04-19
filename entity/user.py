class User:
    def __init__(self, id, username, email, role, supplier_id=None):
        self.id = id
        self.username = username
        self.email = email
        self.role = role
        self.supplier_id = supplier_id