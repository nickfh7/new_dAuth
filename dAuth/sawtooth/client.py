import random
import requests
import base64
import yaml
import json
import cbor

from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
from sawtooth_sdk.protobuf.batch_pb2 import BatchList
from sawtooth_sdk.protobuf.batch_pb2 import Batch

from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_signing import ParseError
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey

from dAuth.sawtooth.transactions import _sha512, get_prefix, build_payload, make_ccellular_address
from dAuth.config import DistributedManagerConfig
from dAuth.proto.database import DatabaseOperation


# Handles the creation of transactions for locally originating messages
class CCellularClient:
    def __init__(self, conf: DistributedManagerConfig):
        self.conf = conf
        self.url = conf.CLIENT_URL
        keyfile = conf.CLIENT_KEY_PATH

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

        self.logger = None


    # Creates a transaction and sends to sawtooth validator
    def set_operation(self, operation:DatabaseOperation):
        self.log("Set operation called")
        self._send_transaction('set', operation)

    # Gets data 
    def get(self, key):
        self.log("Get operation called with key: " + str(key))
        address = make_ccellular_address(key)
        result = self._send_request("state/{}".format(address), name=key)
        try:
            json_result = json.loads(result)
            data_response = json_result['data']
            b64data = yaml.safe_load(data_response)
            b64decoded = base64.b64decode(b64data)
            cbor_decoded = cbor.loads(b64decoded)
            return cbor_decoded[key]
        except BaseException as e:
            print("Received a base exception. " + e)
            return None


    # Internal method for building and sending a transaction
    def _send_transaction(self, action, operation):
        payload = build_payload(action, operation)
        address = make_ccellular_address(operation.key())

        header = TransactionHeader(
            signer_public_key=self._signer.get_public_key().as_hex(),
            family_name=self.conf.FAMILY_NAME,
            family_version=self.conf.FAMILY_VERSION,
            inputs=[address],
            outputs=[address],
            dependencies=[],
            payload_sha512=_sha512(payload),
            batcher_public_key=self._signer.get_public_key().as_hex(),
            nonce=hex(random.randint(0, 2 ** 64))
        ).SerializeToString()

        signature = self._signer.sign(header)

        transaction = Transaction(
            header=header,
            payload=payload,
            header_signature=signature
        )

        batch_list = self._create_batch_list([transaction])

        return self._send_request(
            "batches", batch_list.SerializeToString(),
            'application/octet-stream',
        )

    # Creates a transaction batch of one or more transactions
    # All transactions must be included in a batch
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

    # Sends the actual batch request to the validator
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
                raise Exception("No such Key Exists: {}".format(name))

            if not result.ok:
                raise Exception("Error {}: {}".format(result.status_code, result.reason))
    
        except requests.ConnectionError as err:
            raise Exception("Failed to connect to the REST API services : {}".format(err))

        except BaseException as err:
            raise Exception("Failed {}".format(err))

        return result.text

    def log(self, message):
        if self.logger:
            self.logger("(Client) " + message)
