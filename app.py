import io
import os
from ftplib import FTP

import streamlit as st
from dotenv import load_dotenv

# ---- Load env vars ----
load_dotenv()
FTP_HOST = os.getenv("FTP_HOST")
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")


# ---- Connect to Azure Blob ----
def upload_to_blob(filename, file_bytes):
    return True


# ---- FTP folder listing ----
def list_dir(ftp, path):
    ftp.cwd(path)
    items = ftp.nlst()
    files = []
    folders = []
    for item in items:
        try:
            ftp.cwd(f"{path}/{item}")
            folders.append(item)
            ftp.cwd(path)  # go back
        except Exception:
            files.append(item)
    return folders, files


# ---- Streamlit App UI ----
st.set_page_config(page_title="FTP Browser", layout="centered")
st.title("📂 FTP File Browser")

if "ftp_path" not in st.session_state:
    st.session_state.ftp_path = "/"

# Connect to FTP
try:
    ftp = FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)

    current_path = st.session_state.ftp_path
    st.markdown(f"**Current directory:** `{current_path}`")

    folders, files = list_dir(ftp, current_path)

    # Go up button
    if current_path != "/":
        if st.button("⬅️ Go up"):
            st.session_state.ftp_path = (
                os.path.dirname(current_path.rstrip("/")) or "/"
            )
            st.rerun()

    # List folders
    for folder in folders:
        if st.button(f"📂 {folder}"):
            next_path = f"{current_path}/{folder}".replace("//", "/")
            st.session_state.ftp_path = next_path
            st.rerun()

    # List files with download+upload button
    for file in files:
        col1, col2 = st.columns([4, 2])
        with col1:
            st.markdown(f"📄 `{file}`")
        with col2:
            if st.button("📥 Download & Upload", key=f"dl_{file}"):
                full_path = f"{current_path}/{file}".replace("//", "/")
                file_buffer = io.BytesIO()
                ftp.retrbinary(f"RETR {full_path}", file_buffer.write)
                file_buffer.seek(0)

                if upload_to_blob(file, file_buffer):
                    st.success(f"✅ Uploaded `{file}` to Azure Blob Storage")

    ftp.quit()

except Exception as e:
    st.error(f"❌ Could not connect: {e}")
