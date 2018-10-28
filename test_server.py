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
    print(f'connection! address: {addr[0]}')
    crypto_traffic = ServerProtocol()  # server communications encryption protocol object
    print('sending/receiving public keys')
    client_public_key = crypto_traffic.public_key_exchange(conn)  # exchange public keys with client
    crypto_traffic.set_public_key(client_public_key)
    print('public keys exchanged')
    # send welcome message to client
    welcome_message = b'_/\_(@_@)_/\_\nWelcome to the server'
    crypto_traffic.send_crypto_stream(conn, welcome_message)
    response = crypto_traffic.recv_crypto_stream(conn)  # receive response from client
    print(response)

    # send file to client
    crypto_traffic.send_file(conn, 'testFile.txt')
    print(r'file served _/\_(@_@)_/\_')
    conn.close()
