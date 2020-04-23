# This file contains wrappers for proto messages
# Wrappers are designed to:
#  - Hold onto to a protobuf message
#  - Provide helper functions (i.e. to dict for database)
#  - Abstract away protobuf fields


# Represents a generic database operation
# Contains the protobuf message with the relevant data
class DatabaseOperation:
    # Constants for operation type
    INSERT = "i"
    UPDATE = "u"
    DELETE = "d"

    # Can be constructed with a message or a dict
    def __init__(self, protobuf_data):
        if type(protobuf_data) is dict:
            self.protobuf_message = self.dict_to_protobuf(protobuf_data)
        else:
            self.protobuf_message = protobuf_data

    # Returns a dictionary with the protobuf message data
    def to_dict(self):
        return self.protobuf_to_dict(self.protobuf_message)
    
    # Returns the field of the protobuf message that is used as the key
    def key(self):
        pass

    # Return the type of database operation
    def operation(self):
        pass

    # Returns if this message originated non-locally
    def remote(self):
        pass

    # Returns the name of the dAuth node this operation originated from
    def ownership(self):
        pass

    # Returns a unique identifier for this transaction
    def id(self):
        pass


    # Operation types
    def is_insert(self):
        return self.operation() is self.INSERT

    def is_update(self):
        return self.operation() is self.UPDATE

    def is_delete(self):
        return self.operation() is self.DELETE


    # Set attributes
    def set_remote(self, set_to):
        pass

    def set_ownership(self, owner):
        pass

    def set_id(self, new_id):
        pass


    # Returns a dict that represents the protobuf message
    @staticmethod
    def protobuf_to_dict(protobuf_message):
        pass
    
    # Returns a new protobuf message from a dict
    @staticmethod
    def dict_to_protobuf(protobuf_dict):
        pass
