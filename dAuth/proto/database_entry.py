import json

from dAuth.proto.database_entry_pb2 import DatabaseEntryProto

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

        # can also build directly from a protomessage
        elif type(protobuf_data) is DatabaseEntryProto:
            self.protobuf_message = protobuf_data
        
        else:
            raise ValueError("protobuf data is invalid type - " + str(type(protobuf_data)))

    # Returns a dictionary with the protobuf message data
    def to_dict(self):
        return self.protobuf_to_dict(self.protobuf_message)
    
    # Returns the field of the protobuf message that is used as the key
    def key(self):
        return self.protobuf_message.imsi

    # Returns the size of the protobuf message
    def size(self):
        return self.protobuf_message.ByteSize()

    # Generate a filter for MongoDBs
    def get_filter(self):
            return {"imsi": self.key()}

    # Return relevant data depending on operation
    def get_data(self):
        return self.protobuf_to_dict(self.protobuf_message)

    # Returns a serialized dict with payload info (for distributed)
    def get_serialized_message(self):
        return self.protobuf_message.SerializeToString()

    # Returns a dict that represents the protobuf message
    # Operation is NOT returned in the dict
    @staticmethod
    def protobuf_to_dict(protobuf_message:DatabaseEntryProto):
        return {
            "imsi": protobuf_message.imsi,
            "rand": protobuf_message.rand,
            "sqn": protobuf_message.sqn,
            "kasme": protobuf_message.kasme,
            "ck": protobuf_message.ck,
            "ik": protobuf_message.ik,
            "ak": protobuf_message.ak,
            "amf": protobuf_message.amf,
            "autn": protobuf_message.autn,
            "xres": protobuf_message.xres,
        }
    
    # Returns a new protobuf message from a dict
    @staticmethod
    def dict_to_protobuf(protobuf_dict:dict):
        return DatabaseEntryProto(
            imsi=protobuf_dict.get("imsi"),
            rand=protobuf_dict.get("rand"),
            sqn=protobuf_dict.get("sqn"),
            kasme=protobuf_dict.get("kasme"),
            ck=protobuf_dict.get("ck"),
            ik=protobuf_dict.get("ik"),
            ak=protobuf_dict.get("ak"),
            amf=protobuf_dict.get("amf"),
            autn=protobuf_dict.get("autn"),
            xres=protobuf_dict.get("xres"),
        )