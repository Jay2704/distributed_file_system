import socket
import time
import threading

class MasterServer:
    def __init__(self, port, heartbeat_timeout=10):
        self.file_servers = {}  
        self.primary_server_id = None
        self.port = port
        self.heartbeat_timeout = heartbeat_timeout
        self.lock = threading.Lock()

    def handle_heartbeat(self, conn, addr):
        message = conn.recv(1024).decode()
        server_id, role = message.split(":")[1], message.split(":")[2]
        print(f"Received heartbeat from server {server_id} with role {role}")

        # Update the server's last heartbeat timestamp
        with self.lock:
            self.file_servers[server_id] = time.time()

        # Check if the server is the primary server
        if role == "primary":
            self.primary_server_id = server_id

    def monitor_heartbeats(self):
        while True:
            time.sleep(5)
            current_time = time.time()
            for server_id, last_heartbeat in list(self.file_servers.items()):
                if current_time - last_heartbeat > self.heartbeat_timeout:
                    print(f"Server {server_id} failed!")
                    if server_id == self.primary_server_id:
                        print("Primary server failed. Initiating election process.")
                        self.elect_new_primary()

    def elect_new_primary(self):
        with self.lock:
            remaining_servers = [sid for sid in self.file_servers if sid != self.primary_server_id]
            if remaining_servers:
                new_primary = min(remaining_servers) 
                self.primary_server_id = new_primary
                print(f"New primary server is {new_primary}")
                

    def start(self):
        
        threading.Thread(target=self.monitor_heartbeats).start()

        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind(('0.0.0.0', self.port))
            server_socket.listen(5)
            print(f"Master server listening on port {self.port}")

            while True:
                conn, addr = server_socket.accept()
                threading.Thread(target=self.handle_heartbeat, args=(conn, addr)).start()


master_server = MasterServer(port=5000)
master_server.start()
