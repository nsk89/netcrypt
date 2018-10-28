from setuptools import setup, find_packages


setup(
    name='netcrypt',
    version='1.0.0-alpha.0',
    url='https://github.com/nsk89/protocols',
    license='BSD 2-Clause',
    author='Nathaniel Knous',
    author_email='nsk89@live.com',
    description='socket transmission and encryption protocols',
    packages=['netcrypt'],
    install_requires=['PySocks', 'PyCryptodome']
)
