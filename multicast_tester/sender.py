'''
command line : multicast ip address port

(multicast ip addresses start with either 239.255 or 244.255)

sender runs continuously waiting for text inputs to send 

'''


import socket
import sys

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <multicast_ip> <port>")
        sys.exit(1)

    MCAST_GRP = sys.argv[1]
    MCAST_PORT = int(sys.argv[2])

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)

    print(f"Connected to multicast group {MCAST_GRP}:{MCAST_PORT}")
    print("Type messages to send. Press Ctrl+C or type 'quit' to exit.\n")

    while True:
        try:
            message = input("> ")
            if message.strip().lower() in ("quit", "exit"):
                print("Exiting sender...")
                break
            sock.sendto(message.encode(), (MCAST_GRP, MCAST_PORT))
            print(f"Sent: {message}")
        except KeyboardInterrupt:
            print("\nExiting sender...")
            break

if __name__ == "__main__":
    main()
