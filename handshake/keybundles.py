from handshake import PRIVATE, PUBLIC, create_keypair, PrivateKey, PublicKey
from typing import Optional
from nacl.signing import SigningKey, SignedMessage

class FuckYourException(Exception):
    pass

"""
THIS BUNDLE SHOULD NEVER SEARCH THE PUBLIC AREA
THIS BUNDLE CONTAINS ALL THE PRIVATE KEYS
THIS BUNDLE IS NEVER MEANT TO BE SENT ANYWHERE
"""
class UserKeyBundle:
    identity: tuple[PrivateKey, PublicKey]
    one_use_keys: list[tuple[PrivateKey, PublicKey]]
    def __init__(self, identity: tuple[PrivateKey, PublicKey], one_use_keys: list[tuple[PrivateKey, PublicKey]]):
        self.identity = identity
        self.one_use_keys = one_use_keys

    @staticmethod
    def init(no_of_one_time_keys: int) -> "UserKeyBundle":
        identity = create_keypair()
        one_use_keys = []
        for _ in range(no_of_one_time_keys):
            one_use_keys.append(create_keypair())
        return UserKeyBundle(identity, one_use_keys)

    def generate_more_one_use_keys(self, no_of_more_keys_to_generate):
        for _ in range(no_of_more_keys_to_generate):
            self.one_use_keys.append(create_keypair())

    def to_obj(self):
        print("Never send this bundle over the internet")
        raise FuckYourException()

"""
This Bundle is designed to travel the public area
This Bundle only contains public keys
This Bundle is sent from the client to the server
"""
class PublicKeyBundle:
    identity: PublicKey
    signed_identity_key: SignedMessage
    one_use_public_keys: list[PublicKey]
    def __init__(
        self,
        identity: PublicKey,
        signed_identity_key: SignedMessage,
        one_use_public_keys: list[PublicKey],
    ):
        self.identity = identity
        self.signed_identity_key = signed_identity_key
        self.one_use_public_keys = one_use_public_keys

    @staticmethod
    def init(user_key_bundle: UserKeyBundle) -> "PublicKeyBundle":
        identity = user_key_bundle.identity[PUBLIC]
        signed_identity_key = SigningKey(
            bytes(user_key_bundle.identity[PRIVATE])
        ).sign(bytes(user_key_bundle.identity[PUBLIC]))
        one_use_public_keys = list(map(lambda pre_key: pre_key[PUBLIC], user_key_bundle.one_use_keys))
        return PublicKeyBundle(identity, signed_identity_key, one_use_public_keys)

    def to_obj(self):
        return {
            "identity": self.identity,
            "signed_identity_key": self.signed_identity_key,
            "one_use_public_keys": self.one_use_public_keys,
        }

    @staticmethod
    def from_obj(data: dict) -> Optional["PublicKeyBundle"]:
        try:
            identity = data["identity"]
            signed_identity_key = data["signed_identity_key"]
            one_use_public_keys = data["one_use_public_keys"]
            return PublicKeyBundle(identity, signed_identity_key, one_use_public_keys)
        except:
            return None

"""
This Bundle is designed to travel the public area
This Bundle only contains public keys
This Bundle is sent from the server to the clients which want to talk to the sender client
"""
class PreKeyBundle:
    identity: PublicKey
    signed_identity_key: SignedMessage
    one_use_public_key: PublicKey
    def __init__(self, identity: PublicKey, signed_identity_key: SignedMessage, one_use_public_key: PublicKey):
        self.identity = identity
        self.signed_identity_key = signed_identity_key
        self.one_use_public_key = one_use_public_key

    @staticmethod
    def init(public_key_bundle: PublicKeyBundle) -> "PreKeyBundle":
        identity = public_key_bundle.identity
        signed_identity_key = public_key_bundle.signed_identity_key
        one_use_public_key = public_key_bundle.one_use_public_keys.pop(0)
        return PreKeyBundle(identity, signed_identity_key, one_use_public_key)

    def to_obj(self):
        return {
            "identity": self.identity,
            "signed_identity_key": self.signed_identity_key,
            "one_use_public_keys": self.one_use_public_key,
        }

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
    def __init__(self, identity: PublicKey, ephemeral_key: PublicKey, one_time_key_used: PublicKey, ciphertext: bytes):
        self.identity = identity
        self.ephemeral_key = ephemeral_key
        self.ciphertext = ciphertext

    def to_obj(self):
        return {
            "identity": self.identity,
            "ephemeral_key": self.ephemeral_key,
            "one_time_key_used": self.one_time_key_used,
            "ciphertext": self.ciphertext
        }