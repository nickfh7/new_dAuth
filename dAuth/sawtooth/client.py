import random
import requests
import base64
import yaml
import json
import cbor
import queue
import threading
import time

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
from dAuth.proto.database_entry import DatabaseEntry


# Handles the creation of transactions for locally originating messages
class CCellularClient:
    def __init__(self, conf: DistributedManagerConfig):
        self.conf = conf
        self.url = conf.CLIENT_URL

        # Transaction batcher
        self.transaction_queue = queue.Queue()
        self.pending_transactions = []
        self.run_check = None
        self.transaction_batcher_thread = None
        self.last_batch_time = 0

        # Get the key from the local machine
        keyfile = conf.CLIENT_KEY_PATH

        # The signer requires a key from the local user/machine
        # See sawtooth documentation for producing a key
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


    # Spawns a thread that handles the creation of transactions and batching
    # Run check function is used by the batcher to check if parent module is still running
    def start_batcher(self, run_check_function):
        if run_check_function is None:
            raise ValueError("Run check function must be specified")
        self.run_check = run_check_function

        self.transaction_batcher_thread = threading.Thread(target=self._transaction_batcher)
        self.transaction_batcher_thread.start()


    # Creates a transaction and sends to sawtooth validator
    def set_entry(self, entry:DatabaseEntry):
        self.log("Set entry called, queueing transaction")
        self.transaction_queue.put(('set', entry))

    # Get value of the entry corresponding to the key
    def get(self, key):
        self.log("Get entry called with key: " + str(key))
        address = make_ccellular_address(key)
        result = self._send_request("state/{}".format(address), name=key)
        if result != None:
            try:
                json_result = json.loads(result)
                data_response = json_result['data']
                b64data = yaml.safe_load(data_response)
                b64decoded = base64.b64decode(b64data)
                cbor_decoded = cbor.loads(b64decoded)
                return DatabaseEntry(cbor_decoded[key])
            except BaseException as e:
                print("Received a base exception:", e)
        return None        

    # Processes available transactions into batches
    # Batch size and timeout can be configured
    def _transaction_batcher(self):
        self.log("Batcher thread entering")

        while self.run_check():
            # get any new transactions (up to batch size)
            while self.transaction_queue.qsize() > 0:
                # get the next pending transaction and add it to pending
                action, entry = self.transaction_queue.get()
                self._build_transaction(action, entry)

                # stop adding new messages if batch size is reached
                # TODO: possible overloading option?
                if len(self.pending_transactions) >= self.conf.BATCH_SIZE:
                    break

            # if there are no transactions, reset the batch timeout
            if len(self.pending_transactions) == 0:
                self.last_batch_time = time.time()
            
            # check for a new full size batch or a batch timeout with at least one transaction
            elif len(self.pending_transactions) >= self.conf.BATCH_SIZE or\
                     (time.time() - self.last_batch_time >= self.conf.BATCH_TIMEOUT and\
                     len(self.pending_transactions) > 0):

                self.log("Creating and sending new batch")
                if len(self.pending_transactions) >= self.conf.BATCH_SIZE:
                    self.log(" Batch size reached")
                else:
                    self.log(" Batch timeout exceeded, sending with {0}/{1}"\
                        .format(len(self.pending_transactions), self.conf.BATCH_SIZE))

                # build batch from available transactions
                batch_list = self._create_batch_list(self.pending_transactions)

                # continue and retry later if there is no batch to send
                if batch_list is None:
                    self.log("No batch list to send")
                    continue

                # clear the pending list of transactions
                self.pending_transactions = []

                # Send new batch (TODO save output?)
                self._send_request(
                    "batches", batch_list.SerializeToString(),
                    'application/octet-stream',
                )

            # wait a little before checking again (for performance)
            time.sleep(self.conf.BATCH_CHECK_DELAY)

        self.log("Batcher thread exiting")
        self.transaction_batcher_thread = None


    # Builds a transaction from the provided info and adds to pending
    def _build_transaction(self, action, entry):
        payload = build_payload(action, entry)
        address = make_ccellular_address(entry.key())

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

        self.pending_transactions.append(transaction)


    # Creates a transaction batch of one or more transactions
    # All transactions must be included in a batch
    def _create_batch_list(self, transactions):
        if len(transactions) < 1:
            self.log("Attempting to create batch with no transactions, ignoring")
            return None

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
                self.log("No such Key Exists: {}".format(name))
                return None

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
