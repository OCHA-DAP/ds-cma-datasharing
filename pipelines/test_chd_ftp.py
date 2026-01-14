import os
import socket
from ftplib import FTP
from urllib.request import urlopen

# from ftplib import FTP_TLS

public_ip = urlopen("https://api.ipify.org").read().decode()
print("Public IP:", public_ip)

host = os.environ["FTP_HOST"]
user = os.environ["FTP_USER"]
pwd = os.environ["FTP_PASS"]


def check_ftp_banner(ip, port=21, timeout=5):
    try:
        with socket.create_connection((ip, port), timeout=timeout) as sock:
            banner = sock.recv(1024).decode("utf-8", errors="ignore").strip()
            print(f"Connected to {ip}:{port}, banner: {banner}")
            return banner
    except socket.timeout:
        print(f"Timeout connecting to {ip}:{port}")
    except ConnectionRefusedError:
        print(f"Connection refused by {ip}:{port}")
    except Exception as e:
        print(f"Error connecting to {ip}:{port} → {e}")
    return None


ftp_banner = check_ftp_banner(host)

if ftp_banner is None:
    print("Aborting: no FTP server detected at this IP.")
    exit(1)

ftp = FTP()
ftp.set_debuglevel(2)  # Shows command trace
ftp.connect(host, 21, timeout=10)
ftp.login(user, pwd)
print("Login successful")

# ftp = FTP_TLS()
# ftp.connect(host, 21)
# ftp.login(user=user, passwd=pwd)
# ftp.prot_p()  # switch to secure data connection

print("Connected to:", host)
print("Current directory:", ftp.pwd())

print("Top-level files and folders:")
for name in ftp.nlst():
    print(" -", name)

ftp.quit()
