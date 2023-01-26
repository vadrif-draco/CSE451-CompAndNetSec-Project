import numpy as np
from . import custom_tables as tables

__TEST = 0
__TEST_DATA_ENC = []
__TEST_DATA_DEC = []

CACHES: dict[str, np.ndarray] = {}


def encrypt(data: np.ndarray, key: np.ndarray, use_caches=False):

    # Generate the keys and S-Boxes to be used in encryption and cache for reuse
    if not use_caches: __generate_and_cache_internal_keys_and_sboxes(seed=key)

    # Go through the 7*6 rounds with them
    for round_number in range(7):
        for inner_round_number in range(6):
            data = __inner_round(
                data,
                inner_round_number,
                CACHES['keys'][round_number][inner_round_number],
                CACHES['sboxes'][round_number][inner_round_number]
            )

    return data


def decrypt(data: np.ndarray, key: np.ndarray, use_caches=False):

    # Generate the keys and S-Boxes to be used in decryption and cache for reuse
    if not use_caches: __generate_and_cache_internal_keys_and_sboxes(seed=key)

    # Go through the 7*6 rounds with thems backwards
    for round_number in range(7)[::-1]:
        for inner_round_number in range(6)[::-1]:
            data = __inverse_inner_round(
                data,
                inner_round_number,
                CACHES['keys'][round_number][inner_round_number],
                CACHES['inverse_sboxes'][round_number][inner_round_number]
            )

    return data


def __generate_and_cache_internal_keys_and_sboxes(seed: np.ndarray):
    seed.flags.writeable = False
    seeded_rng = np.random.RandomState(seed)
    sboxes = np.zeros((7, 6, 256), dtype=np.uint8)
    inverse_sboxes = np.zeros((7, 6, 256), dtype=np.uint8)
    for i in range(7):
        for j in range(6):
            sbox = seeded_rng.permutation(256)
            sboxes[i][j] = sbox
            inverse_sbox = np.zeros(256, dtype=np.uint8)
            inverse_sbox[sbox] = np.arange(256)
            inverse_sboxes[i][j] = inverse_sbox
    global CACHES
    CACHES['sboxes'] = sboxes
    CACHES['inverse_sboxes'] = inverse_sboxes
    CACHES['keys'] = seeded_rng.randint(low=0, high=2, size=(7, 6, 64), dtype=np.uint8)


def __inner_round(ir_input: np.ndarray, ir_number: int, ir_key: np.ndarray, ir_sbox: np.ndarray):

    # Perform substitutions on the input with the round's byte-based S-Box
    substituted = np.unpackbits(np.take(ir_sbox, np.packbits(ir_input)))

    # Take the XOR of the result
    substituted_xored = np.bitwise_xor(substituted, ir_key)

    # Mask the two to isolate the bits which we will swap later
    substituted_masked = np.bitwise_and(substituted, tables.I1_MASKS[ir_number])
    substituted_xored_masked = np.bitwise_and(substituted_xored, tables.I2_MASKS[ir_number])

    # Calculate shift size by which to roll the bits in opposite directions for the swap
    shift_size = np.power(2, ir_number)

    # Roll them left and right by shift size then OR them to perform this round's swap
    rolled_left = np.roll(substituted_masked, -shift_size)
    rolled_right = np.roll(substituted_xored_masked, shift_size)
    substituted_halfxorswap = np.bitwise_or(rolled_left, rolled_right)

    # Transpose the 8x8 representation of the 64 bits (vital for the S-Box used above to work)
    result = substituted_halfxorswap.reshape((8, 8)).transpose().reshape(64)

    if __TEST:
        __TEST_DATA_ENC.append({})
        __TEST_DATA_ENC[-1]['irin'] = np.packbits(ir_input)
        __TEST_DATA_ENC[-1]['subs'] = np.packbits(substituted_masked)
        __TEST_DATA_ENC[-1]['sxor'] = np.packbits(substituted_xored_masked)
        __TEST_DATA_ENC[-1]['shxs'] = np.packbits(substituted_halfxorswap)
        __TEST_DATA_ENC[-1]['rslt'] = np.packbits(result)

    return result


