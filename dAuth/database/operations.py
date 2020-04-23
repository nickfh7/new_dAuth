from pymongo.database import Collection

# TODO: figure out if it is ok keep an object id generated at insert for update and delete

# Static class for performing database operations on a MongoDB
class MongoDBOperations:
    @staticmethod
    def insert(collection:Collection, data:dict):
        collection.insert_one(data)


    @staticmethod
    def update(collection:Collection, data:dict):
        collection.update_one(data)


    @staticmethod
    def delete(collection:Collection, data:dict):
        collection.delete_one(data)
