# CSE451-CompAndNetSec-Project
This is the project for the CSE451 Computer and Networks Security course in the Faculty of Engineering, Ain Shams University. In this project, we implement secure file transfer over FTP.


# Demo
Here's a quick demo for a full run of uploading and encrypting a file on the FTP server backend and requesting, downloading, and decrypting it on the client.

https://user-images.githubusercontent.com/55457021/214453350-532f75ba-1a7f-4fd0-ad06-3c44f7a60f7c.mp4


# Our Custom Algorithm

The code has been made to be self-explanatory with regards to our custom cryptography algorithm, so please feel free to go through it. It is heavily based on the use of RNGs and influenced by both DES and AES (for the prior's use of Feistel structures, and the latter's use of simple yet effective substitution-permutation combinations).

The following video summarizes the encryption path of the algorithm for one inner round from its rounds. It is easy to deduce the decryption path from it also.

https://user-images.githubusercontent.com/55457021/214977213-3b416668-e1bb-4164-a5d4-6881d9ab24f1.mp4


*We'll be adding more details to the README document later...*
