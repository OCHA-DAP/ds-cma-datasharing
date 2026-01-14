import os
import socket
import time
from urllib.request import urlopen

import paramiko

# Optional: check public IP
public_ip = urlopen("https://api.ipify.org").read().decode()
print("Public IP:", public_ip)

host = os.environ["FTP_HOST"]
user = os.environ["FTP_USER"]
pwd = os.environ["FTP_PASS"]
port = int(os.environ["FTP_PORT"])


def check_sftp_port(ip, port=22, timeout=5):
    print(f"Trying to connect to {ip}:{port} with timeout {timeout}...")
    start = time.time()
    try:
        with socket.create_connection((ip, port), timeout=timeout) as sock:
            duration = time.time() - start
            print(f"Connected successfully in {duration:.2f} seconds.")
            print("Socket family:", sock.family)
            print("Socket type:", sock.type)
            print("Socket proto:", sock.proto)
            print("Peer name:", sock.getpeername())
            return True
    except socket.timeout:
        print(f"Connection to {ip}:{port} timed out.")
    except socket.error as e:
        print(f"Socket error: {e}")
    return False


if not check_sftp_port(host, port):
    print("Aborting: SFTP port not open.")
    exit(1)

# Connect using Paramiko
transport = paramiko.Transport((host, port))
transport.connect(username=user, password=pwd)

sftp = paramiko.SFTPClient.from_transport(transport)
print("Login successful via SFTP")
print("Current directory:", sftp.getcwd())
print("Top-level files and folders:")
for item in sftp.listdir():
    print(" -", item)

sftp.close()
transport.close()
