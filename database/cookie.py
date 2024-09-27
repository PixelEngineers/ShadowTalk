from firebase_admin.auth import verify_id_token

class Cookie:
    uid: str
    email: str
    name: str

    def __init__(self, uid: str, email: str, name: str):
        self.uid = uid
        self.email = email
        self.name = name

    @staticmethod
    def from_token(token: str):
        decoded = verify_id_token(token)
        return Cookie(
            decoded['uid'],
            decoded['email'],
            decoded['name']
        )