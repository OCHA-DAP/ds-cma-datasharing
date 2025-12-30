import os
from ftplib import FTP

host = os.environ["FTP_HOST"]
user = os.environ["FTP_USER"]
pwd = os.environ["FTP_PASS"]

# Connect to plain FTP (no TLS)
ftp = FTP(host)
ftp.login(user=user, passwd=pwd)

print("✅ Connected to:", host)
print("📁 Current directory:", ftp.pwd())

print("📄 Top-level files and folders:")
for name in ftp.nlst():
    print(" -", name)

ftp.quit()
