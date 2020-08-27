import cbor
import hashlib

from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from sawtooth_sdk.processor.exceptions import InvalidTransaction, InternalError

from dAuth.proto.database_entry import DatabaseEntry
from dAuth.config import DistributedManagerConfig


# Functions related to managing transactions


def _sha512(data):
    return hashlib.sha512(data).hexdigest()


def get_prefix():
    return _sha512(DistributedManagerConfig.FAMILY_NAME.encode('utf-8'))[0:6]


def make_ccellular_address(key):
    return get_prefix() + _sha512(key.encode('utf-8'))[64:]


# Creates and returns a serialized payload
def build_payload(action, entry:DatabaseEntry):
    payload = {
        "verb": action,
        "key": entry.key(),
        "data": entry.get_serialized_message()
    }

    return cbor.dumps(payload)


# Deserializes the payload and pulls out action, key, and data
def extract_payload(serialized_payload):
    try:
        payload = cbor.loads(serialized_payload)
    except:
        raise InvalidTransaction('Invalid Transaction Payload Serialization Format')
    action = payload['verb']
    key = payload['key']
    data = payload['data']

    return action, key, data


# Unpacks the transaction
def unpack_transaction(transaction:Transaction):
    # get the payload info
    action, key, data = extract_payload(transaction.payload)

    # TODO: validate the data

    return action, key, data


# Pulls state data for merkle database from transaction context
def get_state_data(key, context):
    address = make_ccellular_address(key)
    state_entries = context.get_state([address])

    try:
        return cbor.loads(state_entries[0].data)
    except IndexError:
        return {}
    except:
        raise InternalError('Failed to load local state from the sawtooth state')


# Updates the state of the merkle database
def set_state_data(key, state, context):
    address = make_ccellular_address(key)
    encoded = cbor.dumps(state)
    addresses = context.set_state({address: encoded})
    if not addresses:
        raise InternalError('Failed to set the local state of the sawtooth node')