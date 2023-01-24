import socket
import pickle
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

HOST = "172.174.106.14"
PORT = 10101

def decode_line(line, private_key):
    print(line)
    return private_key.decrypt(
        line,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    ) 



# Generate the RSA private key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)
public_key = private_key.public_key().public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.send(pickle.dumps(public_key))
    while True:
        line = pickle.loads(s.recv(65536))
        print("hi")
        if not line or line == "STOP":
            break
        with open("blah.txt", "ab") as file:
            file.write(decode_line(line, private_key))
        s.send(b"ACK")