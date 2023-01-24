import numpy as np
from . import aes_tables as tables
from . import util


def encrypt(message, initial_key):

    keys = __expand_key(initial_key)

    # Convert plain message form (1x128) to state form (4x4)
    state = __1x128_bits_to_4x4_bytes(message)

    # Proceed with encryption logic
    state = __add_round_key(state, keys[0])
    for i in range(1, 10):
        state = __substitute_bytes(state)
        state = __shift_rows(state)
        state = __mix_cols(state)
        state = __add_round_key(state, keys[i])
    state = __substitute_bytes(state)
    state = __shift_rows(state)
    state = __add_round_key(state, keys[10])

    # Convert state form (4x4) back to cipher message (1x128)
    cipher = __4x4_bytes_to_1x128_bits(state)

    return cipher


def decrypt(cipher, initial_key):

    keys = __expand_key(initial_key)

    # Convert cipher message form (1x128) to state form (4x4)
    state = __1x128_bits_to_4x4_bytes(cipher)

    # Proceed with decryption logic
    state = __add_round_key(state, keys[10])
    for i in range(9, 0, -1):
        state = __shift_rows(state, inverse=True)
        state = __substitute_bytes(state, inverse=True)
        state = __add_round_key(state, keys[i])
        state = __mix_cols(state, inverse=True)
    state = __shift_rows(state, inverse=True)
    state = __substitute_bytes(state, inverse=True)
    state = __add_round_key(state, keys[0])

    # Convert state form (4x4) back to plain message (1x128)
    message = __4x4_bytes_to_1x128_bits(state)

    return message


def __1x128_bits_to_4x4_bytes(data_1x128):
    # 128 bits -> 16 8-bit vectors
    data_16x8 = np.hsplit(data_1x128, 16)
    # 16 8-bit vectors -> 16 bytes
    data_16x1 = np.apply_along_axis(util.bit_vec_to_dec_val, 1, data_16x8)
    # 16 bytes -> 4x4 bytes
    data_4x4 = np.reshape(data_16x1, (4, 4))
    return data_4x4


def __4x4_bytes_to_1x128_bits(data_4x4):
    # 4x4 bytes -> 16 bytes
    data_16x1 = np.reshape(data_4x4, (16, 1))
    # 16 bytes -> 16 8-bit vectors
    data_16x8 = np.apply_along_axis(lambda dec: util.dec_val_to_bit_vec(dec[0], 8), 1, data_16x1)
    # 16 8-bit vectors -> 128 bits
    data_1x128 = np.concatenate(data_16x8)
    return data_1x128


def __g(word, round_num):
    word = np.roll(word, -1)  # Circular shift left
    word = np.take(tables.S_BOX, word)  # S-Box the bytes
    word[0] = np.bitwise_xor(tables.ROUND_CONSTANTS[round_num], word[0])  # XOR first byte with RC
    return word


def __expand_key(initial_key_1x128):
    round_keys = np.zeros((11, 4, 4), dtype=np.uint32)
    round_keys[0] = __1x128_bits_to_4x4_bytes(initial_key_1x128)
    for i in range(1, 11):
        round_keys[i][0] = np.bitwise_xor(round_keys[i - 1][0], __g(round_keys[i - 1][3], i))
        round_keys[i][1] = np.bitwise_xor(round_keys[i - 1][1], round_keys[i][0])
        round_keys[i][2] = np.bitwise_xor(round_keys[i - 1][2], round_keys[i][1])
        round_keys[i][3] = np.bitwise_xor(round_keys[i - 1][3], round_keys[i][2])
    return round_keys


def __add_round_key(state, round_key):
    return np.bitwise_xor(state, round_key)


def __substitute_bytes(state, inverse: bool = False):
    return np.take(tables.INVERSE_S_BOX if inverse else tables.S_BOX, state)


def __shift_rows(state, inverse: bool = False):
    state = np.transpose(state)
    for i in range(1, 4):
        state[i] = np.roll(state[i], i if inverse else -i)
    return np.transpose(state)


def __mix_cols_lookup(word):

    b_0, b_1, b_2, b_3 = word  # the bytes
    return np.array(
        [
            # Remember that XOR is multiplication in GF(2^8)
            [tables.MCLU02[b_0] ^ tables.MCLU03[b_1] ^ tables.MCLU01[b_2] ^ tables.MCLU01[b_3]],
            [tables.MCLU01[b_0] ^ tables.MCLU02[b_1] ^ tables.MCLU03[b_2] ^ tables.MCLU01[b_3]],
            [tables.MCLU01[b_0] ^ tables.MCLU01[b_1] ^ tables.MCLU02[b_2] ^ tables.MCLU03[b_3]],
            [tables.MCLU03[b_0] ^ tables.MCLU01[b_1] ^ tables.MCLU01[b_2] ^ tables.MCLU02[b_3]]
        ]
    ).reshape((4,))


def __mix_cols_inverse_lookup(word):

    b_0, b_1, b_2, b_3 = word  # the bytes
    return np.array(
        [
            [tables.MCLU14[b_0] ^ tables.MCLU11[b_1] ^ tables.MCLU13[b_2] ^ tables.MCLU09[b_3]],
            [tables.MCLU09[b_0] ^ tables.MCLU14[b_1] ^ tables.MCLU11[b_2] ^ tables.MCLU13[b_3]],
            [tables.MCLU13[b_0] ^ tables.MCLU09[b_1] ^ tables.MCLU14[b_2] ^ tables.MCLU11[b_3]],
            [tables.MCLU11[b_0] ^ tables.MCLU13[b_1] ^ tables.MCLU09[b_2] ^ tables.MCLU14[b_3]]
        ]
    ).reshape((4,))


def __mix_cols(state, inverse: bool = False):
    new_state = np.zeros_like(state)
    for word_index, word in enumerate(state):
        new_state[word_index] = __mix_cols_inverse_lookup(word) if inverse else __mix_cols_lookup(word)
    return new_state
