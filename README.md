# CSE451-CompAndNetSec-Project
This is the project for the CSE451 Computer and Networks Security course in the Faculty of Engineering, Ain Shams University. In this project, we implement secure file transfer over FTP.


# Summary of Operation
1. We have content that we wish to transfer via vanilla FTP securely
2. We obtain a master key unique to us, to be used by us for encrypting our own content before transfer
3. The content is split into `N` parts where `N = content size in bytes / 16` such that these parts are cycled in a round robin fashion through three block cipher cryptography algorithms **_that we implemented from scratch_** which are our custom algorithm, DES, and AES (128-bit key version). Parts are either split in two into our custom algorithm and DES (which both take 8 bytes of input plaintext) or taken as a whole by AES (for 16 byte plaintext input).
4. We apply PKCS5 padding in this process and use ECB for the block cipher mode of operation
5. The three algorithms use keys that are randomly generated on the fly, which are then concatenated into one entity and encrypted with the master key with AES 256-bit with PKCS7 padding and ECB mode of operation.
6. Now we have two files: An encrypted data file and an encrypted keys file.
7. For the data file, we simply invoke the STOR command to store it on the vanilla FTP server.
8. For the keys file, we request the public certificate of the FTP server such that we encrypt the master key with it using RSA, then upload that to the FTP server.
9. On the receiving end, to request a file a user must first request the master key, and they do so by sending their public certificate to the FTP server such that it can be encrypted and sent to the user to decrypt at their end.
10. As for the data file, it is afterwards fetched with a RETR command then decrypted using the keys that would be unconcatenated and decrypted using the master key obtained in the previous step.

Note that the FTP server can be hosted on one of the clients ends or as a separate node (which the case in our project as we deployed the server over an **_Azure VM_**) while still being secure in both cases.

**Here is another representation of the operational summary through a collaboration diagram for any two clients and a server:**

![image](https://user-images.githubusercontent.com/55457021/215184179-5b9b1318-298b-4f04-9dc9-40fb78de6248.png)

**And here is a sequence diagram for the exchange protocol for the master key:**

![image](https://user-images.githubusercontent.com/55457021/215184458-785884fa-84df-42fe-9e24-3c25170f2841.png)

Note that lots of socket programming went into the master key exchange protocol, and we also devised an exchange protocol for the data and keys files, but did not use it since we are using FTP anyway.


# Demo
Here's a quick demo for a full run of uploading and encrypting a file on the FTP server backend and requesting, downloading, and decrypting it on the client.

https://user-images.githubusercontent.com/55457021/214453350-532f75ba-1a7f-4fd0-ad06-3c44f7a60f7c.mp4


# Our Custom Algorithm
The code has been made to be self-explanatory with regards to our custom cryptography algorithm, so please feel free to go through it. It is heavily based on the use of RNGs and influenced by both DES and AES (for the prior's use of Feistel structures, and the latter's use of simple yet effective substitution-permutation combinations).

The following video summarizes the encryption path of the algorithm for one inner round from its rounds. It is easy to deduce the decryption path from it also.

https://user-images.githubusercontent.com/55457021/214977213-3b416668-e1bb-4164-a5d4-6881d9ab24f1.mp4


# Tests
- `ftp_test` just tests raw file list retrieval from the FTP server and a dummy upload.
- `round_robin_crypto_jpg_test` tests the encryption and decryption of a `.jpg` image (Linux's Tux!) using the round robin algorithm.
- `round_robin_crypto_txt_test` tests the encryption and decryption of a `.txt` file using the round robin algorithm.
- `des_test_zeros` tests DES encryption and decryption of a block of zeros (check if plaintext recovery is ok and cross-check ciphertext with external tool).
- `aes128_test_zeros` tests AES encryption and decryption of a block of zeros (check if plaintext recovery is ok and cross-check ciphertext with external tool).
- `custom_algo_internal_test` invokes the `internal_test` of our custom algorithm which prints out a very verbose log of each round and its inner rounds through the encryption and decryption processes of a randomly generated block of plaintext and randomly generated seed key.
- `custom_algo_test_zeros` tests our custom algorithm's encryption and decryption of a block of zeros (check if plaintext recovery is ok).
- `custom_algo_avalanche_effect_test` tests all-zeros, one-bit-flip in message, and one-bit-flip in key to demonstrate the strength of the custom algorithm's avalanche effect.
- `custom_algo_avalanche_effect_test2` is a stronger test than the previous one, encrypting 1000 different plaintexts and comparing each to get the minimum, maximum, mean, and median statistics of no. of bits changed between every two consecutive ciphertexts, again to demonstrate the strength of the custom algorithm's avalanche effect.
- In the GUI, there's an `Uunsecure Upload` button to test the integration of the FTP server in the backend with the file browse and upload GUI in the frontend without performing any encryption along the way.


# GUI
The GUI was made using `ttkbootstrap` which is a wrapper around the `tkinter` library for python.


# Dependencies
The following libraries and tool were used:
- `python-ftp-server` for hosting the FTP server.
- `ftplib` for the FTP client code.
- `ttkbootstrap` and `tkinter` for the GUI.
- `os` for browsing file to upload / folder to download.
- `threading` for multi-threaded GUI to avoid hanging during encryption / decryption / upload / download / file list retrievel.
- `numpy` for the implementation of DES, AES128, our custom algorithm, and the round robin crypto algorithm.
- `pickle` and `socket` for socket programming for master key exchange protocol.
- `pycryptodome` and `pyca/cryptography` for AES256 (to encrypt/decrypt the master key) and RSA (for client-server asymmetric cryptography), respectively.
