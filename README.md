# Echo Service: TCP vs UDP

Proyek Jaringan Komputer: Project Based Learning 2 (Application Layer dan Transport Layer).

Layanan **Echo Server** (request-response sederhana) diimplementasikan dalam dua versi dengan fungsi dan beban kerja yang identik, lalu dibandingkan menggunakan Wireshark:

| Versi | Socket | Port |
|---|---|---|
| A (TCP) | `SOCK_STREAM` | 5001 |
| B (UDP) | `SOCK_DGRAM` | 5002 |

Alur: client mengirim satu pesan 64 byte, server membalas dengan isi yang sama persis, lalu client mengirim pesan berikutnya sampai 100 pesan. Client mencatat RTT tiap pesan, integritas balasan, connect time (khusus TCP), jumlah pesan hilang (khusus UDP), dan throughput.

## Struktur Berkas

```
src/
├── config.py        # port, jumlah pesan, ukuran pesan, timeout UDP, pembuat payload
├── tcp_server.py    # server echo TCP
├── tcp_client.py    # client TCP (mengukur connect time, RTT, throughput)
├── udp_server.py    # server echo UDP
├── udp_client.py    # client UDP (mengukur RTT, pesan hilang, throughput)
└── README.md
```

## Persyaratan

- Python 3.8 atau lebih baru (hanya memakai pustaka standar, tanpa instalasi tambahan)
- Wireshark (dengan Npcap pada Windows) untuk pengamatan trafik

## Konfigurasi (`config.py`)

| Parameter | Nilai | Keterangan |
|---|---|---|
| `TCP_PORT` | 5001 | port server TCP |
| `UDP_PORT` | 5002 | port server UDP |
| `NUM_MESSAGES` | 100 | jumlah pesan per pengujian |
| `MSG_SIZE` | 64 | ukuran payload tiap pesan (byte) |
| `UDP_TIMEOUT` | 1.0 | detik; UDP dianggap hilang jika tidak ada balasan |

Kedua versi memakai `config.py` yang sama sehingga beban kerjanya identik.

## Opsi Baris Perintah

| Program | Opsi | Default |
|---|---|---|
| `tcp_server.py`, `udp_server.py` | `--host` | `0.0.0.0` (semua interface, agar bisa diakses dari LAN) |
| | `--port` | sesuai `config.py` |
| `tcp_client.py`, `udp_client.py` | `--host` | `127.0.0.1` |
| | `--port` | sesuai `config.py` |

## Menjalankan di Localhost (uji cepat)

Terminal 1: `python tcp_server.py`
Terminal 2: `python tcp_client.py`

Hentikan server TCP dengan `Ctrl+C`, lalu ulangi dengan `udp_server.py` dan `udp_client.py`.

Untuk capture Wireshark pada localhost, pilih interface **Adapter for loopback traffic capture** (Windows) atau `lo` (Linux).

## Menjalankan di LAN (dua perangkat)

### Topologi

Dua perangkat fisik berada dalam satu jaringan lokal (contoh: hotspot HP):

| Perangkat | Peran | IP (contoh) | Subnet Mask |
|---|---|---|---|
| Laptop A | Server | 10.185.237.55 | 255.255.255.0 |
| Laptop B | Client | 10.185.237.220 | 255.255.255.0 |
| HP (hotspot) | Gateway | 10.185.237.53 | 255.255.255.0 |

Ganti IP contoh di atas dengan IP milikmu. Wi-Fi kampus sering mengaktifkan *client isolation* sehingga dua perangkat tidak bisa saling terhubung; gunakan hotspot HP atau router sendiri.

### Langkah 1: Salin kode ke kedua perangkat

Salin seluruh isi folder `src/` ke Laptop A dan Laptop B. Pastikan Python terpasang (`python --version`).

### Langkah 2: Catat IP kedua perangkat

Di masing-masing laptop jalankan:

```
ipconfig
```

Catat **IPv4 Address**, **Subnet Mask**, dan **Default Gateway** pada bagian *Wireless LAN adapter Wi-Fi*. Kedua laptop harus berada pada segmen yang sama (tiga angka pertama IP sama, subnet mask sama).

### Langkah 3: Buka port di firewall Laptop A (server)

Buka **PowerShell sebagai Administrator**, lalu jalankan:

```
New-NetFirewallRule -DisplayName "Jarkom TCP 5001" -Direction Inbound -Protocol TCP -LocalPort 5001 -Action Allow
New-NetFirewallRule -DisplayName "Jarkom UDP 5002" -Direction Inbound -Protocol UDP -LocalPort 5002 -Action Allow
```

Pastikan juga profil jaringan Wi-Fi diatur ke **Private** (Settings, Network & Internet, Wi-Fi, pilih jaringan, Network profile type).

Catatan: `ping` dari client ke server dapat berakhir *Request timed out* walaupun jaringan normal, karena Windows memblokir ICMP echo masuk secara default. Ini tidak memengaruhi pengujian TCP dan UDP.

