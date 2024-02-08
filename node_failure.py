def send_heartbeat(self):
        while True:
            time.sleep(self.heartbeat_interval)
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as master_socket:
                    master_socket.connect((self.master_ip, self.master_port))
                    heartbeat_message = f"HEARTBEAT:{self.chunk_server_id}"
                    master_socket.send(heartbeat_message.encode())
            except Exception as e:
                print(f"Heartbeat failed: {e}")
                self.is_alive = False
