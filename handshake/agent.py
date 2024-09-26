from typing import Optional

from handshake import PUBLIC, PublicKey, create_keypair, PRIVATE
from handshake.keyservice import KeyService
from handshake.keybundles import UserKeyBundle, PublicKeyBundle, InitialMessageBundle
from notation_functions import dh, kdf
from nacl.secret import Aead
import pickle

agent_data_location = "../file_db/agent_data"

class Connection:
    box: Aead
    additional_data: bytes
    def __init__(self, box: Aead, additional_data: bytes):
        self.box = box
        self.additional_data = additional_data

    def encrypt(self, plaintext_message: bytes) -> bytes:
        return self.box.encrypt(plaintext_message, self.additional_data)

    def decrypt(self, encrypted_message: bytes) -> bytes:
        return self.box.decrypt(encrypted_message, self.additional_data)

class Agent:
    identify: str
    user_key_bundle: UserKeyBundle
    key_service: KeyService
    connections: dict[str, Connection]
    def __init__(self, identify: str, key_service: KeyService, no_of_one_time_keys: int):
        self.identify = identify
        self.user_key_bundle = UserKeyBundle.init(no_of_one_time_keys)
        self.key_service = key_service
        self.key_service.create_user(identify, PublicKeyBundle.init(self.user_key_bundle))
        self.connections = {}

    @staticmethod
    def file_else_default(identify: str, key_service: KeyService, no_of_one_time_keys: int) -> "Agent":
        from_file = Agent.from_file(identify)
        if from_file is None:
            return Agent(identify, key_service, no_of_one_time_keys)
        return from_file

    @staticmethod
    def from_file(identify: str) -> Optional["Agent"]:
        try:
            with open(f"{agent_data_location}/{identify}.dat", "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return None

    def to_file(self):
        with open(f"{agent_data_location}/{self.identify}.dat", "wb") as f:
            pickle.dump(self, f)

    """
    Create a connection with another user
    """
    def connect(self, user_id: str) -> InitialMessageBundle:
        pre_key_bundle = self.key_service.get_pre_key_bundle(user_id)
        ephemeral_key = create_keypair()

        IPKa: PublicKey = self.user_key_bundle.identity[PUBLIC]
        EPKa: PublicKey = ephemeral_key[PUBLIC]
        IPKb: PublicKey = pre_key_bundle.identity
        SPKb = pre_key_bundle.signed_identity_key
        OPKb: PublicKey = pre_key_bundle.one_use_public_key

        # dh -> diffie hellman
        dh1 = dh(IPKa.encode(), SPKb.message)
        dh2 = dh(EPKa.encode(), IPKb.encode())
        dh3 = dh(EPKa.encode(), SPKb.message)
        dh4 = dh(EPKa.encode(), OPKb.encode())

        master_key = kdf(
            bytearray(dh1) +
            bytearray(dh2) +
            bytearray(dh3) +
            bytearray(dh4)
        )
        safety_number = bytes(
            self.user_key_bundle.identity[PUBLIC].encode() +
            pre_key_bundle.identity.encode()
        )

        self.connections[user_id] = Connection(Aead(master_key[PRIVATE].encode()), safety_number)

        return InitialMessageBundle(
            IPKa,
            EPKa,
            pre_key_bundle.one_use_public_key,
            self.connections[user_id].encrypt(b"Hello World")
        )

    def initial_message(self, user_id: str, initial_message_bundle: InitialMessageBundle):
        IPKa = initial_message_bundle.identity
        EPKa = initial_message_bundle.ephemeral_key
        IPKb = self.user_key_bundle.identity[PUBLIC]
        SPKb = PublicKeyBundle.init(self.user_key_bundle).signed_identity_key
        OPKb = initial_message_bundle.one_time_key_used

        dh1 = dh(IPKa.encode(), SPKb.message)
        dh2 = dh(EPKa.encode(), IPKb.encode())
        dh3 = dh(EPKa.encode(), SPKb.message)
        dh4 = dh(EPKa.encode(), OPKb.encode())

        master_key = kdf(
            bytearray(dh1) +
            bytearray(dh2) +
            bytearray(dh3) +
            bytearray(dh4)
        )
        safety_number = bytes(IPKa.encode() + IPKb.encode())

        self.connections[user_id] = Connection(Aead(master_key[PRIVATE].encode()), safety_number)

    def send(self, user_id: str, message: bytes) -> Optional[bytes]:
        box = self.connections.get(user_id)
        if box is None:
            return None
        return box.encrypt(message)

    def receive(self, user_id: str, message: bytes) -> Optional[bytes]:
        box = self.connections.get(user_id)
        if box is None:
            return None
        return box.decrypt(message)
