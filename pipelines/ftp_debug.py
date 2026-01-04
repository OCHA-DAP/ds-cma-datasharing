import socket

# import struct
import time


def traceroute(dest_name, max_hops=30, timeout=2):
    port = 33434
    ttl = 1
    try:
        dest_addr = socket.gethostbyname(dest_name)
    except socket.gaierror:
        print(f"Could not resolve {dest_name}")
        return

    print(f"Traceroute to {dest_name} ({dest_addr}), {max_hops} hops max")

    while ttl <= max_hops:
        recv_socket = socket.socket(
            socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP
        )
        send_socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP
        )
        send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
        recv_socket.settimeout(timeout)

        recv_socket.bind(("", port))
        send_socket.sendto(b"", (dest_name, port))

        curr_addr = None
        try:
            start_time = time.time()
            _, curr_addr = recv_socket.recvfrom(512)
            rtt = (time.time() - start_time) * 1000
            curr_addr = curr_addr[0]
        except socket.error:
            rtt = None
        finally:
            send_socket.close()
            recv_socket.close()

        if curr_addr:
            print(
                f"{ttl:2}  {curr_addr:<15}  {round(rtt, 2) if rtt else '*'} ms"
            )
        else:
            print(f"{ttl:2}  *")

        ttl += 1

        if curr_addr == dest_addr:
            break


# Usage
traceroute("210.73.54.91")
