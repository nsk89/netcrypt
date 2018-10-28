import socket
from netcrypt.communication import ClientProtocol


# create basic connection to server
host = 'localhost'
port = 5300
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
crypto_traffic = ClientProtocol()  # client communications encryption protocol object

# optional, enable connection over tor and returns tor socket object. Otherwise use above socket object
print('connecting to server')
sock.connect((host, port))
server_public_key = crypto_traffic.public_key_exchange(sock)  # exchange public keys for encryption with server
crypto_traffic.set_public_key(server_public_key)

server_hello = crypto_traffic.recv_crypto_stream(sock)  # receive hello from server
print(server_hello.decode())
crypto_traffic.send_crypto_stream(sock, b'Thanks for having me')  # send response to server
print('sent response')

# receive encrypted file stream from server and write to disk
crypto_traffic.recv_file(sock)
print('file received and written to disk!')
