# Using the library for the master key only, the rest of the algoirthms are written from scratch
from Crypto.Cipher import AES


def encrypt(data: bytes, master_key: bytes) -> bytes:
    cipher_algo = AES.new(master_key, AES.MODE_EAX)
    return cipher_algo.encrypt(data)


def decrypt(data: bytes, master_key: bytes) -> bytes:
    cipher_algo = AES.new(master_key, AES.MODE_EAX)
    return cipher_algo.decrypt(data)
