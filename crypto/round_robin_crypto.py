import numpy as np
from . import util
from . import aes128, des, custom


def encrypt_file(input_file: util.File, key_aes128, key_des, key_custom) -> np.ndarray:
    even = True
    ciphertext_bits = np.array([], dtype=np.uint8)

    while input_file.has_next:

        block_128 = input_file.get_next_block()

        # Even -> AES
        if even:
            even = False
            ciphertext_bits = np.append(ciphertext_bits, aes128.encrypt(block_128, key_aes128))

        # Odd -> DES follwed by our custom algorithm
        else:
            even = True
            block_64x2 = np.hsplit(block_128, 2)
            ciphertext_bits = np.append(ciphertext_bits, des.encrypt(block_64x2[0], key_des))
            ciphertext_bits = np.append(ciphertext_bits, custom.encrypt(block_64x2[1], key_custom))

    return ciphertext_bits


def decrypt_file(encrypted_file: util.File, output_file_path, key_aes128, key_des, key_custom) -> None:
    even = True
    recovered_bits = np.array([], dtype=np.uint8)

    while encrypted_file.has_next:

        block_128 = encrypted_file.get_next_block(decrypting=True)

        # Even -> AES
        if even:
            even = False
            recovered_bits = np.append(recovered_bits, aes128.decrypt(block_128, key_aes128))

        # Odd -> DES follwed by our custom algorithm
        else:
            even = True
            block_64x2 = np.hsplit(block_128, 2)
            recovered_bits = np.append(recovered_bits, des.decrypt(block_64x2[0], key_des))
            recovered_bits = np.append(recovered_bits, custom.decrypt(block_64x2[1], key_custom))

    util.File.create_file(output_file_path, file_bits=recovered_bits, padded=True)
