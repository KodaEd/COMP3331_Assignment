"""
    Python 3
    Usage: python3 TCPClient3.py localhost 12000
    coding: utf-8
    
    Author: Wei Song (Tutor for COMP3331/9331)
"""
import socket
import sys
import json


# Starts the server
if len(sys.argv) != 2:
    print("\n===== Error usage, python3 client.py SERVER_PORT ======\n")
    exit(0)
serverPort = int(sys.argv[1])
serverHost = "127.0.0.1"
serverAddress = (serverHost, serverPort)

# define a UDP socket for the client side
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def is_valid_credential(text: str):
    return text.isprintable() and len(text) <= 16

while True:
    # Ask for the users password and username
    username = input('Enter username: ')
    password = input('Enter password: ')

    if not is_valid_credential(username) or not is_valid_credential(password):
        print("Authentication failed. Please try again.")
    
    # Define a json
    data = {
        "username": username,
        "password": password,
        "command": "login"
    }

    json_data = json.dumps(data)
    message = json_data.encode('utf-8')
    clientSocket.settimeout(5)

    try:
        # Send JSON data to server
        clientSocket.sendto(message, serverAddress)

        # Wait for response from server
        response, server = clientSocket.recvfrom(1024)

        # Check if response is empty
        print(response)
        if not response:
            print("No response received from server.")
            continue

        response_data: dict = json.loads(response)
        
        if response_data["action"] != "authentication" or response_data["response"] != True:
            print("Authentication failed. Please try again.")
            continue
        
        break
    except socket.timeout:
        # If no response is received within the timeout period
        print("Server could not be reached. Please try again.")
    except Exception as e:
        # Catch all other exceptions and print the error message
        print(f"An unexpected error occurred: {e}")
    

# # build connection with the server and send message to it
# clientSocket.connect(serverAddress)

# while True:
#     message = input("===== Please type any messsage you want to send to server: =====\n")
#     clientSocket.sendall(message.encode())

#     # receive response from the server
#     # 1024 is a suggested packet size, you can specify it as 2048 or others
#     data = clientSocket.recv(1024)
#     receivedMessage = data.decode()

#     # parse the message received from server and take corresponding actions
#     if receivedMessage == "":
#         print("[recv] Message from server is empty!")
#     elif receivedMessage == "user credentials request":
#         print("[recv] You need to provide username and password to login")
#     elif receivedMessage == "download filename":
#         print("[recv] You need to provide the file name you want to download")
#     else:
#         print("[recv] Message makes no sense")
        
#     ans = input('\nDo you want to continue(y/n) :')
#     if ans == 'y':
#         continue
#     else:
#         break

# close the socket
clientSocket.close()