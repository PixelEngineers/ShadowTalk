from handshake import PRIVATE, PUBLIC, create_keypair, PrivateKey, PublicKey
from nacl.signing import SigningKey, SignedMessage

"""
THIS BUNDLE SHOULD NEVER SEARCH THE PUBLIC AREA
THIS BUNDLE CONTAINS ALL THE PRIVATE KEYS
THIS BUNDLE IS NEVER MEANT TO BE SENT ANYWHERE
"""
class UserKeyBundle:
  identity: tuple[PrivateKey, PublicKey]
  one_use_keys: list[tuple[PrivateKey, PublicKey]]
  def __init__(self, no_of_one_time_keys: int):
    self.identity = create_keypair()
    self.one_use_keys = []
    for _ in range(no_of_one_time_keys):
      self.one_use_keys.append(create_keypair())

  def generate_more_one_use_keys(self, no_of_more_keys_to_generate):
    for _ in range(no_of_more_keys_to_generate):
      self.one_use_keys.append(create_keypair())

"""
This Bundle is designed to travel the public area
This Bundle only contains public keys
This Bundle is sent from the client to the server
"""
class PublicKeyBundle:
  identity: PublicKey
  signed_identity_key: SignedMessage
  one_use_public_keys: list[PublicKey]
  one_use_public_keys_used_till: int
  def __init__(self, user_key_bundle: UserKeyBundle):
    self.identity = user_key_bundle.identity[PUBLIC]
    self.signed_identity_key = SigningKey(
      bytes(user_key_bundle.identity[PRIVATE])
    ).sign(bytes(user_key_bundle.identity[PUBLIC]))
    self.one_use_public_keys = list(map(lambda pre_key: pre_key[PUBLIC], user_key_bundle.one_use_keys))
    self.one_use_public_keys_used_till = 0

"""
This Bundle is designed to travel the public area
This Bundle only contains public keys
This Bundle is sent from the server to the clients which want to talk to the sender client
"""
class PreKeyBundle:
  identity: PublicKey
  signed_identity_key: SignedMessage
  one_use_public_key: PublicKey
  def __init__(self, public_key_bundle: PublicKeyBundle):
    self.identity = public_key_bundle.identity
    self.signed_identity_key = public_key_bundle.signed_identity_key
    self.one_use_public_key = public_key_bundle.one_use_public_keys[public_key_bundle.one_use_public_keys_used_till]
    public_key_bundle.one_use_public_keys_used_till += 1

"""
This Bundle is designed to travel the public area
This Bundle only contains public keys
This Bundle is sent from the server to the clients which want to talk to the sender client
"""
class InitialMessageBundle:
  identity: PublicKey
  ephemeral_key: PublicKey
  one_time_key_used: PublicKey
  ciphertext: bytes
  def __init__(self,
    identity: PublicKey,
    ephemeral_key: PublicKey,
    one_time_key_used: PublicKey,
    ciphertext: bytes
  ):
    self.identity = identity
    self.ephemeral_key = ephemeral_key
    self.one_time_key_used = one_time_key_used
    self.ciphertext = ciphertext
