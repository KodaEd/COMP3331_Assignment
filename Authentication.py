import os
from datetime import datetime, timedelta


class AuthServer:
    def __init__(self):
        credentials_filename='credentials.txt'
        self.credentials = {}
        self.heartbeat = {}
        self.clientAddresses = {}

        # loads the file of credentials
        cwd = os.getcwd()
        try:
            with open(cwd + "/" + credentials_filename, 'r') as file:
                for line in file:
                    line = line.strip()
                    contents = line.split(' ')

                    if len(contents) != 2:
                        print("Invalid Credentials Detected")
                        raise

                    # need to validate the entries
                    username, password = contents
                    if not self.is_valid_credential(username) or not self.is_valid_credential(password):
                        print("Invalid Credentials Detected")
                        raise

                    # add it into the hash map
                    self.credentials[username] = password
                    self.heartbeat[username] = None

        except FileNotFoundError:
            print("Credentials File not found.")
            raise
        except IOError:
            print("Error reading file contents.")
            raise
        return
    
    def login(self, username: str, password: str, ipaddress):
        if self.credentials.get(username) != password:
            return False
        
        self.clientAddresses[ipaddress] = username
        self.heartbeat[username] = datetime.now()
        return True

    def is_valid_credential(self, text: str):
        return text.isprintable() and len(text) <= 16
    
    # Should log the current heartbeat
    def log_heartbeat(self, ipaddress):
        username = self.clientAddresses.get(ipaddress)
        if ipaddress == None:
            raise

        self.heartbeat[username] = datetime.now()
    
    def get_username_from_ip(self, ipaddress):
        return self.clientAddresses.get(ipaddress)
    
    def get_active_users_except_client(self, ipaddress):
        username = self.get_username_from_ip(ipaddress)

        now = datetime.now()
        threshold = now - timedelta(seconds=3)
        recent_users = [user for user, timestamp in self.heartbeat.items() if timestamp and timestamp > threshold]

        recent_users.remove(username)

        return recent_users



