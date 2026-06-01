import logging
import mimetypes
import os
import stat
import sys
import time
import warnings
from urllib.request import urlopen

import paramiko
from azure.storage.blob import BlobServiceClient, ContentSettings
from cryptography.utils import CryptographyDeprecationWarning

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)
warnings.filterwarnings(
    "ignore", message="You are using cryptography on a 32-bit.*"
)
warnings.filterwarnings("ignore", message="Blowfish has been deprecated")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    stream=sys.stdout,
)
log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.getLogger().setLevel(getattr(logging, log_level, logging.INFO))
logger = logging.getLogger(__name__)

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
    logger.info("Connected to sftp server: %s", host)
    return sftp, transport


def connect_blob():
    blob_service_client = BlobServiceClient(
        account_url=account_url, credential=sas_token
    )
    logger.info("Connected to blob service: %s", account_url)
    return blob_service_client.get_container_client(container_name)


def upload_blob(container_client, blob_path, local_path):
    with open(local_path, "rb") as f:
        content_type, _ = mimetypes.guess_type(local_path)
        if content_type is None:
            content_type = "application/octet-stream"
        container_client.upload_blob(
            name=blob_path,
            data=f,
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type),
        )
        logger.info("Uploaded: %s | Content-Type: %s", blob_path, content_type)


def list_sftp_tree(sftp, path, indent=0):
    for item in sftp.listdir_attr(path):
        item_path = os.path.join(path, item.filename).replace("\\", "/")
        logger.debug("%s- %s", "  " * indent, item.filename)
        if stat_is_dir(item.st_mode):
            list_sftp_tree(sftp, item_path, indent + 1)


def download_and_upload_dir(
    sftp, container_client, remote_path, local_dir="temp"
):
    """Returns (downloaded, skipped) counts."""
    os.makedirs(local_dir, exist_ok=True)
    downloaded = 0
    skipped = 0
    for item in sftp.listdir_attr(remote_path):
        item_path = remote_path.rstrip("/") + "/" + item.filename
        if stat_is_dir(item.st_mode):
            sub_dl, sub_sk = download_and_upload_dir(
                sftp, container_client, item_path, local_dir
            )
            downloaded += sub_dl
            skipped += sub_sk
        else:
            blob_path = item_path.lstrip("/")
            full_blob_path = f"ds-cma-datasharing/cma_ftp/{blob_path}"
            blob_client = container_client.get_blob_client(full_blob_path)
            if blob_client.exists():
                logger.debug("Skipping existing blob: %s", full_blob_path)
                skipped += 1
                continue

            local_file = os.path.join(local_dir, item.filename)
            logger.debug("Downloading: %s", item_path)
            sftp.get(item_path, local_file)

            try:
                upload_blob(container_client, full_blob_path, local_file)
                downloaded += 1
            finally:
                try:
                    os.remove(local_file)
                except OSError as e:
                    logger.warning(
                        "Failed to delete temporary file %s: %s", local_file, e
                    )
    return downloaded, skipped


def stat_is_dir(st_mode):
    return stat.S_ISDIR(st_mode)


if __name__ == "__main__":
    sys.stdout.flush()
    time.sleep(2)
    logger.info("=== Starting download_all_files.py pipeline ===")
    logger.info(
        "Public IP: %s", urlopen("https://api.ipify.org").read().decode()
    )

    sftp, transport = connect_sftp()
    container_client = connect_blob()

    logger.debug("--- Remote SFTP directory listing ---")
    list_sftp_tree(sftp, "/")
    logger.debug("--- End of directory listing ---")

    start = time.monotonic()
    downloaded, skipped = download_and_upload_dir(sftp, container_client, "/")
    elapsed = int(time.monotonic() - start)

    sftp.close()
    transport.close()
    logger.info(
        "=== Finished -- downloaded: %d, skipped: %d, elapsed: %ds ===",
        downloaded,
        skipped,
        elapsed,
    )
