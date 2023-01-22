import numpy as np
import custom_tables as tables
import util


def make_rngs(subkeys):
    rngs = []
    for subkey in subkeys:
        rngs.append(np.random.RandomState(subkey))

    return rngs


def swap_bits(i1, i2, shift_size):
    I1_MASK = tables.I1_MASKS[shift_size]
    I2_MASK = tables.I2_MASKS[shift_size]

    i1_masked = np.bitwise_and(i1, I1_MASK)
    i2_masked = np.bitwise_and(i2, I2_MASK)

    return np.bitwise_or(np.left_shift(i1_masked, shift_size), np.right_shift(i2_masked, shift_size))


def round(i1, round_number, rngs):
    shift_size = round_number%7

    rng = util.dec_val_to_bin_vec(rngs[7].randint(low=0, high=2**64, dtype=np.uint64), min_width=64)

    i2 = np.bitwise_xor(i1, rng)

    swap = swap_bits(i1, i2, shift_size)

    round_result = np.bitwise_xor(swap, rngs[shift_size].randint(low=0, high=2**64, dtype=np.uint64))
    print(f"i1: {i1}\n\n"
          f"i2: {i2}\n\n"
          f"rng: {rng}\n\n"
          f"swap: {swap}\n\n"
          f"round_result: {round_result}")
    

key = np.array([np.random.choice([0, 1]) for _ in range(256)])
subkeys = np.hsplit(key, 8)
print(subkeys[0])
RNGS = make_rngs(subkeys)

round(util.dec_val_to_bin_vec(RNGS[7].randint(low=0, high=2**64, dtype=np.uint64), min_width=64), 0, RNGS)