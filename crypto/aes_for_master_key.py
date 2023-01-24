# Using the library for the master key only, the rest of the algoirthms are written from scratch
from Crypto.Cipher import AES
from Crypto.Util import Padding


def encrypt(data: bytes, master_key: bytes) -> bytes:
    cipher_algo = AES.new(master_key, AES.MODE_ECB)
    padded_data = Padding.pad(data, 16)
    return cipher_algo.encrypt(padded_data)


def decrypt(data: bytes, master_key: bytes) -> bytes:
    cipher_algo = AES.new(master_key, AES.MODE_ECB)
    recovered_text = cipher_algo.decrypt(data)
    return Padding.unpad(recovered_text, 16)


if __name__ == "__main__":
    import numpy as np
    key = np.random.rand(4).tobytes()
    message = np.random.rand(3).tobytes()
    cipher = encrypt(message, key)
    recovered = decrypt(cipher, key)
    print(message)
    print(recovered)