def __inverse_inner_round(ir_input: np.ndarray, ir_number: int, ir_key: np.ndarray, ir_inverse_sbox: np.ndarray):

    # Undo the transpose operation from the last step of the corresponding encryption round
    substituted_halfxorswap = ir_input.reshape((8, 8)).transpose().reshape(64)

    # Calculate shift size by which to unroll the bits to undo the round's swap
    shift_size = np.power(2, ir_number)

    # Roll them right and left by shift size to undo the roll from encryption (but note that they're not masked!)
    unrolled_left = np.roll(substituted_halfxorswap, shift_size)
    unrolled_right = np.roll(substituted_halfxorswap, -shift_size)

    # Restore the substituted-only portion, which is the unrolled left portion when masked
    substituted_masked = np.bitwise_and(unrolled_left, tables.I1_MASKS[ir_number])

    # Restore the substituted-and-xored portion, which is the unrolled right portion when masked after undoing the XOR
    substituted_unxored = np.bitwise_xor(unrolled_right, ir_key)
    substituted_unxored_masked = np.bitwise_and(substituted_unxored, tables.I2_MASKS[ir_number])

    # Restore the substituted text by taking the OR of the restored portions above
    substituted = np.bitwise_or(substituted_masked, substituted_unxored_masked)

    # Undo the substituted with the round's inverse byte-based S-box
    unsubstituted = np.unpackbits(np.take(ir_inverse_sbox, np.packbits(substituted)))

    if __TEST:
        __TEST_DATA_DEC.append({})
        __TEST_DATA_DEC[-1]['irin'] = np.packbits(ir_input)
        __TEST_DATA_DEC[-1]['shxs'] = np.packbits(substituted_halfxorswap)
        __TEST_DATA_DEC[-1]['sxor'] = np.packbits(np.bitwise_and(unrolled_right, tables.I2_MASKS[ir_number]))
        __TEST_DATA_DEC[-1]['subs'] = np.packbits(substituted_masked)
        __TEST_DATA_DEC[-1]['rslt'] = np.packbits(unsubstituted)

    return unsubstituted


def internal_test():
    global __TEST
    __TEST = 1

    message = np.array([np.random.choice([0, 1]) for _ in range(64)])
    key = np.array([np.random.choice([0, 1]) for _ in range(256)])
    encrypted = encrypt(message, key)
    decrypted = decrypt(encrypted, key)

    print(f"Key: {np.packbits(key)}")
    print(f"Original:  {np.packbits(message)}")
    print(f"Decrypted: {np.packbits(decrypted)}")
    print(f"Encrypted: {np.packbits(encrypted)}")

    for round_number in range(7):
        for inner_round_number in range(6):
            i = round_number * 6 + inner_round_number
            print(
                f"Encryption round number: {1+round_number}:{1+inner_round_number}\n"
                f"Decryption round number: {7-round_number}:{6-inner_round_number}\n"
                "\n"
                f"Encryption round input:  {__TEST_DATA_ENC[i]['irin']}\n"
                f"Encryption round result: {__TEST_DATA_ENC[i]['rslt']}\n"
                f"Decryption round input:  {__TEST_DATA_DEC[41-i]['irin']}\n"
                f"Decryption round result: {__TEST_DATA_DEC[41-i]['rslt']}\n"
                "\n"
                f"Encryption substituted masked input: {__TEST_DATA_ENC[i]['subs']}\n"
                f"Decryption substituted masked input: {__TEST_DATA_DEC[41-i]['subs']}\n"
                "\n"
                f"Encryption substituted-xored masked input: {__TEST_DATA_ENC[i]['sxor']}\n"
                f"Decryption substituted-xored masked input: {__TEST_DATA_DEC[41-i]['sxor']}\n"
                "\n"
                f"Encryption half-substituted-xored swapped input: {__TEST_DATA_ENC[i]['shxs']}\n"
                f"Decryption half-substituted-xored swapped input: {__TEST_DATA_DEC[41-i]['shxs']}\n"
                "\n"
                "\n"
            )


if __name__ == "__main__":
    internal_test()
