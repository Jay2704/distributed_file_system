import socket
import time

class FileServer:
    def __init__(self, server_id, role, master_ip, master_port, heartbeat_interval=5):
        self.server_id = server_id
        self.role = role  # ex: primary
        self.master_ip = master_ip
        self.master_port = master_port
        self.heartbeat_interval = heartbeat_interval
        self.is_primary = self.role == 'primary'

    def send_heartbeat(self):
        while True:
            time.sleep(self.heartbeat_interval)
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as master_socket:
                    master_socket.connect((self.master_ip, self.master_port))
                    heartbeat_message = f"HEARTBEAT:{self.server_id}:{self.role}"
                    master_socket.send(heartbeat_message.encode())
            except Exception as e:
                print(f"Failed to send heartbeat from server {self.server_id}: {e}")


file_server = FileServer(server_id=1, role='secondary', master_ip='192.168.1.100', master_port=5000)
file_server.send_heartbeat()
