# Echo Service: TCP vs UDP (Python 3)

Workload identik di kedua versi (lihat `config.py`): 100 pesan x 64 byte, di-echo oleh server.

## Menjalankan (localhost)
Terminal 1: `python tcp_server.py`
Terminal 2: `python tcp_client.py`

Terminal 1 (setelah TCP selesai): `python udp_server.py`
Terminal 2: `python udp_client.py`

## Menjalankan (LAN, 2 perangkat)
Di server: `python tcp_server.py` / `python udp_server.py`
Di client: `python tcp_client.py --host <IP_SERVER>` / `python udp_client.py --host <IP_SERVER>`

Pastikan firewall mengizinkan port 5001 (TCP) dan 5002 (UDP).

## Output
`results_tcp.csv` dan `results_udp.csv` (seq, rtt_ms, status) untuk grafik di laporan.

## Filter Wireshark
`tcp.port == 5001` dan `udp.port == 5002`
(localhost: capture di interface Loopback / Adapter for loopback traffic)
