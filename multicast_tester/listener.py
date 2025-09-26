'''
command line : multicast_ip port

listener listens and repeats text sent

'''


import socket
import struct
import sys

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <multicast_ip> <port>")
        sys.exit(1)

    MCAST_GRP = sys.argv[1]
    MCAST_PORT = int(sys.argv[2])

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock.bind(("", MCAST_PORT))

    mreq = struct.pack("=4s4s", socket.inet_aton(MCAST_GRP), socket.inet_aton("0.0.0.0"))
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print(f"Listening for multicast on {MCAST_GRP}:{MCAST_PORT}...")

    while True:
        data, addr = sock.recvfrom(1024)
        print(f"Received from {addr}: {data.decode(errors='ignore')}")

if __name__ == "__main__":
    main()
