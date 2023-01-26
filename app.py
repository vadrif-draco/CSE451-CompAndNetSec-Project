import numpy as np
from gui import main
from ftp import ftp_client
from crypto import des, aes128, custom, util, round_robin_crypto
from Crypto.Cipher import AES


def start_gui():

    master_key = None

    try:
        temp_master_key = np.array(np.fromfile("MASTER_KEY")).tobytes()
        AES.new(temp_master_key, AES.MODE_ECB)
        master_key = temp_master_key

    except Exception as ex:
        print(ex)

    main.start(master_key)


def ftp_test():
    print(ftp_client.get_file_list())
    ftp_client.upload("test_files\\test-document.txt")


def round_robin_crypto_jpg_test():
    encrypted_file = round_robin_crypto.encrypt_file(
        util.File("test_files\\tux-linux-logo.jpg"),
        output_file_path="test_files\\tux-linux-logo-encrypted.jpg",
        key_des=np.array([0] * 64),
        key_aes128=np.zeros((128,), dtype=np.uint8),
        key_custom=np.zeros((128,), dtype=np.uint8)
    )

    round_robin_crypto.decrypt_file(
        encrypted_file,
        output_file_path="test_files\\tux-linux-logo-decrypted.jpg",
        key_des=np.array([0] * 64),
        key_aes128=np.zeros((128,), dtype=np.uint8),
        key_custom=np.zeros((128,), dtype=np.uint8)
    )


def round_robin_crypto_txt_test():
    encrypted_file = round_robin_crypto.encrypt_file(
        util.File("test_files\\test-document.txt"),
        output_file_path="test_files\\test-document-encrypted.txt",
        key_des=np.array([0] * 64),
        key_aes128=np.zeros((128,), dtype=np.uint8),
        key_custom=np.zeros((128,), dtype=np.uint8)
    )

    round_robin_crypto.decrypt_file(
        encrypted_file,
        output_file_path="test_files\\test-document-decrypted.txt",
        key_des=np.array([0] * 64),
        key_aes128=np.zeros((128,), dtype=np.uint8),
        key_custom=np.zeros((128,), dtype=np.uint8)
    )


def des_test_zeros():
    key = np.array([0] * 64)
    message = np.array([0] * 64)
    cipher = des.encrypt(message, key)
    recovered_plaintext = des.decrypt(cipher, key)
    print(np.packbits(cipher))
    print(np.packbits(recovered_plaintext))


def aes128_test_zeros():
    message = np.zeros((128,), dtype=np.uint8)
    key = np.zeros((128,), dtype=np.uint8)

    cipher = aes128.encrypt(message, key)
    print(np.packbits(cipher))
    print(np.packbits(aes128.decrypt(cipher, key)))


def custom_algo_internal_test():
    custom.internal_test()


def custom_algo_test_zeros():
    message = np.zeros((64,), dtype=np.uint8)
    key = np.zeros((128,), dtype=np.uint8)
    cipher = custom.encrypt(message, key)
    recovered_message = custom.decrypt(cipher, key)
    print("plaintext:", np.packbits(message))
    print("ciphertext:", np.packbits(cipher))
    print("recovered:", np.packbits(recovered_message))


def custom_algo_avalanche_effect_test():
    print("All zeros")
    message = np.zeros((64,), dtype=np.uint8)
    key = np.zeros((128,), dtype=np.uint8)
    cipher = custom.encrypt(message, key)
    recovered_message = custom.decrypt(cipher, key)
    print("key:", np.packbits(key))
    print("plaintext:", np.packbits(message))
    print("recovered:", np.packbits(recovered_message))
    print("ciphertext:", np.packbits(cipher))

    print("\nOne bit flip in message")
    message_1bit_changed = message.copy()
    message_1bit_changed[np.random.randint(0, 64)] = 1
    cipher = custom.encrypt(message_1bit_changed, key)
    recovered_message = custom.decrypt(cipher, key)
    print("key:", np.packbits(key))
    print("plaintext:", np.packbits(message_1bit_changed))
    print("recovered:", np.packbits(recovered_message))
    print("ciphertext:", np.packbits(cipher))

    print("\nOne bit flip in key")
    key_1bit_changed = key.copy()
    key_1bit_changed[np.random.randint(0, 128)] = 1
    cipher = custom.encrypt(message, key_1bit_changed)
    recovered_message = custom.decrypt(cipher, key_1bit_changed)
    print("key:", np.packbits(key_1bit_changed))
    print("plaintext:", np.packbits(message))
    print("recovered:", np.packbits(recovered_message))
    print("ciphertext:", np.packbits(cipher))


def custom_algo_avalanche_effect_test2(num_of_tests=1000):
    print("")
    ciphers = np.zeros((num_of_tests, 64), dtype=int)
    key = np.random.randint(0, 2, 128)
    for i in range(num_of_tests):
        print(f"Avalanche effect test2: {i+1}/{num_of_tests} encryptions done", end="\r")
        message = np.array(util.dec_val_to_bit_vec(i, 64), dtype=np.uint8)
        ciphers[i] = custom.encrypt(message, key)
    print("")
    diffs = np.zeros((num_of_tests - 1,), dtype=np.uint8)
    for i in range(1, num_of_tests):
        diffs[i - 1] = np.sum(np.abs(ciphers[i] - ciphers[i - 1]))

    print(f'Avalanche effect test2: Min diff: {np.min(diffs)}')
    print(f'Avalanche effect test2: Max diff: {np.max(diffs)}')
    print(f'Avalanche effect test2: Mean diff: {np.round(np.mean(diffs), decimals=2)}')
    print(f'Avalanche effect test2: Median diff: {np.median(diffs)}')


if __name__ == "__main__":
    # -------------------- GUI --------------------
    start_gui()

    # -------------------- FTP --------------------
    # ftp_test()

    # ------------- RoundRobin Crypto -------------
    # round_robin_crypto_txt_test()
    # round_robin_crypto_jpg_test()

    # # Print in hex with no line-wrapping
    np.set_printoptions(linewidth=np.inf, formatter={'int': hex})

    # print("\n-------------------- DES --------------------\n")
    # des_test_zeros()

    # print("\n-------------------- AES --------------------\n")
    # aes128_test_zeros()

    # print("\n---------------- CUSTOM ALGO ----------------\n")
    # custom_algo_internal_test()
    # custom_algo_test_zeros()
    # custom_algo_avalanche_effect_test()
    # custom_algo_avalanche_effect_test2()

    # # Reset printing to its default
    np.set_printoptions()
