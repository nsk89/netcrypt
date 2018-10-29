import socket
from netcrypt.communication import ServerProtocol


# create basic server
host = 'localhost'
port = 5300
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((host, port))

sock.listen(5)  # listen on socket
print('**listening**')
while 1:  # when connection
    conn, addr = sock.accept()  # accept connection
    print(f'connection made! address: {addr[0]}\n')

    '''
    server communications encryption protocol object
    set cipher block sizes for lower(more performance)/higher(performance impact) security
    RSA: 1028, 2048, 4096
    AES: 16(128 bit), 32(256 bit)
    '''
    crypto_traffic = ServerProtocol(rsa_block_size=2048, aes_block_size=16)

    client_public_key = crypto_traffic.public_key_exchange(conn)  # exchange public keys with client
    crypto_traffic.set_public_key(client_public_key)
    print('received client public key')
    print(f'client public key: {client_public_key}\n')
    # send welcome message to client
    welcome_message = b'_/\_(@_@)_/\_\nWelcome to the server'
    print('sending welcome message to client')
    crypto_traffic.send_crypto_stream(conn, welcome_message)
    response = crypto_traffic.recv_crypto_stream(conn)  # receive response from client
    print(f'client response received:\n{response.decode()}\n')

    # send file to client
    crypto_traffic.send_file(conn, 'testFile.txt')
    print(r'file served to client _/\_(@_@)_/\_')
    conn.close()
