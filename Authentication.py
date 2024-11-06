import os

class AuthServer:
    def __init__(self):
        credentials_filename='credentials.txt'
        self.credentials = {}

        # loads the file of credentials
        cwd = os.getcwd()
        try:
            with open(cwd + credentials_filename, 'r') as file:
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

        except FileNotFoundError:
            print("Credentials File not found.")
            raise
        except IOError:
            print("Error reading file contents.")
            raise
        return
    
    def login(self, username: str, password: str):
        return self.credentials.get(username) == password

    def is_valid_credential(text: str):
        return text.isprintable() and len(text) <= 16


