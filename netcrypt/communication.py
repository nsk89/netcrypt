import hashlib
import struct
import pickle
import hmac
import ntpath
import os
import socks
from Crypto import Random
from netcrypt.cryptography import CryptoProtocol


class SharedMethods:  # methods used for both server and client
    def __init__(self):
        self.crypto_worker = CryptoProtocol()  # create cryptography object for cipher operations
        self.block_size = 4096
        self.public_key = ''

    def set_public_key(self, public_key):
        self.public_key = public_key

    def generate_key(self, length):
        key = Random.get_random_bytes(length)  # use PyCrypto Random module to get random bytes based off system state
        secret = Random.get_random_bytes(length)

        # create hmac sha3_384 key using key/secret
        generated_key = hmac.new(key, secret, hashlib.sha384).hexdigest()[:length]

        return bytes(generated_key, 'utf-8')

    def recv_message(self, socket_object):
        raw_msg_length = self.recv_all(socket_object, 4)  # receive first 4 bytes of data in stream
        if not raw_msg_length:
            return None

        # unpack first 4 bytes using network byte order to retrieve incoming message length
        msg_length = struct.unpack('>I', raw_msg_length)[0]

        return self.recv_all(socket_object, msg_length)  # recv rest of stream up to message length

    def recv_all(self, socket_object, num_bytes):
        data = b''
        while len(data) < num_bytes:  # while amount of data recv is less than message length passed
            packet = socket_object.recv(num_bytes - len(data))  # recv remaining bytes/message
            if not packet:
                return None
            data += packet
        return data

    def verify_message(self, received_key, received_message, received_verification):
        #  check that encrypted message/data is the original sent
        message_hash = bytes(hmac.new(received_key, received_message, hashlib.sha384).hexdigest(), 'utf-8')
        if message_hash == received_verification:
            return True
        else:
            return False

    def fetch_filename(self, path):  # split files from paths
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)

    def pack_file(self, file_location):  # prepare file for transmission
        filename = bytes(self.fetch_filename(file_location), 'utf-8')  # retrieve filename
        with open(file_location, 'rb') as f:  # open file
            data = f.read()  # read file data
        f.close()
        file_dict = {'filename': filename, 'data': data}  # store filename and data in dictionary
        file_dict = pickle.dumps(file_dict)  # serialize dictionary

        return file_dict

    def write_file(self, file_dict, save_location=''):
        if save_location == '':
            save_location = os.getcwd()  # default store to client.py working dir
        file_dict = pickle.loads(file_dict)  # de-serialize dictionary
        file_name = file_dict['filename']
        data = file_dict['data']
        os.chdir(save_location)  # change dir to custom location or default
        with open(file_name, 'wb') as f:  # open file with name from dictionary
            f.write(data)  # write file data to disk
        f.close()

    def send_crypto_stream(self, socket_object, message):  # handle outgoing encrypted data stream
        # generate encryption keys based off system state
        aes_key = self.generate_key(32)
        aes_salt = self.generate_key(16)

        # encrypt encryption keys with public key encryption
        aes_key_encrypted = self.crypto_worker.rsa_encrypt(self.public_key, aes_key)
        aes_salt_encrypted = self.crypto_worker.rsa_encrypt(self.public_key, aes_salt)

        # encrypt the message/data using non-encrypted keys
        message = self.crypto_worker.aes_encrypt(aes_key, aes_salt, message)

        # create message verification
        message_verification = bytes(hmac.new(aes_key, message, hashlib.sha384).hexdigest(), 'utf-8')
        message_verification = self.crypto_worker.rsa_encrypt(self.public_key, message_verification)

        # serialize encryption keys/message|data/verification for transport
        serialized_keys = {'aes': aes_key_encrypted, 'salt': aes_salt_encrypted,
                                  'message': message, 'verification': message_verification}
        serialized_keys = pickle.dumps(serialized_keys)
        # structure data to internet byte order
        serialized_keys = struct.pack('>I', len(serialized_keys)) + serialized_keys

        socket_object.sendall(serialized_keys)  # transport encrypted data

    def recv_crypto_stream(self, socket_object):  # handle incoming encrypted data stream
        serialized_server_keys = self.recv_message(socket_object)  # recv message
        serialized_server_keys = pickle.loads(serialized_server_keys)  # return to dict from pickle

        # retrieve encryption keys
        server_aes_key = serialized_server_keys['aes']
        server_aes_salt = serialized_server_keys['salt']
        server_aes_message = serialized_server_keys['message']
        server_aes_verification = serialized_server_keys['verification']

        # RSA decrypt encryption keys
        server_aes_key = self.crypto_worker.rsa_decrypt(server_aes_key)
        server_aes_salt = self.crypto_worker.rsa_decrypt(server_aes_salt)
        server_aes_verification = self.crypto_worker.rsa_decrypt(server_aes_verification)

        # verify message is original, decrypt received data stream
        if self.verify_message(server_aes_key, server_aes_message, server_aes_verification):
            self.server_aes_key = server_aes_key
            self.server_aes_salt = server_aes_salt
            server_aes_message = self.crypto_worker.aes_decrypt(server_aes_key, server_aes_salt, server_aes_message)
            return server_aes_message
        else:
            return b'Message Verification Failure'


class ClientProtocol(SharedMethods):  # inherits the shared methods
    def __init__(self):
        super().__init__()  # init inherited variables
        self.server_public_key = None
        self.client_public_key = self.crypto_worker.start_rsa(self.block_size)  # generate required RSA information

    def recv_crypto_stream(self, sock):  # return inherited method
        return super(ClientProtocol, self).recv_crypto_stream(sock)

    def send_crypto_stream(self, socket_object, message):  # return inherited method
        return super(ClientProtocol, self).send_crypto_stream(socket_object, message)

    def public_key_exchange(self, socket_object):  # server/client share public keys to start RSA encryption
        self.server_public_key = socket_object.recv(self.block_size)
        socket_object.sendall(self.client_public_key)

        return self.server_public_key

    def send_file(self, socket_object, file_location):  # send data to server
        # pack the file located at file_location and send over the stream
        self.send_crypto_stream(socket_object, self.pack_file(file_location))

    def recv_file(self, socket_object, file_location=''):  # send data from server
        if file_location == '':  # file_location controls where the file will store
            file_location = os.getcwd()  # default file storage
        # receive encrypted file stream and write file to disk
        self.write_file(self.recv_crypto_stream(socket_object), file_location)

    def enable_tor(self):
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, 'localhost', 9050, True)

        return socks.socksocket()


class ServerProtocol(SharedMethods):  # inherits the shared methods
    # comment information is similar as above except with different socket requirements
    def __init__(self):
        super().__init__()  # init inherited variables
        self.server_public_key = self.crypto_worker.start_rsa(self.block_size)

    def recv_crypto_stream(self, socket_object):  # return inherited method
        return super(ServerProtocol, self).recv_crypto_stream(socket_object)

    def send_crypto_stream(self, socket_object, message):  # return inherited method
        return super(ServerProtocol, self).send_crypto_stream(socket_object, message)

    def public_key_exchange(self, socket_object):
        socket_object.sendall(self.server_public_key)
        client_public_key = socket_object.recv(self.block_size)

        return client_public_key

    def send_file(self, socket_object, file_location):
        self.send_crypto_stream(socket_object, self.pack_file(file_location))

    def recv_file(self, socket_object, file_location=''):
        if file_location == '':
            file_location = os.getcwd()
        self.write_file(self.recv_crypto_stream(socket_object), file_location)
