import os

# from ftplib import FTP
from ftplib import FTP_TLS

host = os.environ["FTP_HOST"]
user = os.environ["FTP_USER"]
pwd = os.environ["FTP_PASS"]

# Connect to plain FTP (no TLS)
# ftp = FTP(host)
# ftp.login(user=user, passwd=pwd)

ftp = FTP_TLS()
ftp.connect(host, 21)
ftp.login(user=user, passwd=pwd)
ftp.prot_p()  # switch to secure data connection

print("Connected to:", host)
print("Current directory:", ftp.pwd())

print("Top-level files and folders:")
for name in ftp.nlst():
    print(" -", name)

ftp.quit()
