import socket
import pickle
from typing import Tuple, Union
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

HOST = "172.174.106.14"
PORT = 10101

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


def __generate_private_key() -> rsa.RSAPrivateKey:
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    return private_key
    

def __get_public_key(private_key: rsa.RSAPrivateKey) -> bytes:
    return private_key.public_key() \
                .public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)


def __init_connection() -> Union[rsa.RSAPrivateKey, None]:
    private_key = __generate_private_key()
    public_key = __get_public_key(private_key)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.send(b"INIT")
        ack = s.recv(4)
        if ack == b"ACK":
            s.send(pickle.dumps(public_key))
            auth = s.recv(8)
            if auth == b"AUTH":
                return private_key
        
        return None
    

def __send_filename_and_extension(filename: str, extension: str) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            s.send(b"FNEX")
            ack = s.recv(4)
            if ack == b"ACK":
                s.send(f"{filename}/{extension}".encode())
        except:
            return


def __receive_master_key(filename: str, private_key: rsa.RSAPrivateKey) -> Union[str, None]:
    file_path = f"{filename}-master.keys"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            s.send(b"MKEY")
            ack = s.recv(4)
            if ack == b"ACK":
                while True:
                    key = s.recv(4096)
                    line = pickle.loads(key)
                    if not line or line == "END":
                        break
                    with open(file_path, "ab") as file:
                        file.write(__decode_line(line, private_key))
                    s.send(b"ACK")
                return file_path

            return None
        except:
            return None


def receive_data(filename: str, extension: str) -> Union[str, None]:
    private_key = __init_connection()
    
    if private_key == None:
        return None, None
    
    __send_filename_and_extension(filename, extension)

    ecnrypted_master_key_filename = __receive_master_key(filename, private_key)

    return ecnrypted_master_key_filename
