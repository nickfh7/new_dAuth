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
                'ccellular = dAuth.main:main',
                'logging-server = network.logging_server:run_server',
                'test-ccellular = dAuth.tests.testing:main',
                'db-operation = dAuth.database.operations_cli:main',
            ]
        })