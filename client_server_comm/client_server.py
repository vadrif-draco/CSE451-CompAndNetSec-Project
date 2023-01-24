import socket
import pickle
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

HOST = "172.174.106.14"
PORT = 10100

def __init_connection() -> rsa.RSAPublicKey:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.send(b"INIT")
        public_key = pickle.loads(s.recv(2048))

        return public_key
    

def __send_filename(filename: str) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            s.send(b"FNAM")
            ack = s.recv(4)
            if ack == b"ACK":
                s.send(filename.encode())
        except:
            return
        

def __send_file(filename: str, public_key: rsa.RSAPublicKey) -> None:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
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
                    s.send(pickle.dumps(ciphertext))
                    while True:
                        ack = s.recv(4)
                        if ack == b"ACK":
                            break
                s.send(b"END")
    except Exception as e:
        print(e)


def __send_master_key(filename: str, public_key: rsa.RSAPublicKey) -> None:
    file = f"{filename}-master.keys"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.send(b"MKEY")
        ack = s.recv(4)
        if ack == b"ACK":
            __send_file(file, public_key)


def send_master_key(filename: str) -> None:
    public_key = __init_connection()

    __send_filename(filename)

    __send_master_key(filename, public_key)