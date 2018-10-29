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
