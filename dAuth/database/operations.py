from pymongo.database import Collection

from dAuth.proto.database_entry import DatabaseEntry


# TODO: figure out if it is ok keep an object id generated at insert for update and delete

# Static class for performing database operations on a MongoDB
# All details for how an operation occurs should be done here
class MongoDBOperations:
    @staticmethod
    def insert(collection:Collection, entry:DatabaseEntry):
        collection.update_one(entry.get_filter(), {"$set":entry.get_data()}, upsert=True)


    @staticmethod
    def update(collection:Collection, entry:DatabaseEntry):
        collection.update_one(entry.get_filter(), entry.get_data())


    @staticmethod
    def delete(collection:Collection, entry:DatabaseEntry):
        collection.delete_one(entry.get_filter())
