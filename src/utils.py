import socket
import time


CREATE_NO_WINDOW = 0x08000000


def resolve_addresses(target):
    started = time.perf_counter()
    infos = socket.getaddrinfo(target, None, type=socket.SOCK_STREAM)
    elapsed_ms = round((time.perf_counter() - started) * 1000, 1)
    addresses = []
    seen = set()
    for family, _, _, _, sockaddr in infos:
        ip = sockaddr[0]
        if ip in seen:
            continue
        seen.add(ip)
        addresses.append({
            "ip": ip,
            "family": "IPv6" if family == socket.AF_INET6 else "IPv4",
        })
    return addresses, elapsed_ms
