import socket
import threading

class Client:
    def __init__(self, ip, port, client_id):
        self.ip = ip
        self.port = port
        self.client_id = client_id
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.master_server_address = ("127.0.0.1", 5011)
        self.primary_server = None
        self.connect_to_master_server()

    def connect_to_master_server(self):
        try:
            self.client_socket.connect(self.master_server_address)
            print(f"Client {self.client_id} connected to Master Server on {self.master_server_address[0]}:{self.master_server_address[1]}")
        except Exception as e:
            print(f"Error connecting to Master Server: {e}")
            exit(1)

    def send_request(self, request):
        try:
            self.client_socket.send(request.encode())
            response = self.client_socket.recv(1024).decode()
            print(f"Response for client {self.client_id}: {response}")
            return response
        except Exception as e:
            print(f"Error sending/receiving data: {e}")
            exit(1)

    def receive_messages(self):
        try:
            while True:
                message = self.client_socket.recv(1024).decode()
                print(f"Message from server: File Blocked you are in the Queue!")
                exit(0)
        except Exception as e:
            print(f"Error receiving messages: {e}")

    def find_primary_server(self):
        request = "FIND_PRIMARY_SERVER"
        response = self.send_request(request)
        print(response)
        if response.startswith("PRIMARY_SERVER_INFO:"):
            
            primary_info = response.split(":")[1]
            primary_data = primary_info.split(",")
            
            if len(primary_data) == 2:
               
                primary_ip, primary_port = primary_data
                try:
                    self.primary_server = (primary_ip, int(primary_port))
                    print(f"Client {self.client_id} found primary server at {self.primary_server[0]}:{self.primary_server[1]}")
                    return True
                except ValueError as ve:
                    print(f"Error parsing primary server address: {ve}")
            else:
                print(f"Invalid PRIMARY_SERVER_INFO format: {primary_info}")
        else:
            print(f"Unexpected response: {response}")

        return False

    def connect_to_primary_server(self):
        if self.primary_server:
            try:
                self.client_socket.close()  # Close connection to the master server
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect(self.primary_server)
                print(f"Client {self.client_id} connected to Primary Server on {self.primary_server[0]}:{self.primary_server[1]}")
                return True
            except Exception as e:
                print(f"Error connecting to Primary Server: {e}")

        return False

    def create_file(self):
        try:
            file_name = input("Enter file name: ")
            request = f"CREATE_FILE:{file_name}"
            self.send_request(request)
        except Exception as e:
            print(f"Error creating file: {e}")
            exit(1)

    def write_file(self):
        try:
            file_name = input("Enter file name: ")
            content = input("Enter content: ")
            request = f"WRITE_FILE:{file_name}:{content}"
            self.send_request(request)
        except Exception as e:
            print(f"Error writing file: {e}")
            exit(1)

    def read_file(self):
        try:
            file_name = input("Enter file name: ")
            request = f"READ_FILE:{file_name}"
            self.send_request(request)
        except Exception as e:
            print(f"Error reading file: {e}")
            exit(1)

    def delete_file(self):
        try:
            file_name = input("Enter file name: ")
            request = f"DELETE_FILE:{file_name}"
            self.send_request(request)
        except Exception as e:
            print(f"Error deleting file: {e}")
            exit(1)

    def handle_operations(self):
        try:
            print(f"Client {self.client_id} connected to Master Server.")
            if self.find_primary_server():
                if self.connect_to_primary_server():
                    message_thread = threading.Thread(target=self.receive_messages)
                    message_thread.start()

                    while True:
                        print("\nOperations:")
                        print("1. Create File")
                        print("2. Write to File")
                        print("3. Read File")
                        print("4. Delete File")
                        print("5. Exit")

                        choice = input("Enter your choice (1-5): ")

                        if choice == "1":
                            self.create_file()
                        elif choice == "2":
                            self.write_file()
                        elif choice == "3":
                            self.read_file()
                        elif choice == "4":
                            self.delete_file()
                        elif choice == "5":
                            print(f"Client {self.client_id} exiting...")
                            break
                        else:
                            print("Invalid choice. Please enter a number between 1 and 5.")
                else:
                    print("Failed to connect to the primary server.")
            else:
                print("Failed to find the primary server.")
                
        except Exception as e:
            print(f"Error in handle_operations: {e}")
            exit(1)

    def start(self):
        operation_thread = threading.Thread(target=self.handle_operations)
        operation_thread.start()

if __name__ == "__main__":
    client = Client("127.0.0.1", 5011, 1)
    client.start()
