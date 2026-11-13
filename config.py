# Konfigurasi bersama TCP & UDP (workload HARUS sama)
TCP_PORT = 5001
UDP_PORT = 5002
NUM_MESSAGES = 100      # jumlah pesan yang dikirim
MSG_SIZE = 64           # ukuran payload per pesan (byte)
UDP_TIMEOUT = 1.0       # detik, UDP dianggap loss jika tidak ada balasan


def make_payload(seq: int, size: int = MSG_SIZE) -> bytes:
    """Payload deterministik: '000001|AAAA...' sepanjang `size` byte."""
    head = f"{seq:06d}|".encode()
    return head + b"A" * (size - len(head))
