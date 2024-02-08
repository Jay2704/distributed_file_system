import socket
import threading
import os
import time



#Using  Object oriented programming


# each object of chunbk server has a ip, port, chunk_server_id, master server ip, master port
class ChunkServer:
    def __init__(self, ip, port, chunk_server_id, master_ip, master_port):
        self.ip = ip
        self.port = port
        self.chunk_server_id = chunk_server_id
        self.master_ip = master_ip
        self.master_port = master_port
        self.chunk_server_directory = f"chunk_server_{chunk_server_id}_directory"
        self.create_chunk_server_directory_if_not_exists()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((ip, port))
        self.server_socket.listen(5)

        # file lock if the file is busy

        self.file_lock = threading.Lock()
        self.locked_files = set()  # Track locked files
        self.timeout = 120
        #printing chunk server
        print(f"Chunk Server {chunk_server_id} listening on {ip}:{port}")

        self.register_with_master()

    def create_chunk_server_directory_if_not_exists(self):
        directory_path = os.path.join(os.getcwd(), self.chunk_server_directory)
        os.makedirs(directory_path, exist_ok=True)
        print(f"Chunk Server {self.chunk_server_id} directory: {directory_path}")


# method to add chunk server to master server data.
    def register_with_master(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((self.master_ip, self.master_port))
            registration_request = f"REGISTER_CHUNK_SERVER:{self.chunk_server_id}:{self.ip}:{self.port}"
            client_socket.send(registration_request.encode())
            response = client_socket.recv(1024).decode()
            print(response)


# updating master server infromation
    def update_master_with_file_info(self, file_name):
        # Send file information to the Master Server
        chunk_server_info = f"CHUNK_SERVER_INFO:{self.chunk_server_id},{file_name}"
        self.send_to_master_server(chunk_server_info)

    def send_to_master_server(self, message):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as master_socket:
            master_socket.connect((self.master_ip, self.master_port))
            master_socket.send(message.encode())


# 
    def handle_client(self, client_socket, addr):
        try:
            print(f"Accepted connection to Chunk Server {self.chunk_server_id} from {addr[0]}:{addr[1]}")

            # Set a timeout of 120 seconds for the socket operations
            client_socket.settimeout(self.timeout)

            request = client_socket.recv(1024).decode()
            print(f"Request received at Chunk Server {self.chunk_server_id}: {request}")

            start_time = time.time()

            if request.startswith("CREATE_FILE:"):
                _, file_name = request.split(":")
                local_file_path = os.path.join(self.chunk_server_directory, file_name)
                # primary_file_path = os.path.join("/path/to/primary/server/directory", file_name)  # Update with the actual path
                # secondary_file_path = os.path.join("/path/to/secondary/server/directory", file_name)  # Update with the actual path

                with self.file_lock:
                    print(f"File lock acquired for CREATE_FILE operation.")
                    
                    # Create the file in the local chunk server directory
                    with open(local_file_path, 'w') as local_file:
                        local_file.write("File created")
                    
                    # Create the file on the primary server
                    # try:
                    #     with open(primary_file_path, 'w') as primary_file:
                    #         primary_file.write("File created")
                    # except Exception as primary_create_error:
                    #     print(f"Error creating file on primary server: {primary_create_error}")

                    # # Create the file on other chunk server directories
                    # try:
                    #     with open(secondary_file_path, 'w') as secondary_file:
                    #         secondary_file.write("File created")
                    # except Exception as secondary_create_error:
                    #     print(f"Error creating file on secondary server: {secondary_create_error}")

                    print(f"File lock released after CREATE_FILE operation.")

                response = "FILE_CREATED"

                # Update meta data
                chunk_server_info = f"CHUNK_SERVER_INFO:{self.chunk_server_id},{file_name}"
                self.send_to_master_server(chunk_server_info)

                client_socket.send(response.encode())
                print("File created successfully.")

            elif request.startswith("WRITE_FILE:"):
                _, file_name, content = request.split(":")
                file_path = os.path.join(self.chunk_server_directory, file_name)
                copy_path = f"/Users/libuser/Desktop/AOS/{file_name}"  # Specify the local directory for the copy

                with self.file_lock:
                    print(f"File lock acquired for WRITE_FILE operation.")
                    if file_name in self.locked_files:
                        print(f"File {file_name} is already locked by another client.")
                        client_socket.send("FILE_LOCKED_ERROR".encode())
                        return

                    # Create a copy of the file in the local directory
                    try:
                        with open(file_path, 'r') as original, open(copy_path, 'w') as local_copy:
                            original_content = original.read()
                            local_copy.write(original_content)
                    except Exception as copy_error:
                        print(f"Error creating local copy: {copy_error}")
                        client_socket.send("COPY_ERROR".encode())
                        return

                    # Update the original file in the chunk server directory
                    with open(file_path, 'w') as file:
                        file.write(content)

                    print(f"File lock released after WRITE_FILE operation.")
                    self.locked_files.remove(file_name)

                response = "FILE_WRITTEN"
                client_socket.send(response.encode())
                print("File written successfully.")

            elif request.startswith("READ_FILE:"):
                _, file_name = request.split(":")
                file_path = os.path.join(self.chunk_server_directory, file_name)

                with self.file_lock:
                    print(f"File lock acquired for READ_FILE operation.")
                    if file_name in self.locked_files:
                        print(f"File {file_name} is already locked by another client.")
                        client_socket.send("FILE_LOCKED_ERROR".encode())
                        return
                    self.locked_files.add(file_name)
                    if os.path.exists(file_path):
                        with open(file_path, 'r') as file:
                            file_content = file.read()
                        response = f"FILE_CONTENT:{file_content}"
                    else:
                        response = "FILE_NOT_FOUND"
                    print(f"File lock released after READ_FILE operation.")
                    self.locked_files.remove(file_name)

                client_socket.send(response.encode())
                print("File content sent.")

            elif request.startswith("DELETE_FILE:"):
                _, file_name = request.split(":")
                file_path = os.path.join(self.chunk_server_directory, file_name)

                with self.file_lock:
                    print(f"File lock acquired for DELETE_FILE operation.")
                    if file_name in self.locked_files:
                        print(f"File {file_name} is already locked by another client.")
                        client_socket.send("FILE_LOCKED_ERROR".encode())
                        return
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        response = "FILE_DELETED"
                    else:
                        response = "FILE_NOT_FOUND"
                    print(f"File lock released after DELETE_FILE operation.")

                client_socket.send(response.encode())
                print("File deleted successfully.")

            else:
                print(f"Invalid request to Chunk Server {self.chunk_server_id}")


            end_time = time.time()
            time_taken = end_time - start_time
            print(f"Time taken to serve the request: {time_taken:.6f} seconds")

        except socket.timeout:
            # Handle socket timeout
            print("Timeout: File access took too long.")
            client_socket.send("TIMEOUT_ERROR".encode())

        except Exception as e:
            print(f"Error handling client request: {e}")

        finally:
            # Reset the socket timeout to its default value
            client_socket.settimeout(None)
            # client_socket.close()

    def start(self):
        while True:
            client_socket, addr = self.server_socket.accept()

            client_handler = threading.Thread(target=self.handle_client, args=(client_socket, addr))
            client_handler.start()

if __name__ == "__main__":
    chunk_server = ChunkServer("127.0.0.1", 6003, 3, "127.0.0.1", 5011)
    chunk_server.start()
