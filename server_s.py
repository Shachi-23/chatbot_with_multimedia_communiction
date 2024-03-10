import socket
import threading
import os

host = '192.168.139.142'
port = 5000
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []

def broadcast(message, sender=None):
    for client in clients:
        if client != sender:
            client.send(message)

def handle_client(conn, addr):
    print(f"Connected by {addr}")
    while True:
        try:
            header = conn.recv(4096).decode('utf-8')
            if header.startswith("FILE:"):
                filename = header.split(":")[1]
                filesize = int(header.split(":")[2])
                broadcast(f"FILE:{filename}:{filesize}".encode('utf-8'), conn)
                bytes_received = 0
                with open(filename, "wb") as file:
                    while bytes_received < filesize:
                        bytes_read = conn.recv(min(4096, filesize - bytes_received))
                        if not bytes_read:
                            break
                        file.write(bytes_read)
                        bytes_received += len(bytes_read)
                broadcast_file(filename, filesize, conn)
                os.remove(filename)  # Optional: Remove file after sending
            else:
                broadcast(header.encode('utf-8'), conn)
        except Exception as e:
            print(f"Error handling message from {addr}: {e}")
            clients.remove(conn)
            break

def broadcast_file(filename, filesize, sender=None):
    with open(filename, "rb") as file:
        while True:
            bytes_read = file.read(4096)
            if not bytes_read:
                break
            for client in clients:
                if client != sender:
                    client.send(bytes_read)

def receive():
    while True:
        client, address = server.accept()
        print(f"Connection from {address} has been established.")
        clients.append(client)
        thread = threading.Thread(target=handle_client, args=(client, address))
        thread.start()

print("Server is listening...")
receive()