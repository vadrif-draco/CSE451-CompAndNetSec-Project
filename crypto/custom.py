import numpy as np
from . import custom_tables as tables
from . import util


DEBUG = 0
debug_data_enc = []
debug_data_dec = []


def encrypt(message, key):
    keys = __generate_keys(seed=key)

    for round_number in range(7):
        for inner_round_number in range(6):
            message = __inner_round(
                message,
                inner_round_number,
                keys[round_number][inner_round_number],
                keys[round_number][inner_round_number + 6]
            )

    return message


def decrypt(cipher, key):
    keys = __generate_keys(seed=key)

    for round_number in range(7)[::-1]:
        for inner_round_number in range(6)[::-1]:
            cipher = __inverse_inner_round(
                cipher,
                inner_round_number,
                keys[round_number][inner_round_number],
                keys[round_number][inner_round_number + 6]
            )

    return cipher


def __generate_keys(seed):
    # Generate keys for all rounds and their inner rounds
    # The 6 + 6 refers to the 6 keys used by each inner round's initial XOR, plus the 6 keys used by the terminal XOR
    keys_int64 = np.random.RandomState(seed).randint(low=0, high=2**64, dtype=np.uint64, size=(7 * (6 + 6), 1))

    # Convert from int64 value to 64-bit vectors
    keys_bits = np.apply_along_axis(lambda decimal: util.dec_val_to_bit_vec(decimal[0], min_width=64), 1, keys_int64)

    # Reshape for 7 rounds and 6+6 inner rounds of 64-bit keys
    return np.reshape(keys_bits, (7, 12, 64))


def __swap_bits(i1_original, i2_original, inner_round_number, shift_size):
    i1_masked = np.bitwise_and(i1_original, tables.I1_MASKS[inner_round_number])
    i2_masked = np.bitwise_and(i2_original, tables.I2_MASKS[inner_round_number])

    if DEBUG:
        debug_data_enc.append({})
        debug_data_enc[-1]['i1_masked'] = np.packbits(np.hsplit(i1_masked, 8))
        debug_data_enc[-1]['i2_masked'] = np.packbits(np.hsplit(i2_masked, 8))

    return np.bitwise_or(np.roll(i1_masked, -shift_size), np.roll(i2_masked, shift_size))


def __reverse_swap_bits(swap, shift_size):
    i1_unmasked = np.roll(swap, shift_size)
    i2_unrolled = np.roll(swap, -shift_size)

    return i1_unmasked, i2_unrolled


def __inner_round(i1_original, inner_round_number, keyi, key6):
    shift_size = np.power(2, inner_round_number)

    i2_original = np.bitwise_xor(i1_original, key6)

    swap = __swap_bits(i1_original, i2_original, inner_round_number, shift_size)

    ciphertext = np.bitwise_xor(swap, keyi)

    if DEBUG:
        debug_data_enc[-1]['shift_size'] = shift_size
        debug_data_enc[-1]['key6'] = np.packbits(np.hsplit(key6, 8))
        debug_data_enc[-1]['keyi'] = np.packbits(np.hsplit(keyi, 8))
        debug_data_enc[-1]['i1'] = np.packbits(np.hsplit(i1_original, 8))
        debug_data_enc[-1]['i2'] = np.packbits(np.hsplit(i2_original, 8))
        debug_data_enc[-1]['swap'] = np.packbits(np.hsplit(swap, 8))
        debug_data_enc[-1]['ciphertext'] = np.packbits(np.hsplit(ciphertext, 8))

    return ciphertext


def __inverse_inner_round(ciphertext, inner_round_number, keyi, key6):
    shift_size = np.power(2, inner_round_number)

    swap = np.bitwise_xor(ciphertext, keyi)

    i1_unmasked, i2_unrolled = __reverse_swap_bits(swap, shift_size)

    i2_unmasked = np.bitwise_xor(i2_unrolled, key6)

    i1_masked = np.bitwise_and(i1_unmasked, tables.I1_MASKS[inner_round_number])
    i2_masked = np.bitwise_and(i2_unmasked, tables.I2_MASKS[inner_round_number])

    plaintext = np.bitwise_or(i1_masked, i2_masked)

    if DEBUG:
        debug_data_dec.append({})
        debug_data_dec[-1]['shift_size'] = shift_size
        debug_data_dec[-1]['keyi'] = np.packbits(np.hsplit(keyi, 8))
        debug_data_dec[-1]['key6'] = np.packbits(np.hsplit(key6, 8))
        debug_data_dec[-1]['swap'] = np.packbits(np.hsplit(swap, 8))
        debug_data_dec[-1]['i1_unmasked'] = np.packbits(np.hsplit(i1_unmasked, 8))
        debug_data_dec[-1]['i2_unroll'] = np.packbits(np.hsplit(i2_unrolled, 8))
        debug_data_dec[-1]['i2_unmasked'] = np.packbits(np.hsplit(i2_unmasked, 8))
        debug_data_dec[-1]['i1_masked'] = np.packbits(np.hsplit(i1_masked, 8))
        debug_data_dec[-1]['i2_masked'] = np.packbits(np.hsplit(
            np.bitwise_and(i2_unrolled, tables.I2_MASKS[inner_round_number]),
            8
        ))
        debug_data_dec[-1]['plaintext'] = np.packbits(np.hsplit(plaintext, 8))
        debug_data_dec[-1]['ciphertext'] = np.packbits(np.hsplit(ciphertext, 8))

    return plaintext


def test():
    global DEBUG
    DEBUG = 1

    np.set_printoptions(formatter={'int': hex})  # To print in hex

    message = np.array([np.random.choice([0, 1]) for _ in range(64)])
    print(f"message:\n{np.packbits(np.hsplit(message, 8))}\n")

    key = np.array([np.random.choice([0, 1]) for _ in range(256)])
    print(f"key:\n{np.packbits(np.hsplit(key, 8))}\n")

    cipher = encrypt(message, key)
    print(f"cipher:\n{np.packbits(np.hsplit(cipher, 8))}\n")

    recovered_message = decrypt(cipher, key)
    print(f"recovered_message:\n{np.packbits(np.hsplit(recovered_message, 8))}\n")

    for round_number in range(7):
        print(f"------- round_number {round_number} -------\n")
        for inner_round_number in range(6):
            i = round_number * 6 + inner_round_number
            print(
                f"---- inner_round_number {inner_round_number} ----\n"
                f"i={i}\n"
                f"plaintext:\nEnc: {debug_data_enc[i]['i1']}\nDec: {debug_data_dec[41-i]['plaintext']}\n\n"
                f"key{inner_round_number}:\nEnc: {debug_data_enc[i]['keyi']}\nDec: {debug_data_dec[41-i]['keyi']}\n\n"
                f"key6:\nEnc: {debug_data_enc[i]['key6']}\nDec: {debug_data_dec[41-i]['key6']}\n\n"
                f"i1_masked:\nEnc: {debug_data_enc[i]['i1_masked']}\nDec: {debug_data_dec[41-i]['i1_masked']}\n\n"
                f"i2_masked:\nEnc: {debug_data_enc[i]['i2_masked']}\nDec: {debug_data_dec[41-i]['i2_masked']}\n\n"
                f"swap:\nEnc: {debug_data_enc[i]['swap']}\nDec: {debug_data_dec[41-i]['swap']}\n\n"
                f"ciphertext:\n{debug_data_enc[i]['ciphertext']}\n{debug_data_dec[41-i]['ciphertext']}\n"
                f"-------------------------------\n\n"
            )

    np.set_printoptions()  # To reset printing to its default


if __name__ == "__main__":
    test()
