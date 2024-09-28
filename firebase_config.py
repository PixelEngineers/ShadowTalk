from dotenv import load_dotenv
from os import getenv
from firebase_admin import credentials

load_dotenv()

KEY_COLLECTION = "key_data"
USER_COLLECTION = "user_data"
GROUP_COLLECTION = "group_data"

def message_path(group_id: str):
    return f"messages/{group_id}"

config_app = {
    "apiKey": getenv("API_KEY"),
    "authDomain": getenv("AUTH_DOMAIN"),
    "projectId": getenv("PROJECT_ID"),
    "storageBucket": getenv("STORAGE_BUCKET"),
    "messagingSenderId": getenv("MESSAGING_SENDER_ID"),
    "appId": getenv("APP_ID"),
    "measurementId": getenv("MEASUREMENT_ID"),
}
config = credentials.Certificate("firebase_creds.json")