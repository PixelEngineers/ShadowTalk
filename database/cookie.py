from firebase_admin.auth import verify_id_token

class Cookie:
    id: str
    email: str
    name: str

    def __init__(self, uid: str, email: str, name: str):
        self.id = uid
        self.email = email
        self.name = name

    @staticmethod
    def from_dict(data: dict):
        return Cookie(
            data['uid'],
            data['email'],
            data['name']
        )

    def to_dict(self):
        return {
            "uid": self.id,
            "email": self.email,
            "name": self.name
        }