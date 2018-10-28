import hashlib
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


class CryptoProtocol:  # base protocol for crypto methods
    def __init__(self):
        self.private_key = None
        self.public_key = None

    def aes_encrypt(self, key, salt, data):
        # check for or convert to bytes
        key = self.convert_to_bytes(key)
        data = self.convert_to_bytes(data)

        cipher = AES.new(key, AES.MODE_CFB, salt)  # create cipher object
        data = cipher.encrypt(data)  # encrypt data
        del cipher
        return data

    def aes_decrypt(self, key, salt, data):
        # check for or convert to bytes
        key = self.convert_to_bytes(key)
        salt = self.convert_to_bytes(salt)
        data = self.convert_to_bytes(data)

        cipher = AES.new(key, AES.MODE_CFB, salt)  # create cipher object
        data = cipher.decrypt(data)  # decrypt data
        del cipher
        return data

    def start_rsa(self, block_size=4096):  # block size, change for RSA encryption strength, 1024, 2048, 4096
        self.private_key = RSA.generate(block_size)  # create RSA private key
        self.public_key = self.private_key.publickey().exportKey()  # get public key ready for export

        return self.public_key

    def stop_rsa(self):
        del self.private_key
        del self.public_key
        self.private_key = None
        self.public_key = None

    def rsa_encrypt(self, public_key, data):
        '''
        :param data:
        RSA doesn't encrypt large data amounts, data arg is for key
        encryption
        '''
        # check for or convert to bytes
        public_key = self.convert_to_bytes(public_key)
        data = self.convert_to_bytes(data)

        public_key = RSA.importKey(public_key)  # import exported public key
        cipher = PKCS1_OAEP.new(public_key)  # create new RSA cipher
        data = cipher.encrypt(data)  # encrypt passed data
        del cipher

        return data

    def rsa_decrypt(self, data):
        data = self.convert_to_bytes(data)  # check for or convert to bytes
        cipher = PKCS1_OAEP.new(self.private_key)  # create new RSA cipher
        data = cipher.decrypt(data)  # decrypt key data
        del cipher

        return data

    def fetch_hash(self, hash_type, data):  # return hashed data
        data = self.convert_to_bytes(data)  # check for or convert to bytes
        hasher = hashlib.new(hash_type)  # create hash object
        hasher.update(data)  # update hash object with data
        data = hasher.hexdigest()  # digest hash object as hex, re-store in data
        del hasher

        return data

    def convert_to_bytes(self, object):  # check for or convert data to bytes
        if type(object) != bytes:  # if object passed not equal to bytes
            object = bytes(object, 'utf-8')  # convert object to bytes
            return object
        else:
            return object

    def compare_file_hash(self, input_file, hash_type, hash_to_compare):  # compare file hashes
        with open(input_file, 'rb') as f:  # open file
            data = f.read()  # store file data
        f.close()
        file_hash = self.fetch_hash(hash_type, data)  # get hash of file data

        if file_hash == hash_to_compare:  # compare file hash to given hash
            return True
        else:
            return False
