import socket
import threading

first_port = 31400
last_port = 31409
#your computer ip 
ip = "192.168.1.100"


def create_socket(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
    server_socket.bind((ip, port))
    server_socket.listen(1)
    print(f"Port {port} is now open.") 

    while True:
        # Accept incoming connections
        connection, address = server_socket.accept()
        print(f"Connection established from {address}")

    
threads=[]

for port in range(first_port,last_port+1):
    thread = threading.Thread(target=create_socket, args=(port,))
    thread.start()
    threads.append(thread)
for thread in threads:
    thread.join() 
