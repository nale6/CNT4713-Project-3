from socket import *
import sys

#TODO key/pair function, encryption/decryption function logic, display secure/compromised correctly, answers to question and video
#FUNCTIONALITY: Run server first in one terminal (python server.py or click run) and in another terminal run client (python client.py) and client will connect to server.

def main():
  #Local host for address (can also be empty), port 8080 as per project instructions
  HOST = '127.0.0.1'
  PORT = 8080

  #Set up server. For server, need to bind, listen and finally accept
  server = socket(AF_INET, SOCK_STREAM)

  print("Starting server...")

  #Bind server to host address and port number. For AF_INET (ipv4) address family this uses host address and port number.
  server.bind((HOST, PORT))

  print("Creating RSA keypair")
  #TODO keypair here
  print("RSA keypair created")

  server.listen(1)

  print("Awaiting connections...")

  running = True

  while running:
    #accept function returns pair of connection and address
    connection, address = server.accept()
    #Need while loop here to continuously receive data from client until system gets quit out
    #Not sure if quit functionality is needed
    while True:
      data = connection.recv(1024)
      if not data: break

      #Decode sent client command
      command = data.decode()

      #Switch case
      match command:
        #If quit, turn overall while loop boolean to false, close connection and server and break out from current while loop
        #Not asked by the project but convenient to have while using input for commands for now.
        #TODO consider whether to delete this later and automate process or ask if should be automated. If deleted then at another point will need to close connection and server before end of program.
        case "quit":
          if command == "quit":
            running = False
            print("Shutting down")
            connection.send("Shutting down server".encode())
            connection.close()
            server.close()
            break
        #If connect, server will create a new data socket and send an open port number to client for client to create a data socket connection with
        case "connect":
            print("Connection requested. Creating data socket")
            #Create socket object for data connection and eventually data transfer
            dataSocket = socket()
            #Port number 0 will use a random open port number, which is what will be sent
            #We do address + port bind here because AF_INET address family (ipv4) uses host port as arguments
            dataSocket.bind(("127.0.0.1", 0))
            dataSocket.listen(1)
            #Getsockname returns own address, including port, which is why we take the second
            #Again, socket family AF_INET dictates (host, port) as parameters and this is what is returned with getsockname, hence the second value (index 1) being the port
            port = dataSocket.getsockname()[1]
            #Send to client port number. Newline to stop data being sent after port number, that's the only thing we want.
            connection.sendall(f"{port}\n".encode())
            #Data connection with socket and address returned from accept for future commands tunnel and post data transfer
            dataConnection, dataAddress = dataSocket.accept()

        case "tunnel":
          print("Tunnel requested. Sending public key")
          #TODO tunnel server code

        case "post":
          print("Post requested.")
          #TODO post code

      #Generic response. TODO Delete later. Just here to make sure while loop makes it to end and program isn't hanging up on something.
      print("Client says:", command)

  sys.exit()

main()