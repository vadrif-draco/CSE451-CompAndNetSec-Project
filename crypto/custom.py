import numpy as np
import custom_tables as tables
import util


def make_rngs(subkeys):
    rngs = []
    for subkey in subkeys:
        rngs.append(np.random.RandomState(subkey))

    return rngs


def swap_bits(i1, i2, inner_round_number, shift_size):
    I1_MASK = tables.I1_MASKS[inner_round_number]
    I2_MASK = tables.I2_MASKS[inner_round_number]

    i1_masked = np.bitwise_and(i1, I1_MASK)
    i2_masked = np.bitwise_and(i2, I2_MASK)

    if (DEBUG):
        debug_data_enc['i1_masked'] = i1_masked
        debug_data_enc['i2_masked'] = i2_masked

    return np.bitwise_or(np.roll(i1_masked, -shift_size), np.roll(i2_masked, shift_size))


def reverse_swap_bits(swap, shift_size):

    i1_unmasked = np.roll(swap, shift_size)
    i2_unroll = np.roll(swap, -shift_size)

    return i1_unmasked, i2_unroll


def round(i1, inner_round_number, rngs):
    shift_size = np.power(2, inner_round_number)

    rng7 = util.dec_val_to_bin_vec(rngs[7].randint(low=0, high=2**64, dtype=np.uint64), min_width=64)

    i2 = np.bitwise_xor(i1, rng7)

    swap = swap_bits(i1, i2, inner_round_number, shift_size)

    rng = util.dec_val_to_bin_vec(rngs[inner_round_number].randint(low=0, high=2**64, dtype=np.uint64), min_width=64)

    ciphertext = np.bitwise_xor(swap, rng)

    if DEBUG:
        debug_data_enc['shift_size'] = shift_size
        # TODO: Fix for different rounds
        debug_data_enc['rng7'] = rng7
        debug_data_enc[f'rng{inner_round_number}'] = rng
        debug_data_enc['i1'] = i1
        debug_data_enc['i2'] = i2
        debug_data_enc['swap'] = swap
        debug_data_enc['ciphertext'] = ciphertext
    
    return ciphertext
    

def round_inverse(ciphertext, inner_round_number, rngs):
    shift_size = np.power(2, inner_round_number)
    I1_MASK = tables.I1_MASKS[inner_round_number]
    I2_MASK = tables.I2_MASKS[inner_round_number]

    rng = util.dec_val_to_bin_vec(rngs[inner_round_number].randint(low=0, high=2**64, dtype=np.uint64), min_width=64)
    swap = np.bitwise_xor(ciphertext, rng)

    i1_unmasked, i2_unroll = reverse_swap_bits(swap, shift_size)
    
    rng7 = util.dec_val_to_bin_vec(rngs[7].randint(low=0, high=2**64, dtype=np.uint64), min_width=64)
    i2_unmasked = np.bitwise_xor(i2_unroll, rng7)

    i1_masked = np.bitwise_and(i1_unmasked, I1_MASK)
    i2_masked = np.bitwise_and(i2_unmasked, I2_MASK)

    plaintext = np.bitwise_or(i1_masked, i2_masked)

    if DEBUG:
        debug_data_dec['shift_size'] = shift_size
        debug_data_dec[f'rng{inner_round_number}'] = rng
        debug_data_dec['rng7'] = rng7
        debug_data_dec['swap'] = swap
        debug_data_dec['i1_unmasked'] = i1_unmasked
        debug_data_dec['i2_unroll'] = i2_unroll
        debug_data_dec['i2_unmasked'] = i2_unmasked
        debug_data_dec['i1_masked'] = i1_masked
        debug_data_dec['i2_masked'] = np.bitwise_and(i2_unroll, I2_MASK)
        debug_data_dec['plaintext'] = plaintext
        debug_data_dec['ciphertext'] = ciphertext
    
    return plaintext
    

DEBUG = 1
debug_data_enc = {}
debug_data_dec = {}

key = np.array([np.random.choice([0, 1]) for _ in range(256)])
subkeys = np.hsplit(key, 8)
print(subkeys[0])
RNGS = make_rngs(subkeys)

for inner_round_number in range(6):
    ciphertext = round(util.dec_val_to_bin_vec(np.random.randint(low=0, high=2**64, dtype=np.uint64), min_width=64), inner_round_number, RNGS)

    # RNGS = make_rngs(subkeys)
    # original = round_inverse(ciphertext, inner_round_number, RNGS)
    if DEBUG:
        print(
            f"---- inner_round_number {inner_round_number} ----\n"
            f"rng{inner_round_number}:\n{debug_data_enc[f'rng{inner_round_number}']}\n{debug_data_dec[f'rng{inner_round_number}']}\n\n"
            f"rng7:\n{debug_data_enc['rng7']}\n{debug_data_dec['rng7']}\n\n"
            f"i1_masked:\n{debug_data_enc['i1_masked']}\n{debug_data_dec['i1_masked']}\n\n"
            f"i2_masked:\n{debug_data_enc['i2_masked']}\n{debug_data_dec['i2_masked']}\n\n"
            f"swap:\n{debug_data_enc['swap']}\n{debug_data_dec['swap']}\n\n"
            f"plaintext:\n{debug_data_enc['i1']}\n{debug_data_dec['plaintext']}\n\n"
            f"ciphertext:\n{debug_data_enc['ciphertext']}\n{debug_data_dec['ciphertext']}\n"
            f"-------------------------------\n\n"
        )