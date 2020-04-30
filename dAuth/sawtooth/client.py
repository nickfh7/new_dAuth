import random
import requests
import base64
import yaml
import json
import cbor # Go ahead and remove the dependency on this with protobuf serialization format.

from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
from sawtooth_sdk.protobuf.batch_pb2 import BatchList
from sawtooth_sdk.protobuf.batch_pb2 import Batch

from dAuth.utils import _sha512
from dAuth.config import DistributedManagerConfig

from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_signing import ParseError
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey


# Handles the creation of transactions for locally originating messages
class CCellularClient:
    def __init__(self, url, keyfile=None, 
                            BINARY_NAME=DistributedManagerConfig.BINARY_NAME,
                            BINARY_VERSION=DistributedManagerConfig.BINARY_VERSION):
        self.url = url
        self.BINARY_VERSION

        if keyfile is not None:
            try:
                with open(keyfile) as fd:
                    private_key_str = fd.read().strip()
                    fd.close()
            except OSError as err:
                raise Exception('Failed to read private key at {}'.format(err))

            try:
                private_key = Secp256k1PrivateKey.from_hex(private_key_str)
            except ParseError as e:
                raise Exception('Unable to load the private key correctly {}'.format(str(e)))

            self._signer = CryptoFactory(create_context('secp256k1')).new_signer(private_key)
            print(self._signer)


    def set(self, key, value):
        # print("Trying to set {} to {}".format(imsi, value))
        return self._send_transaction('set', key, value)


    # Private methods used by the client
    @staticmethod
    def _get_prefix():
        return _sha512(self.BINARY_NAME.encode('utf-8'))[0:6]

    def _get_address(self, imsi):
        prefix = self._get_prefix()
        address = _sha512(imsi.encode('utf-8'))[64:]
        return prefix + address

    def _send_request(self, suffix, data=None, content_type=None, name=None):
        if self.url.startswith("http://"):
            url = "{}/{}".format(self.url, suffix)
        else:
            url = "http://{}/{}".format(self.url, suffix)
        headers = {}

        if content_type is not None:
            headers['Content-Type'] = content_type

        try:
            if data is not None:
                result = requests.post(url, headers=headers, data=data)
            else:
                result = requests.get(url, headers=headers)

            if result.status_code == 404:
                raise Exception("No such IMSI Exists: {}".format(name))

            if not result.ok:
                raise Exception("Error {}: {}".format(result.status_code, result.reason))
        except requests.ConnectionError as err:
            raise Exception("Failed to connect to the REST API services : {}".format(err))
        except BaseException as err:
            raise Exception("Failed {}".format(err))
        return result.text

    def _send_transaction(self, operation, key, value):
        payload = cbor.dumps({'verb': operation, 'key': key, 'value': value})
        # Construct the address
        address = self._get_address(key)
        header = TransactionHeader(
            signer_public_key=self._signer.get_public_key().as_hex(),
            family_name=self.BINARY_NAME,
            family_version=self.BINARY_VERSION,
            inputs=[address],
            outputs=[address],
            dependencies=[],
            payload_sha512=_sha512(payload),
            batcher_public_key=self._signer.get_public_key().as_hex(),
            nonce=hex(random.randint(0, 2 ** 64))
        ).SerializeToString()

        # print("Header : {}".format(header))

        signature = self._signer.sign(header)
        # print("Signature: {}".format(signature))

        transaction = Transaction(
            header=header,
            payload=payload,
            header_signature=signature
        )

        # print("Transaction: {}".format(transaction))

        batch_list = self._create_batch_list([transaction])

        return self._send_request(
            "batches", batch_list.SerializeToString(),
            'application/octet-stream',
        )

    def _create_batch_list(self, transactions):
        transaction_signatures = [t.header_signature for t in transactions]

        header = BatchHeader(
            signer_public_key=self._signer.get_public_key().as_hex(),
            transaction_ids=transaction_signatures
        ).SerializeToString()

        signature = self._signer.sign(header)

        batch = Batch(
            header=header,
            transactions=transactions,
            header_signature=signature)
        return BatchList(batches=[batch])