from socket import *
from threading import Thread
import sys, json
from ServerManager import ServerManager
from datetime import datetime


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


class ServerThread(Thread):
    def __init__(self, clientAddress, message, manager: ServerManager):
        Thread.__init__(self)
        self.clientAddress = clientAddress
        self.message: dict = json.loads(message)
        self.manager = manager
        
    def run(self):
        if "command" not in self.message:
            print("unkown command")
            return

        command = self.message.get("command")
        print(f"{datetime.now()}: {clientAddress[1]}: Recieved {command} from {auth.get_username_from_ip(clientAddress)}")
        print(self.message)

        if command == "AUTH":
            if self.manager.login(self.message["username"], self.message["password"], clientAddress):
                data = {
                    "response": "OK",
                }
            else:
                data = {
                    "response": "ERR",
                }

        if command == "HBT":
            # Dont need to send anything back
            self.manager.log_heartbeat(clientAddress)
            return

        if command == "LAP":
            data = {
                "response": self.manager.get_active_users_except_client(clientAddress),
            }

        if command == "LPF":
            data = {
                "response": list(self.manager.get_all_published_files())
            }
        
        if command == "PUB":
            self.manager.publish_file(self.message["content"], clientAddress)
            data = {
                "response": "OK"
            }

        serverSocket.sendto(json.dumps(data).encode('utf-8'), self.clientAddress)








        # print("Received data from", self.clientAddress, self.message)



    def process_login(self):
        response = json.dumps({"action": "authentication", "response": True})
        print("[send] " + response)
        serverSocket.sendto(response.encode(), self.clientAddress)


print("\n===== UDP Server is running =====")
print("===== Waiting for client requests... =====")

auth = ServerManager()
while True:
    # Wait to receive data from any client
    data, clientAddress = serverSocket.recvfrom(1024)
    # Start a new thread to handle the client's request
    clientThread = ServerThread(clientAddress, data, auth)
    clientThread.start()
