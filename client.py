import socket
import sys
import json
import time

host = "127.0.0.1"
port = 15555

print("# Creating socket")
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
    print("Failed to create socket")
    sys.exit()

print("# Getting remote IP address")
try:
    remote_ip = socket.gethostbyname(host)
except socket.gaierror:
    print("Hostname could not be resolved. Exiting")
    sys.exit()

print("# Connecting to server, " + host + " (" + remote_ip + ")")
s.connect((remote_ip, port))

print("# Sending data to server")
request = {"pass": "123", "test": "testo1"}

while True:
    try:
        s.sendall(json.dumps(request).encode("utf8"))
    except socket.error:
        print("Send failed")
        sys.exit()
    time.sleep(1)


s.close()

# print("# Receive data from server")
# reply = s.recv(4096)

# print(reply)
