import json

from dAuth.proto.database_entry_pb2 import DatabaseEntryProto
from dAuth.utils import _sha512

# Wrapper around a protobuf object
# Handles the contruction and setting
class DatabaseEntry:
    # Can be constructed with a protobuf message or a dict or a serialized string (bytes)
    def __init__(self, protobuf_data):
        self.old_op = None

        # if the type is an op document (dict), build based on data and op type
        if type(protobuf_data) is dict:
            # build protobuf message from data
            self.protobuf_message = self.dict_to_protobuf(protobuf_data)

        # can also build from serialized string of a protobuf message
        elif type(protobuf_data) is bytes:
            self.protobuf_message = DatabaseEntryProto()
            self.protobuf_message.ParseFromString(protobuf_data)
            self.protobuf_message = self.dict_to_protobuf(self.protobuf_to_dict(self.protobuf_message))

        # can also build directly from a protomessage
        elif type(protobuf_data) is DatabaseEntryProto:
            self.protobuf_message = protobuf_data
        
        else:
            raise ValueError("protobuf data is invalid type - " + str(type(protobuf_data)))

        # Update the max sqn if needed
        self.update_max_known_sqn()

    # Returns a dictionary with the protobuf message data
    def to_dict(self):
        return self.protobuf_to_dict(self.protobuf_message)
    
    # Returns the field of the protobuf message that is used as the key
    def key(self):
        return self.protobuf_message.imsi

    # Returns the size of the protobuf message
    def size(self):
        return self.protobuf_message.ByteSize()

    # Returns the list of vectors
    def get_vectors(self):
        return json.loads(self.protobuf_message.vectors)

    def get_max_known_sqn(self):
        return int(self.protobuf_message.max_known_sqn)

    # Returns max sqn, or -1 if there are none
    def get_max_current_sqn(self):
        vectors = self.get_vectors()
        if len(vectors) > 0:
            return max([int(vector['sqn']) for vector in vectors])
        else:
            return -1

    # Generate a filter for MongoDBs
    def get_filter(self):
        return {"imsi": self.key()}

    # Return relevant data depending on operation
    def get_data(self):
        return self.protobuf_to_dict(self.protobuf_message)

    # Returns a serialized dict with payload info (for distributed)
    def get_serialized_message(self):
        return self.protobuf_message.SerializeToString()

    def update_max_known_sqn(self):
        self.protobuf_message.max_known_sqn =\
            str(max(self.get_max_known_sqn(), self.get_max_current_sqn()))

    # Creates a hash id string of protobuf message
    # Returns the first 16 chars
    def get_id_string(self):
        return _sha512(self.get_serialized_message())[0:16]

    # Returns a dict that represents the protobuf message
    @staticmethod
    def protobuf_to_dict(protobuf_message:DatabaseEntryProto):
        return {
            "imsi": protobuf_message.imsi,
            "max_known_sqn": protobuf_message.max_known_sqn,
            "vectors": protobuf_message.vectors,
        }
    
    # Returns a new protobuf message from a dict
    @staticmethod
    def dict_to_protobuf(protobuf_dict:dict):
        return DatabaseEntryProto(
            imsi=protobuf_dict.get("imsi"),
            max_known_sqn=protobuf_dict.get("max_known_sqn"),
            vectors=protobuf_dict.get("vectors")
        )