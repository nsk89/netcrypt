# client byte string and file receive over tor example


import socket
from netcrypt.communication import ClientProtocol


# create basic connection to server
host = 'localhost'
port = 5300
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


'''
    client communications encryption protocol object
    set cipher block sizes for lower(more performance)/higher(performance impact) security
    RSA: 1028, 2048, 4096
    AES: 16(128 bit), 32(256 bit)
    '''
crypto_traffic = ClientProtocol(rsa_block_size=2048, aes_block_size=16)

# optional enable_tor(), enable connection over tor and returns tor socket object. tor must be installed
# otherwise use above socket object "sock" in place of the following tor_sock
#tor_sock = crypto_traffic.enable_tor()
print('connecting to the server')
sock.connect((host, port))
server_public_key = crypto_traffic.public_key_exchange(sock)  # exchange public keys for encryption with server
print(f'received server public key:\n{server_public_key}\n')
crypto_traffic.set_public_key(server_public_key)

server_hello = crypto_traffic.recv_crypto_stream(sock)  # receive hello from server
print(f'{server_hello.decode()}\n')
crypto_traffic.send_crypto_stream(sock, b'Thanks for having me')  # send response to server
print('sent response to server')

# receive encrypted file stream from server and write to disk
crypto_traffic.recv_file(sock)
print('file received from server and written to disk!')
