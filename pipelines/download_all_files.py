import os
import stat
import warnings
from urllib.request import urlopen

import paramiko
from azure.storage.blob import BlobServiceClient, ContentSettings
from cryptography.utils import CryptographyDeprecationWarning

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)

# Config
host = os.environ["FTP_HOST"]
port = int(os.environ.get("FTP_PORT", 22))
username = os.environ["FTP_USER"]
password = os.environ["FTP_PASS"]

account_url = "https://imb0chd0dev.blob.core.windows.net"
container_name = "projects"
sas_token = os.environ["DSCI_AZ_BLOB_DEV_SAS_WRITE"]


def connect_sftp():
    transport = paramiko.Transport((host, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    print("Connected to sftp server:", host)
    return sftp, transport


def connect_blob():
    blob_service_client = BlobServiceClient(
        account_url=account_url, credential=sas_token
    )
    print("Connected to blob service:", account_url)
    return blob_service_client.get_container_client(container_name)


def upload_blob(container_client, blob_path, local_path):
    with open(local_path, "rb") as f:
        content_type = "application/octet-stream"
        container_client.upload_blob(
            name=blob_path,
            data=f,
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type),
        )
        print("Uploaded:", blob_path)


def download_and_upload_dir(
    sftp, container_client, remote_path, local_dir="temp"
):
    os.makedirs(local_dir, exist_ok=True)
    for item in sftp.listdir_attr(remote_path):
        item_path = remote_path.rstrip("/") + "/" + item.filename
        if stat_is_dir(item.st_mode):
            download_and_upload_dir(
                sftp, container_client, item_path, local_dir
            )
        else:
            local_file = os.path.join(local_dir, item.filename)
            print("Downloading:", item_path)
            sftp.get(item_path, local_file)

            blob_path = item_path.lstrip("/")
            full_blob_path = f"ds-cma-datasharing/cma_ftp/{blob_path}"
            upload_blob(container_client, full_blob_path, local_file)

            os.remove(local_file)


def stat_is_dir(st_mode):
    return stat.S_ISDIR(st_mode)


if __name__ == "__main__":
    print("=== Starting download_all_files.py pipeline ===")
    print("Public IP:", urlopen("https://api.ipify.org").read().decode())

    sftp, transport = connect_sftp()
    container_client = connect_blob()

    download_and_upload_dir(sftp, container_client, "/")

    sftp.close()
    transport.close()
    print("=== Finished download_all_files.py pipeline ===")
