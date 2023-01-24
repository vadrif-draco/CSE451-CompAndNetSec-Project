import socket
import pickle
from typing import Tuple
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization

HOST = "10.0.0.4"
PORT = 10101

def __send_ack(conn: socket) -> None:
    conn.send(b"ACK")

def receive_public_key(conn: socket) -> rsa.RSAPublicKey:
    public_key = __get_public_key(pickle.loads(conn.recv(4096)))
    conn.send(b"AUTH")
    return public_key
    

def __get_public_key(public_key_bytes):
    return serialization.load_pem_public_key(public_key_bytes)


def get_filename_and_extension(conn: socket) -> Tuple[str, str]:
    filename_and_extension_bytes = conn.recv(1024)
    filename_and_extension_str = filename_and_extension_bytes.decode()
    filename_and_extension = filename_and_extension_str.split("/")
    return filename_and_extension[0], filename_and_extension[1]


def __send_file(filename: str, public_key: rsa.RSAPublicKey, conn: socket) -> None:
    try:
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
                while True:
                    ack = conn.recv(4)
                    if ack == b"ACK":
                        break
            conn.send(b"END")
    except Exception as e:
        print(e)


def send_master_key(filename: str, public_key: rsa.RSAPublicKey, conn: socket) -> None:
    file = f"/home/test/ftp/{filename}-master.keys"
    __send_file(file, public_key, conn)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    while True:
        conn, addr = s.accept()
        with conn:
            while True:
                message = conn.recv(8)
                if not message:
                    break
                if message == b"INIT":
                    __send_ack(conn)
                    public_key = receive_public_key(conn)
                elif message == b"FNEX":
                    __send_ack(conn)
                    filename, extension = get_filename_and_extension(conn)
                elif message == b"MKEY":
                    __send_ack(conn)
                    send_master_key(filename, public_key, conn)
                