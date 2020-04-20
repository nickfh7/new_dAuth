# This file contains wrappers for proto messages
# Wrappers are designed to:
#  - Hold onto to a protobuf message
#  - Provide helper functions (i.e. to dict for database)
#  - Abstract protobuf fields


# Represents a generic database operation
# Contains the protobuf message with the relevant data
class DatabaseOperation:
    # Can be constructed with a message or a dict
    def __init__(self, protobuf_data=None):
        if type(protobuf_data) is dict:
            self.protobuf_message = self.dict_to_protobuf(protobuf_message)
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
    def from_remote(self):
        pass


    # Returns a dict that represents the protobuf message
    @staticmethod
    def protobuf_to_dict(protobuf_message):
        pass
    
    # Returns a new protobuf message from a dict
    @staticmethod
    def dict_to_protobuf(protobuf_dict):
        pass
