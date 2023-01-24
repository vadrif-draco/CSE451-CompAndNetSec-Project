import socket
import pickle
from typing import Tuple, Union
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

HOST = "10.0.0.4"
PORT = 10100

def __generate_private_key() -> rsa.RSAPrivateKey:
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    return private_key
    

def __get_public_key(private_key: rsa.RSAPrivateKey) -> bytes:
    return private_key.public_key() \
                .public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)


def send_public_key(conn: socket) -> rsa.RSAPrivateKey:
    private_key = __generate_private_key()
    public_key = __get_public_key(private_key)

    conn.send(pickle.dumps(public_key))        
    
    return private_key


def get_filename(conn: socket) -> str:
    filename_bytes = conn.recv(1024)
    filename = filename_bytes.decode()
    conn.send(b"ACK")
    return filename


def __decode_line(line: bytes, private_key: rsa.RSAPrivateKey) -> bytes:
    decrypted = private_key.decrypt(
        line,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted


def receive_master_key(filename: str, private_key: rsa.RSAPrivateKey, conn: socket) -> None:
    file_path = f"/home/test/ftp/{filename}-master.keys"
    try:
        while True:
            key = conn.recv(4096)
            line = pickle.loads(key)
            if not line or line == "END":
                break
            with open(file_path, "wb") as file:
                file.write(__decode_line(line, private_key))
            conn.send(b"ACK")
    except Exception as e:
        print(e)
        

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
                    private_key = send_public_key(conn)
                elif message == b"FNAM":
                    filename = get_filename(conn)
                elif message == b"MKEY":
                    receive_master_key(filename, private_key, conn)
                