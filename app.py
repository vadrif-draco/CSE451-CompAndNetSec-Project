import numpy as np
from gui import main
from ftp import ftp_client
from crypto import des, aes128, custom, util, round_robin_crypto


def round_robin_crypto_jpg_test():
    encrypted_file_bits = round_robin_crypto.encrypt_file(
        util.File("test_files\\tux-linux-logo-original.jpg"),
        key_des=np.array([0] * 64),
        key_aes128=np.zeros((128,), dtype=np.uint8),
        key_custom=np.zeros((128,), dtype=np.uint8)
    )

    encrypted_file = util.File.create_file("test_files\\tux-linux-logo-encrypted.jpg", encrypted_file_bits)

    round_robin_crypto.decrypt_file(
        encrypted_file,
        output_file_path="test_files\\tux-linux-logo-decrypted.jpg",
        key_des=np.array([0] * 64),
        key_aes128=np.zeros((128,), dtype=np.uint8),
        key_custom=np.zeros((128,), dtype=np.uint8)
    )


def round_robin_crypto_txt_test():
    encrypted_file_bits = round_robin_crypto.encrypt_file(
        util.File("test_files\\test-document-original.txt"),
        key_des=np.array([0] * 64),
        key_aes128=np.zeros((128,), dtype=np.uint8),
        key_custom=np.zeros((128,), dtype=np.uint8)
    )

    encrypted_file = util.File.create_file("test_files\\test-document-encrypted.txt", encrypted_file_bits)

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
    print(np.packbits(np.hsplit(cipher, 8)))
    print(np.packbits(np.hsplit(recovered_plaintext, 8)))


def aes128_test_zeros():
    message = np.zeros((128,), dtype=np.uint8)
    key = np.zeros((128,), dtype=np.uint8)

    cipher = aes128.encrypt(message, key)
    print(np.packbits(np.hsplit(cipher, 8)))
    print(np.packbits(np.hsplit(aes128.decrypt(cipher, key), 8)))


def custom_algo_internal_test():
    custom.test()


def custom_algo_test_zeros():
    message = np.zeros((64,), dtype=np.uint8)
    key = np.zeros((128,), dtype=np.uint8)
    cipher = custom.encrypt(message, key)
    recovered_message = custom.decrypt(cipher, key)
    print("plaintext:", np.packbits(np.hsplit(message, 8)))
    print("ciphertext:", np.packbits(np.hsplit(cipher, 8)))
    print("recovered:", np.packbits(np.hsplit(recovered_message, 8)))


def custom_algo_avalanche_effect_test():
    message = np.zeros((64,), dtype=np.uint8)
    key = np.zeros((128,), dtype=np.uint8)
    message[63] = 1
    key[127] = 1
    cipher = custom.encrypt(message, key)
    recovered_message = custom.decrypt(cipher, key)
    np.set_printoptions(formatter={'int': hex})  # To print in hex
    print("plaintext:", np.packbits(np.hsplit(message, 8)))
    print("ciphertext:", np.packbits(np.hsplit(cipher, 8)))
    print("recovered:", np.packbits(np.hsplit(recovered_message, 8)))


if __name__ == "__main__":
    # -------------------- GUI --------------------
    # main.start()

    # -------------------- FTP --------------------
    # ftp_client.upload("C:\\Users\\Administrator\\Desktop\\7amada_out.txt", "7amada.txt")
    # ftp_client.download("C:\\Users\\Administrator\\Desktop\\7amada_in.txt", "7amada.txt")

    # ------------- RoundRobin Crypto -------------
    round_robin_crypto_jpg_test()
    round_robin_crypto_txt_test()

    # To print in hex
    np.set_printoptions(formatter={'int': hex})

    print("\n-------------------- DES --------------------\n")
    des_test_zeros()

    print("\n-------------------- AES --------------------\n")
    aes128_test_zeros()

    print("\n---------------- CUSTOM ALGO ----------------\n")
    custom_algo_internal_test()
    custom_algo_test_zeros()
    custom_algo_avalanche_effect_test()

    # To reset printing to its default
    np.set_printoptions()
