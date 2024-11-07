import socket
import sys
import json
import time
from threading import Thread
import os

class HeartbeatClient(Thread):
    def __init__(self, clientSocket: socket.socket, serverAddress: tuple[str, int]):
        super().__init__()
        self.clientSocket = clientSocket
        self.serverAddress = serverAddress
        self.message = json.dumps({"command": "HBT"}).encode('utf-8')
    
    def run(self):
        while True:
            try:
                # Send the message to the server
                self.clientSocket.sendto(self.message, self.serverAddress)
            except Exception as e:
                print(f"Error Failed to send heartbeat: {e}")
            time.sleep(2)

class CommandClient(Thread):
    def __init__(self, udpClient: socket.socket, tcpClient: socket.socket, serverAddress: tuple[str, int]):
        super().__init__()
        self.udpClient = udpClient
        self.tcpClient = tcpClient
        self.serverAddress = serverAddress
    
    def run(self):
        while True:
            userInput = input("> ")
            processedInput = userInput.split(" ")
            if len(processedInput) > 2 or len(processedInput) <= 0:
                raise#TODO fix this shit

            command, *extra = processedInput
            extra = extra[0] if extra else None
            
            if command == "lap":
                data = self.udpClient.sendto(json.dumps({"command": "LAP"}).encode('utf-8'), self.serverAddress)
                response, server =  self.udpClient.recvfrom(1024)
                response_data: dict = json.loads(response)
                print(response_data)
                if len(response_data["response"]) <= 0:
                    print("No active peers")
                else:
                    print(f"{len(response_data["response"])} active peers:")
                    for i in response_data["response"]:
                        print(i)

            if command == "lpf":
                self.udpClient.sendto(json.dumps({"command": "LPF"}).encode('utf-8'), self.serverAddress)
                response, server =  self.udpClient.recvfrom(1024)
                response_data: dict = json.loads(response)
                if len(response_data["response"]) <= 0:
                    print("No files published")
                else:
                    print(f"{len(response_data["response"])} file published:")
                    for i in response_data["response"]:
                        print(i)

            if command == "pub":
                self.udpClient.sendto(json.dumps({"command": "PUB", "content": extra}).encode('utf-8'), self.serverAddress)
                response, server =  self.udpClient.recvfrom(1024)
                response_data: dict = json.loads(response)
                if response_data["response"] == "OK":
                    print("File published successfully")
                else:
                    print("File publication failed")

            if command == "unp":
                self.udpClient.sendto(json.dumps({"command": "UNP", "content": extra}).encode('utf-8'), self.serverAddress)
                response, server =  self.udpClient.recvfrom(1024)
                response_data: dict = json.loads(response)
                if response_data["response"] == "OK":
                    print("File unpublished successfully")
                else:
                    print("File unpublication failed")
            
            if command == "sch":
                self.udpClient.sendto(json.dumps({"command": "SCH", "content": extra}).encode('utf-8'), self.serverAddress)
                response, server =  self.udpClient.recvfrom(1024)
                response_data: dict = json.loads(response)
                if len(response_data["response"]) <= 0:
                    print("No files found")
                else:
                    print(f"{len(response_data["response"])} file found:")
                    for i in response_data["response"]:
                        print(i)
            
            if command == "get":
                # get it from the server
                self.udpClient.sendto(json.dumps({"command": "GET", "content": extra}))

                # wait for a response from the server
                response, server =  self.udpClient.recvfrom(1024)
                response_data: dict = json.loads(response)
                peerPort = response_data["response"]
                if not peerPort:
                    raise #TODO somrthing
                try:
                    self.tcpClient.connect(("127.0.0.1", peerPort))
                    # TODO ENSURE THE FILES ARE CORRECT
                    self.tcpClient.sendall(json.dumps({"command": "GET", "filename": extra}).encode('utf-8'))

                    cwd = os.getcwd()

                    with open(cwd + "/" + extra, "wb") as file:
                        while True:
                            data = self.tcpClient.recv(1024)
                            if not data:
                                break
                            file.write(data)
                except Exception as e:
                    print(f"Error: {e}")
                print(f"{extra} downloaded successfully")
                # then get it from the peers

class RequestHandler(Thread):
    def __init__(self, tcpSocket: socket, address: tuple[str, int]):
        super().__init__()
        self.connection = tcpSocket
        self.address = address
    
    def run(self):
        try:
            request_data = self.connection.recv(1024).decode('utf-8')
            request: dict = json.loads(request_data)
            filename = request.get("filename")

            if request.get("command") == "GET" and filename:
                    cwd = os.getcwd()
                    with open(cwd + "/" + filename, "rb") as file:
                        while chunk := file.read(1024):
                            self.connection.sendall(chunk)
                    print(f"File {filename} sent to {self.address}")
        finally:
            self.connection.close()


class RequestListener(Thread):
    def __init__(self, tcpSocket: socket):
        super().__init__()
        self.socket = tcpSocket
    
    def run(self):
        while True:
            # Accept new connections
            connection, address = self.socket.accept()
            print(f"Accepted connection from {address}")
            # Spawn a new thread to handle the file request
            handler = RequestHandler(connection, address)
            handler.start()






# Starts the server
if len(sys.argv) != 2:
    print("\n===== Error usage, python3 client.py SERVER_PORT ======\n")
    exit(0)
serverPort = int(sys.argv[1])
serverHost = "127.0.0.1"
serverAddress = (serverHost, serverPort)

# define a UDP socket for the client side
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udpClientSocket:

    def is_valid_credential(text: str):
        return text.isprintable() and len(text) <= 16

    # Login procedour, 
    while True:
        # Ask for the users password and username
        username = input('Enter username: ')
        password = input('Enter password: ')

        if not is_valid_credential(username) or not is_valid_credential(password):
            print("Authentication failed. Please try again.")
        
        # Define the json
        data = {
            "command": "AUTH",
            "username": username,
            "password": password,
        }

        json_data = json.dumps(data)
        message = json_data.encode('utf-8')
        udpClientSocket.settimeout(5)

        try:
            # Send JSON data to server
            udpClientSocket.sendto(message, serverAddress)

            # Wait for response from server
            response, server = udpClientSocket.recvfrom(1024)

            # Check if response is empty
            print(response)
            if not response:
                print("No response received from server.")
                continue

            response_data: dict = json.loads(response)
            if response_data["response"] != "OK":
                print("Authentication failed. Please try again.")
                continue

            break
        except socket.timeout:
            # If no response is received within the timeout period
            print("Server could not be reached. Please try again.")
        except Exception as e:
            # Catch all other exceptions and print the error message
            print(f"An unexpected error occurred: {e}")

    # Create 3 threads:
    #   - Client Commands
    #   - Recieving Connections
    #   - Heartbeat
    print("Welcome to BitTrickle!")
    print("Available commands are: get, lap, lpf, pub, sch, unp, xit")

    heartbeat = HeartbeatClient(udpClientSocket, serverAddress)
    command = CommandClient(udpClientSocket, udpClientSocket, serverAddress)
    heartbeat.start()
    command.start()

    heartbeat.join()
    command.join()

    udpClientSocket.settimeout(5)