from dAuth.proto.database import DatabaseOperation
from dAuth.utils import random_string


# Used as a simple test of a database operation
# Should mimic behavior
class TestDatabaseOperation(DatabaseOperation):
    operations = ['i', 'u', 'd']

    # Expects dict with (at least) 'operation' and 'key' entries
    def __init__(self, protobuf_data):
        operation_type = protobuf_data.get("operation")
        operation_key = protobuf_data.get("key")
        operation_value = protobuf_data.get("value", {})

        if operation_type not in TestDatabaseOperation.operations:
            raise ValueError("Not a supported operation type - " + str(operation_type))

        if type(operation_key) is not str:
            raise ValueError("Operation Key must be a string - " + str(type(operation_key)))

        self.protobuf_data = protobuf_data


    def to_dict(self):
        return self.protobuf_data
    
    def key(self):
        return self.protobuf_data.get('key')

    def operation(self):
        return self.protobuf_data.get("operation")

    def remote(self):
        return self.protobuf_data.get("remote", False)

    def ownership(self):
        return self.protobuf_data.get("ownership")

    def set_remote(self, remote):
        self.protobuf_data['remote'] = remote

    def set_ownership(self, owner):
        self.protobuf_data['ownership'] = owner

    def set_id(self, new_id):
        self.protobuf_data['id'] = new_id

    def id(self):
        return self.protobuf_data['id']