import socket
import pickle
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization

HOST = "10.0.0.4"
PORT = 10101

def get_public_key(public_key_bytes):
    return serialization.load_pem_public_key(public_key_bytes)


def send_file(filename, public_key: rsa.RSAPublicKey, conn):
    with open(filename, 'rb') as file:
        for line in file:
            ciphertext = public_key.encrypt(
                line,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            conn.send(pickle.dumps(ciphertext))


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    while True:
        conn, addr = s.accept()
        with conn:
            while True:
                message = conn.recv(2048)
                if not message:
                    break
                key = pickle.loads(message)
                public_key = get_public_key(key)
                send_file("blah.txt", public_key, conn)
                