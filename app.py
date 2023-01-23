import numpy as np
from gui import main
from ftp import ftp_client
from crypto import des, aes128, custom, util, round_robin_crypto

if __name__ == "__main__":
    # -------------------- GUI --------------------
    # main.start()

    # -------------------- FTP --------------------
    # ftp_client.upload("C:\\Users\\Administrator\\Desktop\\7amada_out.txt", "7amada.txt")
    # ftp_client.download("C:\\Users\\Administrator\\Desktop\\7amada_in.txt", "7amada.txt")

    # ------------- RoundRobin Crypto -------------

    encrypted_file_bits = round_robin_crypto.encrypt_file(
        util.File("test\\tux-linux-logo-original.jpg"),
        key_des=np.array([0] * 64),
        key_aes128=np.zeros((128,), dtype=np.uint8),
        key_custom=np.zeros((128,), dtype=np.uint8)
    )

    encrypted_file = util.File.create_file("test\\tux-linux-logo-encrypted.jpg", encrypted_file_bits)

    round_robin_crypto.decrypt_file(
        encrypted_file,
        output_file_path="test\\tux-linux-logo-decrypted.jpg",
        key_des=np.array([0] * 64),
        key_aes128=np.zeros((128,), dtype=np.uint8),
        key_custom=np.zeros((128,), dtype=np.uint8)
    )

    encrypted_file_bits = round_robin_crypto.encrypt_file(
        util.File("test\\test-document-original.txt"),
        key_des=np.array([0] * 64),
        key_aes128=np.zeros((128,), dtype=np.uint8),
        key_custom=np.zeros((128,), dtype=np.uint8)
    )

    encrypted_file = util.File.create_file("test\\test-document-encrypted.txt", encrypted_file_bits)

    round_robin_crypto.decrypt_file(
        encrypted_file,
        output_file_path="test\\test-document-decrypted.txt",
        key_des=np.array([0] * 64),
        key_aes128=np.zeros((128,), dtype=np.uint8),
        key_custom=np.zeros((128,), dtype=np.uint8)
    )

    # ---------------------------------------------
    np.set_printoptions(formatter={'int': hex})  # To print in hex
    # ---------------------------------------------

    # -------------------- DES --------------------
    print("\n-------------------- DES --------------------\n")
    key = np.array([0] * 64)
    message = np.array([0] * 64)
    cipher = des.encrypt(message, key)
    recovered_plaintext = des.decrypt(cipher, key)
    print(np.packbits(np.hsplit(cipher, 8)))
    print(np.packbits(np.hsplit(recovered_plaintext, 8)))

    # -------------------- AES --------------------
    print("\n-------------------- AES --------------------\n")
    message = np.zeros((128,), dtype=np.uint8)
    key = np.zeros((128,), dtype=np.uint8)

    cipher = aes128.encrypt(message, key)
    print(np.packbits(np.hsplit(cipher, 8)))
    print(np.packbits(np.hsplit(aes128.decrypt(cipher, key), 8)))

    # ---------------- CUSTOM ALGO ----------------
    print("\n---------------- CUSTOM ALGO ----------------\n")

    # custom.test()
    message = np.zeros((64,), dtype=np.uint8)
    key = np.zeros((128,), dtype=np.uint8)
    cipher = custom.encrypt(message, key)
    recovered_message = custom.decrypt(cipher, key)
    print("plaintext:", np.packbits(np.hsplit(message, 8)))
    print("ciphertext:", np.packbits(np.hsplit(cipher, 8)))
    print("recovered:", np.packbits(np.hsplit(recovered_message, 8)))

    # Testing for avalanche effect
    message[63] = 1
    key[127] = 1
    cipher = custom.encrypt(message, key)
    recovered_message = custom.decrypt(cipher, key)
    np.set_printoptions(formatter={'int': hex})  # To print in hex
    print("plaintext:", np.packbits(np.hsplit(message, 8)))
    print("ciphertext:", np.packbits(np.hsplit(cipher, 8)))
    print("recovered:", np.packbits(np.hsplit(recovered_message, 8)))

    # ---------------------------------------------
    np.set_printoptions()  # To reset printing to its default
    # ---------------------------------------------
