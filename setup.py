from setuptools import setup, find_packages

if __name__ == '__main__':
    setup(
        name='dAuth',
        version="0.1",
        packages=find_packages(),
        install_requires=[
            'requests',
            'pymongo',
            'mongotriggers',
            'protobuf',
            'grpcio',
            'cbor',
            'sawtooth-sdk',
        ],
        entry_points={
            'console_scripts': [
                'dauth-main = dAuth.main:main',
                'logging-server = network.logging_server:run_server',
            ]
        })