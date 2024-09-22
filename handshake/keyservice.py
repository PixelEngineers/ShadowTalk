from handshake.keybundles import PublicKeyBundle, PreKeyBundle
from os.path import exists
import pickle

class KeyService:
  def __init__(self): pass
  def deinit(self): pass

  def create_user(self, user_id: str, public_key_bundle: PublicKeyBundle): pass
  def get_pre_key_bundle(self, user_id: str) -> PreKeyBundle: pass

def create_if_not_exist(name: str, default_data, mode='w'):
  if exists(name):
    return
  f = open(name, mode)
  f.write(default_data)
  f.close()

key_data_location = "../file_db/keys.dat"

class FileKeyService(KeyService):
  key_data: dict[str, PublicKeyBundle]
  key_data_location: str

  def __init__(self):
    create_if_not_exist(key_data_location, pickle.dumps({}), 'wb')

    with open(key_data_location, 'rb') as f:
      self.key_data = pickle.load(f)

    self.key_data_location = key_data_location
    super().__init__()

  def deinit(self):
    with open(self.key_data_location, 'wb') as f:
      pickle.dump(self.key_data, f)

  def create_user(self, user_id: str, public_key_bundle: PublicKeyBundle):
    self.key_data[user_id] = public_key_bundle

  def get_pre_key_bundle(self, user_id: str) -> PreKeyBundle:
    return PreKeyBundle(self.key_data[user_id])
