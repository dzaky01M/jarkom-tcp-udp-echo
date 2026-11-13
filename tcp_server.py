import argparse
import socket
from config import TCP_PORT, MSG_SIZE


def recv_exact(conn, n):
    """TCP adalah byte stream, jadi baca sampai tepat n byte."""
    buf = b""
    while len(buf) < n:
        chunk = conn.recv(n - len(buf))
        if not chunk:
            return None
        buf += chunk
    return buf


def main():
    ap = argparse.ArgumentParser()
    # 0.0.0.0 agar bisa diakses dari LAN
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=TCP_PORT)
    a = ap.parse_args()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:   # TCP
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((a.host, a.port))
        s.listen()
        print(f"[TCP server] listening di {a.host}:{a.port}")
        while True:
            conn, addr = s.accept()
            print(f"[TCP server] koneksi dari {addr}")
            with conn:
                count = 0
                while (data := recv_exact(conn, MSG_SIZE)) is not None:
                    conn.sendall(data)   # echo
                    count += 1
            print(f"[TCP server] selesai, {count} pesan di-echo")


if __name__ == "__main__":
    main()
