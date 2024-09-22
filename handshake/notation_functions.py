APPLICATION_DOMAIN = "in.shadowtalk"

from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.hashes import SHA512
from nacl.signing import SigningKey
from nacl.public import PrivateKey, PublicKey

def dh(pk1: bytes, pk2: bytes) -> bytes:
  return HKDF(
    SHA512(),
    32,
    b'\xff'*32,
    APPLICATION_DOMAIN.encode()
  ).derive(bytearray(pk1) + bytearray(pk2))

def sign(pk: SigningKey, m: bytes) -> bytes:
  return pk.sign(m)

def kdf(km: bytes) -> tuple[PrivateKey, PublicKey]:
  sk = PrivateKey(HKDF(
    SHA512(),
    32,
    b'\xff'*32,
    APPLICATION_DOMAIN.encode()
  ).derive(km))
  pk = sk.public_key
  return sk, pk

