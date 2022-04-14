BIT = 1
BYTE = BIT * 8
KiB = BYTE * 1024
MiB = KiB * 1024
GiB = MiB * 1024

MAX_BANDWIDTH = 900
MAX_THREADS = 300

# LISTEN_HOST = "127.0.0.1"
LISTEN_HOST = "0.0.0.0"

ADDRESS = (LISTEN_HOST, 8081)
# PROXY_AUTHORIZATION_HEADER="BBC-Proxy-Authorization"
PROXY_AUTHORIZATION_HEADER = "Proxy-Authorization"
