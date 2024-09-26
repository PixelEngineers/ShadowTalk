from dotenv import load_dotenv
from os import getenv as env

load_dotenv()

KEY_COLLECTION = "key_data"
USER_COLLECTION = "user_data"
GROUP_COLLECTION = "group_data"

def message_path(group_id: str):
    return f"messages/{group_id}"

config = {
    "apiKey": env("API_KEY"),
    "authDomain": env("AUTH_DOMAIN"),
    "projectId": env("PROJECT_ID"),
    "storageBucket": env("STORAGE_BUCKET"),
    "messagingSenderId": env("MESSAGING_SENDER_ID"),
    "appId": env("APP_ID"),
    "measurementId": env("MEASUREMENT_ID"),
}
