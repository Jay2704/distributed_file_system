import socket
import threading
import random
import json


class Main_Server:
    """
    Master Server for Distributed File System
    
    This class implements the master server functionality that:
    - Manages chunk server registrations
    - Maintains metadata about files and their locations
    - Handles primary server selection and updates
    - Coordinates communication between clients and chunk servers
    """

    def __init__(self, ip, port):
        """
        Initialize the Master Server
        
        Args:
            ip (str): IP address to bind the server to
            port (int): Port number to listen on
        """
        self.ip = ip
        self.port = port
        # Thread lock for thread-safe access to metadata
        self.metadata_lock = threading.Lock()
        # Dictionary to store chunk server information
        # Format: {chunk_server_id: {'ip': str, 'port': int, 'is_primary': bool, 'files': dict}}
        self.chunk_servers = {}
        # Create TCP socket for server communication
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((ip, port))
        self.server_socket.listen(5)  # Allow up to 5 pending connections
        print(f"Master Server listening on {ip}:{port}")

    def update_primary(self):
        """
        Update the primary server selection
        
        This method randomly selects a new primary server from the available chunk servers.
        It ensures only one server is marked as primary at any time.
        """
        # Randomly select a Chunk Server as primary
        if self.chunk_servers:
            previous_primary_server_id = None
            # Find the current primary server if any exists
            if any(data['is_primary'] for data in self.chunk_servers.values()):
                previous_primary_server_id = next(
                    (chunk_server_id for chunk_server_id, data in self.chunk_servers.items() if data['is_primary']),
                    None
                )

            # Randomly select a new primary server
            primary_server_id = random.choice(list(self.chunk_servers.keys()))

            with self.metadata_lock:
                # Update previous primary server to False
                if previous_primary_server_id is not None:
                    self.chunk_servers[previous_primary_server_id]['is_primary'] = False

                # Update the new primary server to True
                self.chunk_servers[primary_server_id]['is_primary'] = True

            print(f"Primary Server updated. New Primary Server: Chunk Server {primary_server_id}")

    def register_chunk_server(self, chunk_server_id, chunk_server_ip, chunk_server_port):
        """
        Register a new chunk server with the master server
        
        Args:
            chunk_server_id (int): Unique identifier for the chunk server
            chunk_server_ip (str): IP address of the chunk server
            chunk_server_port (int): Port number of the chunk server
        """
        # First registered server becomes primary, adjust this based on your criteria
        is_primary = not bool(self.chunk_servers)

        with self.metadata_lock:
            # Store chunk server information in the metadata
            self.chunk_servers[chunk_server_id] = {
                'ip': chunk_server_ip,
                'port': chunk_server_port,
                'is_primary': is_primary,
                'files': {},  # Dictionary to store files managed by this chunk server
            }
        print(f"Chunk Server {chunk_server_id} registered.")
        self.update_primary()  # Update primary after registration
        self.print_metadata()  # Print metadata after registration

    def print_metadata(self):
        """
        Print the current metadata state for debugging and monitoring
        """
        with self.metadata_lock:
            print("\nMaster Server Metadata:")
            primary_server_id = None
            # Iterate through all registered chunk servers
            for chunk_server_id, data in self.chunk_servers.items():
                print(f"\n\nChunk Server {chunk_server_id}:")
                print(f"  IP: {data['ip']}")
                print(f"  Port: {data['port']}")
                print(f"  Primary: {data['is_primary']}")
                print(f"  Files: {data['files']}")
                print("\n\n")
                if data['is_primary']:
                    primary_server_id = chunk_server_id

            # Display primary server information
            if primary_server_id is not None:
                print(f"Primary Server: Chunk Server {primary_server_id}")
            else:
                print("No primary server selected yet.")

            print("Chunk Servers Dictionary:")
            print(self.chunk_servers)

    def handle_client(self, client_socket):
        """
        Handle incoming client connections and messages
        
        Args:
            client_socket: Socket connection to the client
        """
        try:
            # Accept the connection from the Chunk Server
            message = client_socket.recv(1024).decode()

            # Route messages based on their type
            if message == "FIND_PRIMARY_SERVER":
                # Handle the FIND_PRIMARY_SERVER request
                self.find_primary_server(client_socket)
            elif message.startswith("REGISTER_CHUNK_SERVER"):
                # Handle the REGISTER_CHUNK_SERVER request
                # Parse message format: "REGISTER_CHUNK_SERVER:chunk_server_id:ip:port"
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

        # Note: Client socket is kept open for continued communication
        # finally:
        #     # Close the client socket
        #     client_socket.close()

    def handle_chunk_server_info(self, message):
        """
        Process file information sent by chunk servers
        
        Args:
            message (str): Message containing chunk server and file information
                          Format: "CHUNK_SERVER_INFO:chunk_server_id:file_name"
        """
        # Process information sent by Chunk Server
        val, chunk_server_id, file_name = message.split(":")
        chunk_server_id = int(chunk_server_id)

        if chunk_server_id in self.chunk_servers:
            with self.metadata_lock:
                # Update the chunk server's file list
                self.chunk_servers[chunk_server_id]['files'][file_name] = True
                self.save_metadata()  # Save metadata directly after updating

            print(f"Received file info from Chunk Server {chunk_server_id}: {file_name}")
        else:
            print(f"Invalid Chunk Server ID in file info: {chunk_server_id}")

    def find_primary_server(self, client_socket):
        """
        Find and send information about the primary server to the client
        
        Args:
            client_socket: Socket connection to send the response
        """
        # Implement logic to find and send information about the primary server
        print("FIND_PRIMARY_SERVER request received. Responding with primary server info.")
        primary_server_id = None
        
        # Search for the primary server in registered chunk servers
        for chunk_server_id, data in self.chunk_servers.items():
            ip = data['ip']
            port = data['port']
            
            if data['is_primary']:
                primary_server_id = chunk_server_id
                break

        # Send primary server information back to the client
        primary_server_info = f"PRIMARY_SERVER_INFO:{ip},{port}" if primary_server_id is not None else "PRIMARY_SERVER_INFO:No primary server selected yet."
        client_socket.send(primary_server_info.encode())

    def start(self):
        """
        Start the master server and begin listening for connections
        
        This method runs indefinitely, accepting client connections
        and spawning new threads to handle each client.
        """
        while True:
            # Accept incoming connections
            client_socket, addr = self.server_socket.accept()
            print(f"Accepted connection from {addr[0]}:{addr[1]}")

            # Start a new thread to handle the client
            # This allows the server to handle multiple clients concurrently
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()

if __name__ == "__main__":
    # Create and start the master server on localhost port 5011
    master_server = Main_Server("127.0.0.1", 5011)
    master_server.start()
