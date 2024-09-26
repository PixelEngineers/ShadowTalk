from os.path import exists
from typing import Optional, TypeVar, Callable
import pickle

from database.Interop import DatabaseInterop
from database.user import User
from database.group import Group
from database.message import Message

T = TypeVar("T")
def find_index(to_iter: list[T], expression: Callable[[T], bool]) -> Optional[int]:
    for i, item in enumerate(to_iter):
        if expression(item):
            return i

def create_if_not_exist(name: str, default_data, mode='w'):
    if exists(name):
        return
    f = open(name, mode)
    f.write(default_data)
    f.close()

class FileDatabase(DatabaseInterop):
    users: list[User]
    groups: list[Group]
    messages: dict[str, list[Message]]

    user_db_location: str
    group_db_location: str
    messages_db_location: str

    def __init__(self, user_db_location: str, group_db_location: str, messages_db_location: str):
        create_if_not_exist(user_db_location, pickle.dumps([]), 'wb')
        create_if_not_exist(group_db_location, pickle.dumps([]), 'wb')
        create_if_not_exist(messages_db_location, pickle.dumps({}), 'wb')

        with open(user_db_location, 'rb') as f:
            self.users = pickle.load(f)
        with open(group_db_location, 'rb') as f:
            self.groups = pickle.load(f)
        with open(messages_db_location, 'rb') as f:
            self.messages = pickle.load(f)

        self.user_db_location = user_db_location
        self.group_db_location = group_db_location
        self.messages_db_location = messages_db_location
        super().__init__()

    def deinit(self):
        with open(self.user_db_location, 'wb') as f:
            pickle.dump(self.users, f)
        with open(self.group_db_location, 'wb') as f:
            pickle.dump(self.groups, f)
        with open(self.messages_db_location, 'wb') as f:
            pickle.dump(self.messages, f)

