import math
import numpy as np
from . import util
from . import aes128, des, custom


def encrypt_file(input_file: util.File, output_file_path, key_aes128, key_des, key_custom, progress_update_hook=None) -> util.File:
    even = True
    key_aes128_cached = False
    key_des_cached = False
    key_custom_cached = False
    block_counter = 0
    num_of_blocks = math.ceil(len(input_file.file_in_bytes) / input_file.BLOCK_SIZE)

    ciphertext_bits = np.array([], dtype=np.uint8)

    while input_file.has_next:

        block_128 = input_file.get_next_block()

        if progress_update_hook:
            block_counter += 1
            progress_update_hook(round(100 * (block_counter / num_of_blocks)))

        # Even -> AES
        if even:
            even = False
            ciphertext_bits = np.append(ciphertext_bits, aes128.encrypt(block_128, key_aes128, key_aes128_cached))
            key_aes128_cached = True

        # Odd -> DES follwed by our custom algorithm
        else:
            even = True
            block_64x2 = np.hsplit(block_128, 2)
            ciphertext_bits = np.append(ciphertext_bits, des.encrypt(block_64x2[0], key_des, key_des_cached))
            ciphertext_bits = np.append(ciphertext_bits, custom.encrypt(block_64x2[1], key_custom, key_custom_cached))
            key_des_cached = True
            key_custom_cached = True

    return util.File.create_file(output_file_path, ciphertext_bits)


def decrypt_file(encrypted_file: util.File, output_file_path, key_aes128, key_des, key_custom, progress_update_hook=None) -> None:
    even = True
    key_aes128_cached = False
    key_des_cached = False
    key_custom_cached = False
    block_counter = 0
    num_of_blocks = math.ceil(len(encrypted_file.file_in_bytes) / encrypted_file.BLOCK_SIZE)

    recovered_bits = np.array([], dtype=np.uint8)

    while encrypted_file.has_next:

        block_128 = encrypted_file.get_next_block(decrypting=True)

        if progress_update_hook:
            block_counter += 1
            progress_update_hook(round(100 * (block_counter // num_of_blocks)))

        # Even -> AES
        if even:
            even = False
            recovered_bits = np.append(recovered_bits, aes128.decrypt(block_128, key_aes128, key_aes128_cached))
            key_aes128_cached = True

        # Odd -> DES follwed by our custom algorithm
        else:
            even = True
            block_64x2 = np.hsplit(block_128, 2)
            recovered_bits = np.append(recovered_bits, des.decrypt(block_64x2[0], key_des, key_des_cached))
            recovered_bits = np.append(recovered_bits, custom.decrypt(block_64x2[1], key_custom, key_custom_cached))
            key_des_cached = True
            key_custom_cached = True

    util.File.create_file(output_file_path, file_bits=recovered_bits, padded=True)
