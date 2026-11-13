import argparse
import socket
from config import UDP_PORT


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=UDP_PORT)
    a = ap.parse_args()

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:    # UDP
        s.bind((a.host, a.port))
        print(f"[UDP server] listening di {a.host}:{a.port}")
        count = 0
        while True:
            data, addr = s.recvfrom(65535)
            s.sendto(data, addr)   # echo
            count += 1
            if count % 100 == 0:
                print(f"[UDP server] {count} datagram di-echo")


if __name__ == "__main__":
    main()
