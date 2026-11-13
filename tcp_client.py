import argparse
import csv
import socket
import time
from config import TCP_PORT, NUM_MESSAGES, MSG_SIZE, make_payload
from tcp_server import recv_exact


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=TCP_PORT)
    a = ap.parse_args()

    rows, ok, bad = [], 0, 0
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:   # TCP
        t0 = time.perf_counter()
        # 3-way handshake
        s.connect((a.host, a.port))
        conn_ms = (time.perf_counter() - t0) * 1000

        start = time.perf_counter()
        for i in range(1, NUM_MESSAGES + 1):
            msg = make_payload(i)
            t1 = time.perf_counter()
            s.sendall(msg)
            reply = recv_exact(s, MSG_SIZE)
            rtt = (time.perf_counter() - t1) * 1000
            good = reply == msg
            ok += good
            bad += not good
            rows.append((i, round(rtt, 4), "OK" if good else "CORRUPT"))
        total = time.perf_counter() - start

    with open("results_tcp.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["seq", "rtt_ms", "status"])
        w.writerows(rows)

    rtts = [r[1] for r in rows]
    bytes_sent = NUM_MESSAGES * MSG_SIZE
    print(f"[TCP] connect time : {conn_ms:.3f} ms")
    print(f"[TCP] pesan OK/rusak: {ok}/{bad} dari {NUM_MESSAGES}")
    print(
        f"[TCP] RTT min/avg/max: {min(rtts):.3f} / {sum(rtts)/len(rtts):.3f} / {max(rtts):.3f} ms")
    print(
        f"[TCP] throughput   : {bytes_sent*8/total/1e6:.4f} Mbps (payload, {total:.4f} s)")


if __name__ == "__main__":
    main()
