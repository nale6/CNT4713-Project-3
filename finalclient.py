from socket import *
import sys
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import hashlib
#from Crypto.Hash import SHA256


def generate_keypair():
    private_key = RSA.generate(2048)
    public_key = private_key.publickey()
    return private_key, public_key.export_key()

def send_with_length(sock, data_bytes):
    length = len(data_bytes).to_bytes(4, byteorder="big")
    sock.sendall(length + data_bytes)

def recv_exact(sock, num_bytes):
    data = b""
    while len(data) < num_bytes:
        packet = sock.recv(num_bytes - len(data))
        if not packet:
            return None
        data += packet
    return data

def recv_with_length(sock):
    length_bytes = recv_exact(sock, 4)
    if not length_bytes:
        return None
    length = int.from_bytes(length_bytes, byteorder="big")
    return recv_exact(sock, length)

def encrypt_message(message_bytes, public_key_bytes):
    public_key = RSA.import_key(public_key_bytes)
    cipher_rsa = PKCS1_OAEP.new(public_key)
    return cipher_rsa.encrypt(message_bytes)

def decrypt_message(ciphertext, private_key):
    cipher_rsa = PKCS1_OAEP.new(private_key)
    return cipher_rsa.decrypt(ciphertext)

def compute_sha256(message_bytes):
    h = hashlib.sha256(message_bytes)
    return h.hexdigest().encode()

def main():
    print("Starting client...")
    print("Creating RSA keypair")
    client_private_key, client_public_key = generate_keypair()
    print("RSA keypair created")

    HOST = "127.0.0.1"
    PORT = 8080
    connected = False
    dataConnection = None
    server_public_key = None
    original_message = b""

    print("Creating client socket")
    client = socket(AF_INET, SOCK_STREAM)

    try:
        print("Connecting to server")
        client.connect((HOST, PORT))
        connected = True
    except:
        print("Unable to connect to server.")
        sys.exit()

    counter = 0

    while connected:
        counter += 1
        if(counter == 1):
            command = "connect"
        elif(counter == 2):
            command = "tunnel"
        elif(counter == 3):
            command = "post"
        elif(counter == 4):
            command = "quit"
        # command = input("Enter a command: ").strip()

        client.sendall(command.encode())

        match command:
            case "quit":
                # print("Quitting client.")
                message = client.recv(1024).decode()
                # print(message)

                if dataConnection:
                    dataConnection.close()
                client.close()
                break

            case "connect":
                print("Creating data socket")
                port = int(client.recv(1024).decode().strip())

                dataConnection = socket(AF_INET, SOCK_STREAM)
                try:
                    dataConnection.connect((HOST, port))
                except:
                    print("Unsuccessful data socket connection")

            case "tunnel":
                print("Requesting tunnel")

                # send client public key on data socket
                send_with_length(dataConnection, client_public_key)

                # receive server public key on data socket
                server_public_key = recv_with_length(dataConnection)

                print("Server public key received")
                print("Tunnel established")

            case "post":
                print("Post requested.")
                
                firstmsg = input("Encrypting message: ").strip()
                original_message = f"{firstmsg}".encode()
                # print(f"Encrypting message: {original_message.decode()}")

                encrypted_message = encrypt_message(original_message, server_public_key)
                print(f"Sending encrypted message: {encrypted_message}")

                send_with_length(dataConnection, encrypted_message)

                encrypted_hash = recv_with_length(dataConnection)
                print("Received hash")
                print("Computing hash")

                # decrypt server response using CLIENT private key
                server_hash = decrypt_message(encrypted_hash, client_private_key)
                local_hash = compute_sha256(original_message)

                if server_hash == local_hash:
                    print("Secure")
                else:
                    print("Compromised")

    sys.exit()

main()
