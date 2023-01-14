import numpy as np


def permute(original, permutation_table):

    permuted = np.zeros_like(permutation_table)

    # TODO: Vectorized/parallelized implementation
    for index, target_index in enumerate(permutation_table):
        permuted[index] = original[target_index]

    return permuted


def feistel_round(left_half, right_half, key, function_f):

    return right_half, np.logical_xor(left_half, function_f(right_half, key), dtype=np.int)


def bin_vec_to_dec_val(binary_vector):

    # Create a vector of powers of 2 (flipped) of the same size of the binary vector
    powers_vector = np.flip(2**(np.arange(len(binary_vector))), axis=0)

    # Mask out the powers that you need and return their sum, i.e., the decimal value equivalent
    return np.sum(powers_vector * binary_vector, dtype=np.uint8)


def dec_val_to_bin_vec(decimal_value, min_width=4):

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
