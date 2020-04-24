import json

from dAuth.proto.database_pb2 import DatabaseData

# This file contains wrappers for proto messages
# Wrappers are designed to:
#  - Hold onto to a protobuf message
#  - Provide helper functions (i.e. make dict for database)
#  - Abstract away protobuf fields


# Represents a generic database operation
# Contains the protobuf message with the relevant data
class DatabaseOperation:
    # Constants for operation type
    INSERT = DatabaseData.INSERT
    UPDATE = DatabaseData.UPDATE
    DELETE = DatabaseData.DELETE

    # Can be constructed with a message or a dict
    # Op_type must be specified with a dict
    # Op_code is used for testing (specifically the simulated distributed system)
    def __init__(self, protobuf_data, op_type=None, op_id=None):
        # if the type is an op document (dict), build based on data and op type
        if type(protobuf_data) is dict:
            # check the op type is valid
            if op_type is None:
                raise ValueError("op_type must be specified with a dict")
            if op_type not in [self.INSERT, self.DELETE, self.UPDATE]:
                raise ValueError("op_type is not valid")

            data = {}

            # use all data for an insert message
            if op_type is self.INSERT:
                data = protobuf_data['o']

            # use _id and insert values for update
            elif op_type is self.UPDATE:
                data["_id"] = protobuf_data['o2']["_id"]
                data["update_data"] = protobuf_data["o"]

                # Remove the internal info
                if "$v" in data["update_data"]:
                    del data["update_data"]["$v"]

            # use only _id for delete
            elif op_type is self.DELETE:
                data["_id"] = protobuf_data["o"]["_id"]
                
            # build protobuf message from data
            self.protobuf_message = self.dict_to_protobuf(data, op_type)


        # can also build from a protomessage
        elif type(protobuf_data) is DatabaseData:
            self.protobuf_message = protobuf_data
        
        else:
            raise ValueError("protobuf data is invalid")

        # Used for debugging / testing
        self.op_id = op_id

    # Returns a dictionary with the protobuf message data
    def to_dict(self):
        return self.protobuf_to_dict(self.protobuf_message)
    
    # Returns the field of the protobuf message that is used as the key
    def key(self):
        return self.protobuf_message._id

    # Return the type of database operation
    def operation(self):
        return self.protobuf_message.operation

    # Returns if this message originated non-locally
    def remote(self):
        return self.protobuf_message.remote

    # Returns the name of the dAuth node this operation originated from
    def ownership(self):
        return self.protobuf_message.ownership


    # Operation types
    def is_insert(self):
        return self.operation() is self.INSERT

    def is_update(self):
        return self.operation() is self.UPDATE

    def is_delete(self):
        return self.operation() is self.DELETE


    # Set attributes
    def set_remote(self, remote):
        if remote is None:
            raise ValueError("remote value must not be None")
        self.protobuf_message.remote = remote

    def set_ownership(self, ownership):
        if ownership is None:
            raise ValueError("ownership value must not be None")
        self.protobuf_message.ownership = ownership


    # Generate a filter based on operation type
    def get_filter(self):
        # insert doesn't need a filter
        if self.is_insert():
            return None
        
        # _id is all that is needed for update and delete
        if self.is_update():
            return {"_id": self.key()}
        
        if self.is_delete():
            return {"_id": self.key()}

    # If operation is update, return relevant update info
    def get_update_data(self):
        if self.is_update():
            return json.loads(self.protobuf_message.update_data)

    # Returns a dict that represents the protobuf message
    # Operation is NOT returned in the dict
    @staticmethod
    def protobuf_to_dict(protobuf_message):
        return {
            "_id": protobuf_message._id,
            "remote": protobuf_message.remote,
            "ownership": protobuf_message.ownership,
            "imsi": protobuf_message.imsi,
            "security": json.loads(protobuf_message.security),  # Security is a nested dict
            "update_data": json.loads(protobuf_message.update_data)
        }
    
    # Returns a new protobuf message from a dict
    @staticmethod
    def dict_to_protobuf(protobuf_dict, op_type):
        return DatabaseData(
            operation=op_type,
            _id=protobuf_dict.get("_id"),
            remote=protobuf_dict.get("remote"),
            ownership=protobuf_dict.get("ownership"),
            imsi=protobuf_dict.get("imsi"),
            security=json.dumps(protobuf_dict.get("security")),  # Security is a nested dict
            update_data=json.dumps(protobuf_dict.get("update_data"))
        )
