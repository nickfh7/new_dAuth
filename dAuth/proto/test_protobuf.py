from dAuth.proto.database_protobuf import DatabaseOperation

# Used as a simple operation type
class TestDatabaseOperation(DatabaseOperation):
    operations = ['i', 'u', 'd']

    # Expects dict of the form {operation_type: <str>, operation_key: <str>, operation_value: <dict>}
    def __init__(self, protobuf_data):
        operation_type = protobuf_data.get("operation_type")
        operation_key = protobuf_data.get("operation_key")
        operation_value = protobuf_data.get("operation_value", {})

        if operation_type not in TestDatabaseOperation.operations:
            raise ValueError("Not a supported operation type - " + str(operation_type))

        if type(operation_value) is not dict:
            raise ValueError("Operation Key must be a string - " + str(type(operation_key)))

        if type(operation_value) is not dict:
            raise ValueError("Operation Value must be a dict - " + str(type(operation_value)))

        self.operation_type = operation_type
        self.operation_key = operation_key
        self.operation_value = operation_value
        self.remote = protobuf_data.get("remote", False)

    def to_dict(self):
        return self.operation_value
    
    def key(self):
        return self.operation_key

    def operation(self):
        return self.operation_type

    def from_remote(self):
        return self.remote