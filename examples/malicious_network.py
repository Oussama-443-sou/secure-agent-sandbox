import socket

print("Attempting to connect to example.com:80...")

sock = socket.create_connection(("example.com", 80), timeout=3)
sock.sendall(b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n")

response = sock.recv(100)
print(response.decode(errors="ignore"))
