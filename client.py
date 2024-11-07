import socket
import sys
import json
import time
from threading import Thread, Event
import os

stopEvent = Event()

class HeartbeatClient(Thread):
    def __init__(self, clientSocket: socket.socket, serverAddress: tuple[str, int]):
        super().__init__()
        self.clientSocket = clientSocket
        self.serverAddress = serverAddress
        self.message = json.dumps({"command": "HBT"}).encode('utf-8')
    
    def run(self):
        while not stopEvent.is_set():
            try:
                # Send the message to the server
                self.clientSocket.sendto(self.message, self.serverAddress)
            except Exception as e:
                print(f"Error Failed to send heartbeat: {e}")
            time.sleep(2)

class CommandClient(Thread):
    def __init__(self, udpClient: socket.socket, serverAddress: tuple[str, int]):
        super().__init__()
        self.udpClient = udpClient
        self.serverAddress = serverAddress
    
    def run(self):
        while not stopEvent.is_set():
            userInput = input("> ")
            processedInput = userInput.split(" ")
            if len(processedInput) > 2 or len(processedInput) <= 0:
                print("Unkown command: Available commands are: get, lap, lpf, pub, sch, unp, xit")

            command, *extra = processedInput
            extra = extra[0] if extra else None
            
            if command == "lap":
                data = self.udpClient.sendto(json.dumps({"command": "LAP"}).encode('utf-8'), self.serverAddress)
                response, server =  self.udpClient.recvfrom(2048)
                response_data: dict = json.loads(response)
                length = len(response_data["response"])
                if length <= 0:
                    print("No active peers")
                else:
                    print(f"{length} active peers:")
                    for i in response_data["response"]:
                        print(i)

            elif command == "lpf":
                self.udpClient.sendto(json.dumps({"command": "LPF"}).encode('utf-8'), self.serverAddress)
                response, server =  self.udpClient.recvfrom(2048)
                response_data: dict = json.loads(response)
                length = len(response_data["response"])
                if length <= 0:
                    print("No files published")
                else:
                    print(f"{length} file published:")
                    for i in response_data["response"]:
                        print(i)

            elif command == "pub":
                self.udpClient.sendto(json.dumps({"command": "PUB", "content": extra}).encode('utf-8'), self.serverAddress)
                response, server =  self.udpClient.recvfrom(2048)
                response_data: dict = json.loads(response)
                if response_data["response"] == "OK":
                    print("File published successfully")
                else:
                    print("File publication failed")

            elif command == "unp":
                self.udpClient.sendto(json.dumps({"command": "UNP", "content": extra}).encode('utf-8'), self.serverAddress)
                response, server =  self.udpClient.recvfrom(2048)
                response_data: dict = json.loads(response)
                if response_data["response"] == "OK":
                    print("File unpublished successfully")
                else:
                    print("File unpublication failed")
            
            elif command == "sch":
                self.udpClient.sendto(json.dumps({"command": "SCH", "content": extra}).encode('utf-8'), self.serverAddress)
                response, server =  self.udpClient.recvfrom(2048)
                response_data: dict = json.loads(response)
                length = len(response_data["response"])
                if length <= 0:
                    print("No files found")
                else:
                    print(f"{length} file found:")
                    for i in response_data["response"]:
                        print(i)
            
            elif command == "get":
                # get it from the server
                self.udpClient.sendto(json.dumps({"command": "GET", "content": extra}).encode('utf-8'), self.serverAddress)

                # wait for a response from the server
                response, server =  self.udpClient.recvfrom(2048)
                response_data: dict = json.loads(response)
                peerPort = response_data["response"]
                
                if not peerPort or peerPort == "ERR":
                    print("File not found")
                    continue

                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_client:
                        tcp_client.connect(("127.0.0.1", peerPort))
                        tcp_client.sendall(json.dumps({"command": "GET", "filename": extra}).encode('utf-8'))

                        cwd = os.getcwd()
                        with open(os.path.join(cwd, extra), "wb") as file:
                            while True:
                                data = tcp_client.recv(2048)
                                if not data:
                                    break
                                file.write(data)
                        print(f"{extra} downloaded successfully")
                
                except Exception as e:
                    print(f"Error: {e} during file transfer.")

            elif command == "xit":
                print("Goodbye!")
                stopEvent.set()
                break
            else:
                print("Unkown command: Available commands are: get, lap, lpf, pub, sch, unp, xit")
            


class RequestHandler(Thread):
    def __init__(self, tcpSocket: socket, address: tuple[str, int]):
        super().__init__()
        self.connection = tcpSocket
        self.address = address
    
    def run(self):
        try:
            request_data = self.connection.recv(2048).decode('utf-8')
            request: dict = json.loads(request_data)
            filename = request.get("filename")

            if request.get("command") == "GET" and filename:
                    cwd = os.getcwd()
                    with open(cwd + "/" + filename, "rb") as file:
                        while chunk := file.read(2048):
                            self.connection.sendall(chunk)
        finally:
            self.connection.close()


class RequestListener(Thread):
    def __init__(self, tcpSocket: socket.socket):
        super().__init__()
        self.socket = tcpSocket
        self.socket.settimeout(1)
    
    def run(self):
        while not stopEvent.is_set():
            try:
                # accept connection
                connection, address = self.socket.accept()
                # spawn a new thread 
                handler = RequestHandler(connection, address)
                handler.start()
            except TimeoutError:
                continue
            except Exception as e:
                print(f"Error accepting connections: {e}")
                break






# Starts the server
if len(sys.argv) != 2:
    print("\n===== Error usage, python3 client.py SERVER_PORT ======\n")
    exit(0)
serverPort = int(sys.argv[1])
serverHost = "127.0.0.1"
serverAddress = (serverHost, serverPort)

# define a UDP socket for the client side
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udpClientSocket:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcpServerSocket:
        tcpServerSocket.bind(('127.0.0.1', 0))
        tcpServerSocket.listen(5)
        tcpPort = tcpServerSocket.getsockname()[1]

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
                "tcpPort": tcpPort
            }

            json_data = json.dumps(data)
            message = json_data.encode('utf-8')
            udpClientSocket.settimeout(5)

            try:
                udpClientSocket.sendto(message, serverAddress)

                response, server = udpClientSocket.recvfrom(2048)

                if not response:
                    print("No response received from server.")
                    continue

                response_data: dict = json.loads(response)
                if response_data["response"] != "OK":
                    print("Authentication failed. Please try again.")
                    continue

                break
            except socket.timeout:
                print("Server could not be reached. Please try again.")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

        # Create 3 threads:
        #   - Client Commands
        #   - Recieving Connections
        #   - Heartbeat
        print("Welcome to BitTrickle!")
        print("Available commands are: get, lap, lpf, pub, sch, unp, xit")

        heartbeat = HeartbeatClient(udpClientSocket, serverAddress)
        command = CommandClient(udpClientSocket, serverAddress)
        listener = RequestListener(tcpServerSocket)
        heartbeat.start()
        listener.start()
        command.start()

        listener.join()
        heartbeat.join()
        command.join()