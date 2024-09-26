from nacl.public import PrivateKey, PublicKey
from nacl.signing import SigningKey

PRIVATE = 0
PUBLIC = 1

def create_keypair() -> tuple[PrivateKey, PublicKey]:
    sk = SigningKey.generate().to_curve25519_private_key()
    pk = sk.public_key
    return sk, pk