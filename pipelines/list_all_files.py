import os
import stat

import paramiko

host = os.environ["FTP_HOST"]
user = os.environ["FTP_USER"]
pwd = os.environ["FTP_PASS"]
port = int(os.environ.get("FTP_PORT", 22))

# Connect
transport = paramiko.Transport((host, port))
transport.connect(username=user, password=pwd)
sftp = paramiko.SFTPClient.from_transport(transport)


def list_all(path, indent=0):
    try:
        items = sftp.listdir_attr(path)
    except IOError as e:
        print("  " * indent + f"[ERROR accessing {path}]: {e}")
        return

    for item in items:
        item_path = os.path.join(path, item.filename).replace("\\", "/")
        if stat.S_ISDIR(item.st_mode):
            print("  " * indent + f"[DIR]  {item.filename}/")
            list_all(item_path, indent + 1)
        else:
            print("  " * indent + f"[FILE] {item.filename}")


print("SFTP Directory Tree:")
list_all("/")

sftp.close()
transport.close()
