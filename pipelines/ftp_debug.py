import socket


def check_tcp_connectivity(host: str, port: int, timeout: float = 5.0):
    print(f"Trying to connect to {host}:{port}...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        try:
            sock.connect((host, port))
            print(f"SUCCESS: Able to connect to {host}:{port}")
        except socket.timeout:
            print(f"TIMEOUT: No response from {host}:{port}")
        except socket.error as e:
            print(f"ERROR: Could not connect to {host}:{port} — {e}")


if __name__ == "__main__":
    # Replace with your target IP and port
    check_tcp_connectivity("210.73.54.91", 21)
    check_tcp_connectivity("210.73.54.91", 22)
