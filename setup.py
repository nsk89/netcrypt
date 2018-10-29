from setuptools import setup, find_packages


with open('README.md', 'rb') as f:
    long_description = f.read()
f.close()


setup(
    name='netcrypt',
    version='1.0.0-alpha.1',
    url='https://github.com/nsk89/netcrypt',
    license='BSD 2-Clause',
    author='Nathaniel Knous',
    author_email='nsk89@live.com',
    description='simplifying socket data stream cryptography using RSA public keys and AES data encryption',
    long_description=long_description,
    packages=find_packages(),
    install_requires=['PySocks', 'PyCryptodome']
)
