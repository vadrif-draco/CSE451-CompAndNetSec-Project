import numpy as np
from gui import main
from crypto import des
from crypto import custom
from ftp import ftp_client

if __name__ == "__main__":
    # main.start()
    # print(des.encrypt([
    #     0, 0, 0, 0,
    #     0, 0, 0, 0,
    #     0, 0, 0, 0,
    #     0, 0, 0, 0,
    #     0, 0, 0, 0,
    #     0, 0, 0, 0,
    #     0, 0, 0, 0,
    #     0, 0, 0, 0,
    #     0, 0, 0, 0,
    #     0, 0, 0, 0,
    #     0, 0, 0, 0,
    #     0, 0, 0, 0,
    #     0, 0, 0, 0,
    #     0, 0, 0, 0,
    #     0, 0, 0, 0,
    #     0, 0, 0, 0
    # ], [
    #     0, 0, 0, 0,
    #     0, 0, 0, 0,
    #     0, 0, 0, 0,
    #     0, 0, 0, 0,
    #     0, 0, 0, 0,
    #     0, 0, 0, 0,
    #     0, 0, 0, 0,
    #     0, 0, 0, 0,
    #     0, 0, 0, 0,
    #     0, 0, 0, 0,
    #     0, 0, 0, 0,
    #     0, 0, 0, 0,
    #     0, 0, 0, 0,
    #     0, 0, 0, 0,
    #     0, 0, 0, 0,
    #     0, 0, 0, 0
    # ]))
    # ftp_client.upload("C:\\Users\\Administrator\\Desktop\\7amada_out.txt", "7amada.txt")
    # ftp_client.download("C:\\Users\\Administrator\\Desktop\\7amada_in.txt", "7amada.txt")

    custom.test()
    message = np.array([
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
    ])
    key = np.array([
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    ])
    cipher = custom.encrypt(message, key)
    recovered_message = custom.decrypt(cipher, key)
    np.set_printoptions(formatter={'int': hex})  # To print in hex
    print("plaintext:", np.packbits(np.hsplit(message, 8)))
    print("ciphertext:", np.packbits(np.hsplit(cipher, 8)))
    print("recovered:", np.packbits(np.hsplit(recovered_message, 8)))
    np.set_printoptions()  # To reset printing to its default

    message = np.array([
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 1,
    ])
    key = np.array([
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    ])
    cipher = custom.encrypt(message, key)
    recovered_message = custom.decrypt(cipher, key)
    np.set_printoptions(formatter={'int': hex})  # To print in hex
    print("plaintext:", np.packbits(np.hsplit(message, 8)))
    print("ciphertext:", np.packbits(np.hsplit(cipher, 8)))
    print("recovered:", np.packbits(np.hsplit(recovered_message, 8)))
    np.set_printoptions()  # To reset printing to its default
