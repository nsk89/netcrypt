# netcrypt

<p>socket transmission and encryption protocols</p>
<p>simplifying socket data stream cryptography using RSA public keys and AES data encryption, using PyCryptodome cryptographic primitives</p>

## installation

<p>clone this repository or simply your favorite way over pip:</p>

```
python3 -m pip install netcrypt
```

## how it works

<p>this project doesn't incorporate basic server/client functions besides communication, though that may change in the future. the current state of the project mainly deals with sending data, including files, over sockets securely. data to be sent is first encrypted using AES. the AES key and init vector are then encrypted with a RSA cipher from the public key set from the exchanging socket connection. the data(message) then creates a hash verification for use on decryption to verify data itegrity. 
<br>
<br>
key, init vector, data verification hash and data are then stored in a dictionary to be dumped into a serialized bytes object. the serialized object is then structured into internet byte order and length of object is stored in the first four bytes of transmission. on receive, the first four bytes are read from the stream retrieving the stream length, the remainder of the stream is collected and read in based off the length. the process goes in reverse from there.
<br>
<br>all socket data encryption is done in communication.py which methods use cryptography.py(based off PyCryptodome ciphers).

## getting started
  
<p>create a server stream encryption object, this example we'll use crypto_traffic:</p>

```
from netcrypt.communication import ServerProtocol


crypto_traffic = ServerProtocol()
```
<br>

<p>to start encrypted communication public keys must be exchanged, exchange the public keys and store the clients key:</p>

```
client_public_key = crypto_traffic.public_key_exchange()
```
<br>

<p>to send or receive data, the public key needs to be set first. in this case we're sending:</p>

```
crypto_traffic.set_public_key(client_public_key)

message = b'Welcome to the server!'
crypto_traffic.send_crypto_stream(conn, message) 
```
<br>

<p>to receive the message client side:</p>

```
server_message = crypto_traffic.recv_crypto_stream(sock)
```
<br>

<p>sending a file from server to client, in this case we have testFile.txt stored in cwd:</p>

```
crypto_traffic.send_file(conn, 'testFile.txt')
```
<br>

<p>to receive above file client side and store in cwd:</p>

```
crypto_traffic.recv_file(sock)
```
<br>

<p>a socks socket will be returned on the enable_tor() call. the returned socket object is used in place of the typical socket <br>object and inherits its functionality. route client through the tor network:</p>

```
tor_sock = crypto_traffic.enable_tor()
```

<br>

## simple server example

```
# server byte string and file transmission example

import socket
from netcrypt.communication import ServerProtocol


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
    
```

## simple client example

```
# client byte string and file receive over tor example


import socket
from netcrypt.communication import ClientProtocol


# create basic connection to server
host = 'localhost'
port = 5300
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
crypto_traffic = ClientProtocol()  # client communications encryption protocol object

# optional enable_tor(), enable connection over tor and returns tor socket object. tor must be installed
# otherwise use above socket object "sock" in place of the following tor_sock
tor_sock = crypto_traffic.enable_tor()
print('connecting to server')
tor_sock.connect((host, port))
server_public_key = crypto_traffic.public_key_exchange(tor_sock)  # exchange public keys for encryption with server
print(f'received server public key:\n{server_pubic_key}\n')
crypto_traffic.set_public_key(server_public_key)

server_hello = crypto_traffic.recv_crypto_stream(tor_sock)  # receive hello from server
print(server_hello.decode())
crypto_traffic.send_crypto_stream(tor_sock, b'Thanks for having me')  # send response to server
print('sent response')

# receive encrypted file stream from server and write to disk
crypto_traffic.recv_file(tor_sock)
print('file received and written to disk!')

```

# cryptographic methods

## getting started

<p>create an instance of CryptoProtocol:</p>

```
from netcrypt.cryptography import CryptoProtocol


crypto_worker = CryptoProtocol()
```

<br>

<p>generate random keys:</p>

```
aes_key = crypto_worker.generate_key(32)
init_vect = crypto_worker.generate_key(16)
```

<br>

<p>encrypt data with AES cipher:</p>

```
data = 'hello, world'
aes_key = crypto_worker.generate_key(32)
init_vect = crypto_worker.genreate_key(16)
encrypted_data = crypto_worker.encrypt(aes_key, init_vect, data)
```

<br>

<p>decrypt data with AES cipher:</p>

```
decrypted_data = crypto_worker.decrypt(aes_key, init_vect, encrypted_data)
```

<br>

<p>create RSA private key and return public key:</p>

```
my_public_key = crypto_worker.start_rsa(4096)
```

<br>

<p>encrypt AES encryption key with RSA public key:</p>

```
encrypted_aes_key = crypto_worker.rsa_encrypt(my_public_key, aes_key)
```

<br>

<p>decrypt AES encryption key with RSA private key:</p>

```
decrypted_aes_key = crypto_worker.rsa_decrypt(encrypted_aes_key)
```

<br>

## test crypto run

```
from netcrypt.cryptography import CryptoProtocol


#  AES TEST

data = 'Hello there world!'  # some data to encrypt
print(f'starting data: {data}')
crypto_worker = CryptoProtocol()  # call cryptography object

# generate random keys for encryption
aes_key = crypto_worker.generate_key(32)
init_vector = crypto_worker.generate_key(16)

encrypted_data = crypto_worker.aes_encrypt(aes_key, init_vector, data)  # encrypt data
print(f'AES key: {aes_key}\ninitialization vector: {init_vector}\nencrypted data: {encrypted_data}')

decrypted_data = crypto_worker.aes_decrypt(aes_key, init_vector, encrypted_data)  # decrypt data
print(f'decrypted data: {decrypted_data}')


# RSA TEST

data = 'Hello there World!'  # some data to encrypt
print(f'starting data: {data}')
crypto_worker = CryptoProtocol()  # call cryptography object
my_public_key = crypto_worker.start_rsa(4096)  # generate RSA private/public keys

# generate random encryption keys for aes
aes_key = crypto_worker.generate_key(32)
init_vector = crypto_worker.generate_key(16)

encrypted_data = crypto_worker.aes_encrypt(aes_key, init_vector, data)  # encrypt data with encryption keys

# use RSA cipher to encrypt the encryption key and init vector used by the AES cipher
encrypted_aes_key = crypto_worker.rsa_encrypt(my_public_key, aes_key)
encrypted_init_vector = crypto_worker.rsa_encrypt(my_public_key, init_vector)
# at this point encrypted key, vector and data are ready to send in a dict over a socket
print(f'encrypted AES key: {encrypted_aes_key}\nencrypted initialization vector: {encrypted_init_vector}\n'
      f'encrypted data: {encrypted_data}')


# use RSA private key to decrypt the encrypted AES cipher key and init vector
decrypted_aes_key = crypto_worker.rsa_decrypt(encrypted_aes_key)
decrypted_init_vector = crypto_worker.rsa_decrypt(encrypted_init_vector)

# data is decrypted back into plaintext
decrypted_data = crypto_worker.aes_decrypt(decrypted_aes_key, decrypted_init_vector, encrypted_data)
print(f'decrypted data: {decrypted_data}')

```






