from socket import *
import sys
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import hashlib

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

def decrypt_message(ciphertext, private_key):
    cipher_rsa = PKCS1_OAEP.new(private_key)
    return cipher_rsa.decrypt(ciphertext)

def encrypt_message(message_bytes, public_key_bytes):
    public_key = RSA.import_key(public_key_bytes)
    cipher_rsa = PKCS1_OAEP.new(public_key)
    return cipher_rsa.encrypt(message_bytes)

def compute_sha256(message_bytes):
    h = hashlib.sha256(message_bytes)
    return h.hexdigest().encode()

def main():
    HOST = "127.0.0.1"
    PORT = 8080

    server = socket(AF_INET, SOCK_STREAM)

    print("Starting server...")

    server.bind((HOST, PORT))

    print("Creating RSA keypair")
    server_private_key, server_public_key = generate_keypair()
    print("RSA keypair created")

    print("Creating server socket")
    server.listen(1)

    print("Awaiting connections...")

    running = True
    dataConnection = None
    client_public_key = None

    while running:
        connection, address = server.accept()

        while True:
            data = connection.recv(1024)
            if not data:
                break

            command = data.decode().strip()

            match command:
                case "quit":
                    running = False
                    connection.send("Shutting down server".encode())

                    if dataConnection:
                        dataConnection.close()
                    connection.close()
                    server.close()
                    break

                case "connect":
                    print("Connection requested. Creating data socket")

                    dataSocket = socket(AF_INET, SOCK_STREAM)
                    dataSocket.bind((HOST, 0))
                    dataSocket.listen(1)

                    port = dataSocket.getsockname()[1]
                    connection.sendall(f"{port}\n".encode())

                    dataConnection, dataAddress = dataSocket.accept()

                case "tunnel":
                    print("Tunnel requested. Sending public key")

                    client_public_key = recv_with_length(dataConnection)

                    send_with_length(dataConnection, server_public_key)

                case "post":
                    print("Post requested.")

                    encrypted_message = recv_with_length(dataConnection)
                    print(f"Received encrypted message: {encrypted_message}")

                    decrypted_message = decrypt_message(encrypted_message, server_private_key)
                    print(f"Decrypted message: {decrypted_message.decode()}")

                    print("Computing hash")
                    message_hash = compute_sha256(decrypted_message)

                    encrypted_hash = encrypt_message(message_hash, client_public_key)

                    print(f"Responding with hash: {message_hash.decode()}")
                    send_with_length(dataConnection, encrypted_hash)

    sys.exit()

main()
