import os
import numpy as np


def feistel_round(left_half, right_half, key, function_f):

    return right_half, np.bitwise_xor(left_half, function_f(right_half, key))


def bit_vec_to_dec_val(binary_vector):

    # Create a vector of powers of 2 (flipped) of the same size of the binary vector
    powers_vector = np.flip(2**(np.arange(len(binary_vector))), axis=0)

    # Mask out the powers that you need and return their sum, i.e., the decimal value equivalent
    return np.sum(powers_vector * binary_vector, dtype=np.uint8)


def dec_val_to_bit_vec(decimal_value, min_width=4):

    # Calculate actual width
    actual_width = 1
    if decimal_value > 0:
        actual_width += np.floor(np.log2(decimal_value))
    elif decimal_value < 0:
        actual_width += np.ceil(np.log2(abs(decimal_value)))

    # Get binary string representation of decimal value using the higher of minimum/actual widths
    binary_string = np.binary_repr(decimal_value, width=max(min_width, actual_width))

    # Convert and return this string representation as an array
    return np.array([int(bit_char) for bit_char in binary_string])

# TODO: bit_vec_to_byte_vec and vice versa


class File:

    BLOCK_SIZE = 16  # bytes

    @staticmethod
    def create_file(file_path, file_bits: np.ndarray, padded=False):
        file_bytes: np.ndarray = np.packbits(file_bits)
        if padded:
            num_of_padding_bytes = file_bytes[-1]  # PKCS5
            file_bytes = np.resize(file_bytes, len(file_bytes) - num_of_padding_bytes)
        file_bytes.tofile(file_path)
        return File(file_path)

    def __init__(self, file_path):
        self.file_in_bytes: np.ndarray = np.fromfile(file_path, dtype=np.uint8)
        self.file_path_no_ext, self.file_ext = os.path.splitext(file_path)
        self.file_path = file_path
        self.has_next = True

    def get_next_block(self, decrypting=False):
        if len(self.file_in_bytes) >= File.BLOCK_SIZE:
            bits = np.unpackbits(self.file_in_bytes[:File.BLOCK_SIZE])
            self.file_in_bytes = self.file_in_bytes[File.BLOCK_SIZE:]
            if len(self.file_in_bytes) == 0 and decrypting:
                self.has_next = False
            return bits

        self.has_next = False
        remaining_bytes = np.uint8(File.BLOCK_SIZE - len(self.file_in_bytes))
        block = self.file_in_bytes.copy()
        for _ in range(remaining_bytes):
            block = np.append(block, remaining_bytes)
        return np.unpackbits(block)
