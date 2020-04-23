from pymongo.database import Collection

from dAuth.proto.database import DatabaseOperation


# TODO: figure out if it is ok keep an object id generated at insert for update and delete

# Static class for performing database operations on a MongoDB
# All details for how an operation occurs should be done here
class MongoDBOperations:
    @staticmethod
    def insert(collection:Collection, operation:DatabaseOperation):
        collection.insert_one(operation.to_dict())


    @staticmethod
    def update(collection:Collection, operation:DatabaseOperation):
        collection.update_one(operation.get_filter(), operation.get_update_data())


    @staticmethod
    def delete(collection:Collection, operation:DatabaseOperation):
        collection.delete_one(operation.get_filter())
