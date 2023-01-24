import numpy as np
from . import util
from . import des_tables as tables


def encrypt(message, key):

    # Initial permutation
    message = np.take(message, tables.INITIAL_PERMUTATION)

    # Split message into left and right halves
    message_left, message_right = message[:32], message[32:]

    # Get subkeys to use in feistel rounds
    subkeys = __generate_subkeys(key)

    # 16 feistel rounds of DES black magic
    for i in range(16):
        message_left, message_right = \
            util.feistel_round(message_left, message_right, subkeys[i], __feistel_function_f)

    # 32-bit swap and concatenate
    message = np.concatenate((message_right, message_left))

    # Inverse initial permutation
    message = np.take(message, tables.INVERSE_INITIAL_PERMUTATION)

    return message


def decrypt(cipher, key):

    # Initial permutation
    cipher = np.take(cipher, tables.INITIAL_PERMUTATION)

    # Split cipher into left and right halves
    cipher_left, cipher_right = cipher[:32], cipher[32:]

    # Get subkeys to use in feistel rounds
    subkeys = __generate_subkeys(key)

    # 16 feistel rounds of DES black magic
    for i in range(15, -1, -1):
        cipher_left, cipher_right = \
            util.feistel_round(cipher_left, cipher_right, subkeys[i], __feistel_function_f)

    # 32-bit swap and concatenate
    cipher = np.concatenate((cipher_right, cipher_left))

    # Inverse initial permutation
    cipher = np.take(cipher, tables.INVERSE_INITIAL_PERMUTATION)

    return cipher


def __substitution(message):

    # Split message into 8 pieces to get an 8x6 matrix
    message_split = np.hsplit(message, 8)

    # Circular-shift first column to be the last
    message_split = np.roll(message_split, -1, axis=1)

    # Split shifted message to row and column selectors as binary vectors
    selectors = np.hsplit(message_split, [4, ])

    # Convert selectors from binary vectors form to decimal values
    row_selectors = np.apply_along_axis(util.bit_vec_to_dec_val, 1, np.flip(selectors[1], axis=1))
    column_selectors = np.apply_along_axis(util.bit_vec_to_dec_val, 1, selectors[0])

    # Get the mapped values from the 8 S-boxes and convert to their binary vector representations
    # TODO: Vectorized/parallelized implementation
    message_subtitutions = np.zeros((8, 4), dtype=np.uint8)
    for i in range(8):
        message_subtitutions[i] = \
            util.dec_val_to_bit_vec(tables.S_BOXES[i][row_selectors[i]][column_selectors[i]])

    # Stitch back the message into the s-boxed message
    message = np.concatenate(message_subtitutions)

    return message


def __feistel_function_f(message, round_key):

    # Expanded permutation (for diffusion)
    message = np.take(message, tables.EXPANSION_PERMUTATION)

    # XOR with round key
    message = np.bitwise_xor(message, round_key)

    # Keyed substitution (8 Substitution-boxes) (anti differential cryptanalysis)
    message = __substitution(message)

    # Transposition (Permutation-box) (for even more diffusion and avalanche effect)
    message = np.take(message, tables.P_BOX)

    # XOR with "mangler"? Mentioned in reference but not actually used in practice

    return message


def __generate_subkeys(key):

    # Use PC1 for initial conversion of 64-bit key to two 28-bit keys
    key = np.take(key, tables.PC1)
    left, right = key[:28], key[28:]

    # Now we define the key rotation schedule
    key_rot_sched = [2, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2]

    # We'll be generating 16 48-bit keys
    subkeys = np.zeros((16, 48), dtype=np.uint8)

    # Then generate the 16 subkeys by shifting based on rotation schedule and permutating with PC2
    for i in range(16):
        left, right = np.roll(left, -key_rot_sched[i]), np.roll(right, -key_rot_sched[i])
        subkeys[i] = np.take(np.concatenate((left, right)), tables.PC2)

    return subkeys
