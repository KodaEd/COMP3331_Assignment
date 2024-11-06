from socket import *
from threading import Thread
import sys, json
from Authentication import AuthServer

# acquire server host and port from command line parameter
if len(sys.argv) != 2:
    print("\n===== Error usage, python3 UDPServer.py SERVER_PORT ======\n")
    exit(0)
serverHost = "127.0.0.1"
serverPort = int(sys.argv[1])
serverAddress = (serverHost, serverPort)

# define a UDP socket for the server
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(serverAddress)

"""
    Define multi-thread class for handling client requests
    Each client request will be handled in a separate thread
"""
class ClientThread(Thread):
    def __init__(self, clientAddress, message, auth: AuthServer):
        Thread.__init__(self)
        self.clientAddress = clientAddress
        print(message)
        self.message: dict = json.loads(message)
        self.auth = auth

        print("===== New connection created for: ", clientAddress)
        
    def run(self):
        if "command" not in self.message:
            print("unkown command")
            return
        
        command = self.message.get("command")

        if command == "login":
            result = auth.login(self.message["username"], self.message["password"])
            data = {
                "action": "authentication",
                "response": result,
            }
            serverSocket.sendto(json.dumps(data).encode('utf-8'), self.clientAddress)




        # print("Received data from", self.clientAddress, self.message)



    def process_login(self):
        response = json.dumps({"action": "authentication", "response": True})
        print("[send] " + response)
        serverSocket.sendto(response.encode(), self.clientAddress)


print("\n===== UDP Server is running =====")
print("===== Waiting for client requests... =====")

auth = AuthServer()
while True:
    # Wait to receive data from any client
    data, clientAddress = serverSocket.recvfrom(1024)
    # Start a new thread to handle the client's request
    clientThread = ClientThread(clientAddress, data, auth)
    clientThread.start()
