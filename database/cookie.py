from firebase_admin.auth import verify_id_token

class Cookie:
    uid: str
    email: str
    name: str

    def __init__(self, token: str):
        decoded = verify_id_token(token)
        self.uid = decoded['uid']
        self.email = decoded['email']
        self.name = decoded['name']