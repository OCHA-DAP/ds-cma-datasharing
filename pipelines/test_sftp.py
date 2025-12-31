import os
import socket
from urllib.request import urlopen

import paramiko

# Optional: check public IP
public_ip = urlopen("https://api.ipify.org").read().decode()
print("Public IP:", public_ip)

host = os.environ["FTP_HOST"]
user = os.environ["FTP_USER"]
pwd = os.environ["FTP_PASS"]
port = 22  # SFTP default


# Check if the SFTP service is open
def check_sftp_port(ip, port=22, timeout=5):
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            print(f"SFTP port {port} on {ip} is open.")
            return True
    except Exception as e:
        print(f"Error connecting to {ip}:{port} -> {e}")
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
