import os
import ssl
from ftplib import FTP_TLS
from urllib.request import urlopen

HOST = "waws-prod-bn1-055.ftp.azurewebsites.windows.net"
USER = r"DataScienceFTP\ocha-chd-cma"
PASS = os.getenv("FTP_PASSWORD")

LOCAL = "test.txt"
REMOTE_DIR = "/site/wwwroot/files"
REMOTE_NAME = "test.txt"

public_ip = urlopen("https://api.ipify.org").read().decode()
print("Public IP:", public_ip)

# Create the TLS context
ctx = ssl.create_default_context()

ftps = FTP_TLS(context=ctx, timeout=30)
ftps.set_debuglevel(2)  # <- see exact commands/responses
ftps.connect(HOST, 21)  # explicit FTPS
ftps.auth()  # upgrade control channel (AUTH TLS)
ftps.login(USER, PASS)
ftps.prot_p()  # protect/encrypt data channel
ftps.set_pasv(True)  # force PASV (avoid active/PORT)

# Move to target directory (no trailing spaces/backslashes)
ftps.cwd(REMOTE_DIR)

try:
    with open(LOCAL, "rb") as f:
        ftps.storbinary(f"STOR {REMOTE_NAME}", f, blocksize=64 * 1024)
except TimeoutError:
    # Azure FTPS sometimes times out during TLS unwrap after successful upload
    pass

ftps.quit()
print("Upload complete.")
