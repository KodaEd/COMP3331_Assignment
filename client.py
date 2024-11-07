import socket
import sys
import json
import time
from threading import Thread

class HeartbeatClient(Thread):
    def __init__(self, clientSocket: socket, serverAddress: tuple[str, int]):
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
    def __init__(self, udpClient: socket, tcpClient: socket, serverAddress: tuple[str, int]):
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
                response, server = udpClientSocket.recvfrom(1024)
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
                response, server = udpClientSocket.recvfrom(1024)
                response_data: dict = json.loads(response)
                print(response_data)

            if command == "pub":
                self.udpClient.sendto(json.dumps({"command": "PUB", "content": extra}).encode('utf-8'), self.serverAddress)
                response, server = udpClientSocket.recvfrom(1024)
                response_data: dict = json.loads(response)
                print(response_data)





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