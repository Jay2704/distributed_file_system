import socket
import threading
import random
import json


class Main_Server:


    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.metadata_lock = threading.Lock()
        self.chunk_servers = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((ip, port))
        self.server_socket.listen(5)
        print(f"Master Server listening on {ip}:{port}")



    def update_primary(self):
        # Randomly select a Chunk Server as primary
        if self.chunk_servers:
            previous_primary_server_id = None
            if any(data['is_primary'] for data in self.chunk_servers.values()):
                previous_primary_server_id = next(
                    (chunk_server_id for chunk_server_id, data in self.chunk_servers.items() if data['is_primary']),
                    None
                )

            primary_server_id = random.choice(list(self.chunk_servers.keys()))

            with self.metadata_lock:
                # Update previous primary server to False
                if previous_primary_server_id is not None:
                    self.chunk_servers[previous_primary_server_id]['is_primary'] = False

                # Update the new primary server to True
                self.chunk_servers[primary_server_id]['is_primary'] = True

            print(f"Primary Server updated. New Primary Server: Chunk Server {primary_server_id}")



    def register_chunk_server(self, chunk_server_id, chunk_server_ip, chunk_server_port):
        is_primary = not bool(self.chunk_servers)  # First one is primary, adjust this based on your criteria

        with self.metadata_lock:
            self.chunk_servers[chunk_server_id] = {
                'ip': chunk_server_ip,
                'port': chunk_server_port,
                'is_primary': is_primary,
                'files': {},
            }
        print(f"Chunk Server {chunk_server_id} registered.")
        self.update_primary()  # Update primary after registration
        self.print_metadata()  # Print metadata after registration


    def print_metadata(self):
        with self.metadata_lock:
            print("\nMaster Server Metadata:")
            primary_server_id = None
            for chunk_server_id, data in self.chunk_servers.items():
                print(f"\n\nChunk Server {chunk_server_id}:")
                print(f"  IP: {data['ip']}")
                print(f"  Port: {data['port']}")
                print(f"  Primary: {data['is_primary']}")
                print(f"  Files: {data['files']}")
                print("\n\n")
                if data['is_primary']:
                    primary_server_id = chunk_server_id

            if primary_server_id is not None:
                print(f"Primary Server: Chunk Server {primary_server_id}")
            else:
                print("No primary server selected yet.")

            print("Chunk Servers Dictionary:")
            print(self.chunk_servers)



    def handle_client(self, client_socket):
        try:
            # Accept the connection from the Chunk Server
            message = client_socket.recv(1024).decode()

            if message == "FIND_PRIMARY_SERVER":
                # Handle the FIND_PRIMARY_SERVER request
                self.find_primary_server(client_socket)
            elif message.startswith("REGISTER_CHUNK_SERVER"):
                # Handle the REGISTER_CHUNK_SERVER request
                jay, chunk_server_id, chunk_server_ip, chunk_server_port = message.split(":")
                chunk_server_id = int(chunk_server_id)
                chunk_server_port = int(chunk_server_port)
                self.register_chunk_server(chunk_server_id, chunk_server_ip, chunk_server_port)
                self.update_primary()  # Update primary after registration
                self.print_metadata()  # Print metadata after registration
            elif message.startswith("CHUNK_SERVER_INFO"):
                # Handle CHUNK_SERVER_INFO message from Chunk Server
                self.handle_chunk_server_info(message)
            else:
                print(f"Invalid message from client: {message}")

        except Exception as e:
            print(f"Error handling client: {e}")

        # finally:
        #     # Close the client socket
        #     client_socket.close()



    def handle_chunk_server_info(self, message):
        # Process information sent by Chunk Server
        val, chunk_server_id, file_name = message.split(":")
        chunk_server_id = int(chunk_server_id)

        if chunk_server_id in self.chunk_servers:
            with self.metadata_lock:
                self.chunk_servers[chunk_server_id]['files'][file_name] = True
                self.save_metadata()  # Save metadata directly after updating

            print(f"Received file info from Chunk Server {chunk_server_id}: {file_name}")
        else:
            print(f"Invalid Chunk Server ID in file info: {chunk_server_id}")



    def find_primary_server(self, client_socket):
        # Implement logic to find and send information about the primary server
        # For now, let's just print a message
        print("FIND_PRIMARY_SERVER request received. Responding with primary server info.")
        primary_server_id = None
        for chunk_server_id, data in self.chunk_servers.items():
            ip = data['ip']
            port = data['port']
            
            if data['is_primary']:
                primary_server_id = chunk_server_id
                break

        primary_server_info = f"PRIMARY_SERVER_INFO:{ip},{port}" if primary_server_id is not None else "PRIMARY_SERVER_INFO:No primary server selected yet."
        client_socket.send(primary_server_info.encode())



    def start(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"Accepted connection from {addr[0]}:{addr[1]}")

            # Start a new thread to handle the client
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()

if __name__ == "__main__":
    master_server = Main_Server("127.0.0.1", 5011)
    master_server.start()