### Langkah 4: Siapkan Wireshark di Laptop A

1. Buka Wireshark, pilih interface **Wi-Fi** (bukan loopback).
2. Pada kolom **capture filter** (halaman awal, kolom hijau "...using this filter") isi:
   - TCP: `host <IP_CLIENT> and port 5001`
   - UDP: `host <IP_CLIENT> and port 5002`
3. Klik dua kali interface Wi-Fi untuk memulai capture **sebelum** menjalankan client.

### Langkah 5: Pengujian TCP

Di Laptop A (server):

```
python tcp_server.py
```

Muncul: `[TCP server] listening di 0.0.0.0:5001`

Di Laptop B (client):

```
python tcp_client.py --host <IP_SERVER>
```

Contoh: `python tcp_client.py --host 10.185.237.55`

Setelah client selesai (tercetak connect time, RTT, throughput), hentikan capture di Wireshark, simpan sebagai `capture_tcp_lan1.pcapng`, lalu hentikan server dengan `Ctrl+C`.

### Langkah 6: Pengujian UDP

Mulai capture baru dengan capture filter port 5002, lalu:

Di Laptop A:

```
python udp_server.py
```

Di Laptop B:

```
python udp_client.py --host <IP_SERVER>
```

Baca baris `pesan OK/rusak/hilang`, hentikan capture, dan simpan sebagai `capture_udp_lan1.pcapng`.

### Langkah 7: Ulangi dan simpan hasil

Ulangi langkah 5 dan 6 sebanyak tiga kali. Setiap client menulis hasil ke `results_tcp.csv` atau `results_udp.csv` di folder tempat program dijalankan, dan **menimpa** berkas dari run sebelumnya. Ganti nama berkas setelah tiap run, misalnya `results_tcp_lan1.csv`, `results_tcp_lan2.csv`, `results_udp_lan1.csv`, dan seterusnya.

## Filter Wireshark untuk Analisis

Pasang pada bilah **display filter** setelah capture selesai:

| Tujuan | Filter |
|---|---|
| Seluruh sesi TCP | `ip.addr == <IP_CLIENT> && tcp.port == 5001` |
| Seluruh sesi UDP | `ip.addr == <IP_CLIENT> && udp.port == 5002` |
| Handshake dan penutupan TCP | `ip.addr == <IP_CLIENT> && tcp.port == 5001 && tcp.len == 0` |
| Retransmisi TCP | `ip.addr == <IP_CLIENT> && tcp.port == 5001 && tcp.analysis.retransmission` |

Display filter dan capture filter memakai sintaks yang berbeda; jangan tertukar. Untuk berkas yang dikumpulkan, gunakan File, Export Specified Packets, **All packets: Displayed** setelah memasang display filter agar capture hanya berisi lalu lintas pengujian.

## Format Keluaran CSV

```
seq,rtt_ms,status
1,14.6660,OK
2,10.2310,OK
...
```

`status` bernilai `OK`, `CORRUPT` (balasan berbeda dari pesan asli), atau `LOST` (UDP, tidak ada balasan dalam batas waktu; `rtt_ms` kosong).

## Pemecahan Masalah

| Gejala | Kemungkinan penyebab dan solusi |
|---|---|
| `can't open file '...tcp_server.py'` | Terminal tidak berada di folder berisi berkas. Pindah dengan `cd`, atau buka foldernya di VS Code. |
| `WinError 10048` (alamat sudah dipakai) | Server lama masih berjalan. Hentikan dengan `Ctrl+C`, atau cari dengan `netstat -ano \| findstr :5002` lalu `taskkill /PID <PID> /F`. |
| Client TCP timeout atau *connection refused* | Server belum berjalan, IP salah, aturan firewall belum dibuat, atau client isolation pada jaringan. |
| UDP: semua pesan `LOST` | Aturan firewall UDP 5002 belum dibuat, atau jaringan memblokir antarperangkat. |
| Capture Wireshark berisi lalu lintas lain | Pasang capture filter sebelum mulai, atau gunakan display filter lalu Export Displayed. |
| Kolom filter Wireshark merah | Sintaks salah: gunakan sintaks display filter (`ip.addr == ...`), bukan capture filter (`host ...`). |

## Opsional: Simulasi Packet Loss

Untuk mengamati keandalan saat paket hilang, gunakan alat seperti **Clumsy** (Windows, jalankan sebagai Administrator) di Laptop B dengan filter `tcp.SrcPort == 5001 or udp.SrcPort == 5002`, aktifkan **Drop** (Inbound) dengan peluang 10%, lalu ulangi pengujian TCP dan UDP. Hentikan Clumsy setelah selesai.

## Membersihkan Aturan Firewall

Setelah pengujian selesai, hapus aturan yang dibuat (PowerShell Administrator):

```
Remove-NetFirewallRule -DisplayName "Jarkom*"
```
