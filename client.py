from socket import *
import sys

#TODO key pair function, encryption/decryption function logic, display secure/compromised correctly, answers to question and video
#FUNCTIONALITY: Run server first in one terminal (python server.py or click run) and in another terminal run client (python client.py) and client will connect to server.

def main():
  print("Starting client...")
  print("Creating RSA keypair")
  #TODO keypair
  print("RSA keypair created")

  #Local host for address (can also be empty), port 8080 as per project instructions
  HOST = '127.0.0.1'
  PORT = 8080
  #Setting connected to true for now
  connected = False

  #For client, just need to connect socket

  #On start, need to create public private key pair

  #Ignore this piece of code for now, just testing client server messaging works at all.
  #Initial query for command. 
  # command = input("Please enter a command (connect, tunnel, post): ")

  # if(command == "connect"):
  #   connected = True
  # else:
  #   print("Connection to server must be first made. Please restart and try 'connect' command.")

  print("Creating client socket")
  client = socket(AF_INET, SOCK_STREAM)
  #Try exception block for connection
  try:
    print("Connecting to server")
    client.connect((HOST, PORT))
    connected = True
    # print("Connection successful.")

  except:
    print("Unable to connect to server.")

  while connected:
    #For now if command sent is quit then terminates client and server
    #This is just for pure testing for now and should be removed later
    #TODO remove when program fully finished
    command = input("Enter a command: ")

    client.sendall(command.encode())

    match command:
      #Custom case for quitting just to make testing easier. Not asked for by project.
      #TODO consider to delete later if not using input for command and instead automating process. If deleted then need to close client before end of program.
      case "quit":
        if command == "quit":
          print("Quitting client.")
          message = client.recv(1024).decode()
          print(message)
          client.close()
          break

      case "connect":
        print("Creating data socket")
        #Parse string to int and remove newline with strip as newline is used to cut off the message from server to only send us the port number
        port = int(client.recv(1024).decode().strip())
        #Debug message
        # print("Successfully retrieved port from server. Port: ", port)
        #Form socket object and connect with localhost and the given port number from server for data connection and data transfer
        dataConnection = socket()
        try:
          dataConnection.connect(("127.0.0.1", port))
          # print("Successful data socket connection")
        except:
          print("Unsuccessful data socket connection")

      #TODO case tunnel AND post
      case "tunnel":  
        print("Tunnel requested. Sending public key")
        #TODO tunnel code

      case "post":
        print("Post requested.")
        #TODO post code

    #TODO change comparisons with sha256 hash and make sure it's correct. Compare SHA256 hash of original message and response. This is for secure/compromised section. Can also be function at top.

  sys.exit()

main()