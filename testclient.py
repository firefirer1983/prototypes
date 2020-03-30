import socket


if __name__ == "__main__":
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", 8003))
    client.sendall(b"Hello World\r\n\r\n")
    while True:
        print(client.recv(1024))
