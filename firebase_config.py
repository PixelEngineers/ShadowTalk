from dotenv import load_dotenv
from firebase_admin import credentials

load_dotenv()

KEY_COLLECTION = "key_data"
USER_COLLECTION = "user_data"
GROUP_COLLECTION = "group_data"

def message_path(group_id: str):
    return f"messages/{group_id}"

config = credentials.Certificate("firebase_creds.json")