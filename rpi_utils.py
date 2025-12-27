import socket
import threading
import paramiko
import os
from concurrent.futures import ThreadPoolExecutor

class NetworkScanner:
    def __init__(self):
        self.found_devices = []

    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    def scan_network(self, port=22):
        self.found_devices = []
        local_ip = self.get_local_ip()
        base_ip = ".".join(local_ip.split(".")[:-1])
        
        print(f"Scanning network: {base_ip}.0/24 for port {port}...")

        with ThreadPoolExecutor(max_workers=50) as executor:
            for i in range(1, 255):
                ip = f"{base_ip}.{i}"
                if ip != local_ip:
                    executor.submit(self.check_port, ip, port)
        
        return self.found_devices

    def check_port(self, ip, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((ip, port))
        if result == 0:
            try:
                # Try to get hostname
                hostname = socket.gethostbyaddr(ip)[0]
            except socket.herror:
                hostname = "Unknown"
            
            self.found_devices.append({"ip": ip, "hostname": hostname})
        sock.close()

class SSHClient:
    def __init__(self, ip, username, password):
        self.ip = ip
        self.username = username
        self.password = password
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(self):
        try:
            self.client.connect(self.ip, username=self.username, password=self.password, timeout=5)
            return True
        except Exception as e:
            print(f"SSH Connection Failed: {e}")
            return False

    def sync_code(self, local_path, remote_path="/home/"):
        # This is a simplified sync. For a full folder sync, we'd need to walk the directory.
        # For now, let's assume we are syncing specific files or a zip.
        # But the user asked to "put the code in /home/".
        # I'll implement a recursive SCP or SFTP put.
        
        sftp = self.client.open_sftp()
        
        try:
            # Check if remote_path exists, if not create it (not doing that for /home/ obviously)
            # Assuming remote_path is a directory like /home/pi/project or just /home/pi/
            
            # Let's just sync the current project directory to a folder in remote home
            # But wait, user said "/home/". That's root home usually, or they meant user home "~/"?
            # I'll assume they meant the user's home directory, e.g. /home/username/
            
            remote_base = f"/home/{self.username}/ai_control_code"
            try:
                sftp.mkdir(remote_base)
            except IOError:
                pass # Directory likely exists

            if os.path.isfile(local_path):
                 remote_file = os.path.join(remote_base, os.path.basename(local_path))
                 sftp.put(local_path, remote_file)
            elif os.path.isdir(local_path):
                self._put_dir_recursive(sftp, local_path, remote_base)
                
            return True
        except Exception as e:
            print(f"Sync Failed: {e}")
            return False
        finally:
            sftp.close()

    def _put_dir_recursive(self, sftp, local_dir, remote_dir):
        # Create remote directory
        try:
            sftp.mkdir(remote_dir)
        except IOError:
            pass

        for item in os.listdir(local_dir):
            if item.startswith(".") or item == "__pycache__" or item == "venv" or item == "node_modules":
                continue
                
            local_path = os.path.join(local_dir, item)
            remote_path = os.path.join(remote_dir, item)

            if os.path.isfile(local_path):
                sftp.put(local_path, remote_path)
            elif os.path.isdir(local_path):
                self._put_dir_recursive(sftp, local_path, remote_path)

    def run_command(self, command, wait=True):
        """Run a command on the RPI."""
        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            if not wait:
                return "Command sent", ""
            return stdout.read().decode('utf-8'), stderr.read().decode('utf-8')
        except Exception as e:
            print(f"Command Execution Failed: {e}")
            return None, str(e)

    def start_server(self):
        """Start the RPI server in the background."""
        remote_base = f"/home/{self.username}/ai_control_code"
        
        # 1. Kill any existing server process
        kill_command = "pkill -f rpi_server.py"
        self.run_command(kill_command, wait=True)
        
        # 2. Start the server in the background
        # We use nohup and & to run it in the background
        # We also need to make sure it doesn't wait for stdout/stderr
        command = f"cd {remote_base} && nohup python3 rpi_server.py > server.log 2>&1 &"
        print(f"Starting server with command: {command}")
        return self.run_command(command, wait=False)

    def close(self):
        self.client.close()
