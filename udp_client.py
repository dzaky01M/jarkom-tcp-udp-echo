import argparse
import csv
import socket
import time
from config import UDP_PORT, NUM_MESSAGES, MSG_SIZE, UDP_TIMEOUT, make_payload


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=UDP_PORT)
    a = ap.parse_args()

    rows, ok, bad, lost = [], 0, 0, 0
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:    # UDP (tanpa handshake)
        s.settimeout(UDP_TIMEOUT)
        start = time.perf_counter()
        for i in range(1, NUM_MESSAGES + 1):
            msg = make_payload(i)
            t1 = time.perf_counter()
            s.sendto(msg, (a.host, a.port))
            try:
                reply, _ = s.recvfrom(65535)
                rtt = (time.perf_counter() - t1) * 1000
                good = reply == msg
                ok += good
                bad += not good
                rows.append((i, round(rtt, 4), "OK" if good else "CORRUPT"))
            except socket.timeout:
                lost += 1
                rows.append((i, "", "LOST"))
        total = time.perf_counter() - start

    with open("results_udp.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["seq", "rtt_ms", "status"])
        w.writerows(rows)

    rtts = [r[1] for r in rows if r[1] != ""]
    bytes_sent = NUM_MESSAGES * MSG_SIZE
    print(
        f"[UDP] pesan OK/rusak/hilang: {ok}/{bad}/{lost} dari {NUM_MESSAGES}")
    if rtts:
        print(
            f"[UDP] RTT min/avg/max: {min(rtts):.3f} / {sum(rtts)/len(rtts):.3f} / {max(rtts):.3f} ms")
    print(
        f"[UDP] throughput   : {bytes_sent*8/total/1e6:.4f} Mbps (payload, {total:.4f} s)")


if __name__ == "__main__":
    main()
