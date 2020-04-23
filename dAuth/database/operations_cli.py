import argparse
import json
from pymongo import MongoClient

from dAuth.config import DatabaseManagerConfig
from dAuth.database.operations import MongoDBOperations
from dAuth.proto.database_proto import DatabaseOperation


# Execute the operation with provided data
def do_operation(collection, op_type, data):
    if op_type is DatabaseOperation.INSERT:
        MongoDBOperations.insert(collection, data)

    elif op_type is DatabaseOperation.UPDATE:
        MongoDBOperations.update(collection, data)

    elif op_type is DatabaseOperation.DELETE:
        MongoDBOperations.delete(collection, data)

    else:
        raise ValueError("Unknown operation value")


# Read args from command line and run on database collection
def main():
    op_choices = [DatabaseOperation.INSERT, DatabaseOperation.UPDATE, DatabaseOperation.DELETE]
    parser = argparse.ArgumentParser(description="Small utility to perform a database operation on a MongoDB."
                                                 " Optional args will use insert and config defaults")
    parser.add_argument("--op-type", default='i', choices=op_choices, help="operation type to perform")
    parser.add_argument("--db-host", default="localhost", help="MongoDB host")
    parser.add_argument("--db-port", default=DatabaseManagerConfig.PORT, type=int, help="MongoDB port")
    parser.add_argument("--db-name", default=DatabaseManagerConfig.DATABASE_NAME, help="Database name to get collection from")
    parser.add_argument("--db-coll", default=DatabaseManagerConfig.COLLECTION_NAME, help="Collection name to operate on")
    parser.add_argument("data", type=json.loads, help="Data to use in the operation in the form of a dictionary")
    args = parser.parse_args()

    print(args)
    if type(args.data) is not dict:
        raise ValueError("Data must be in the form of dictionary")

    # Create a client for the db and get the collection
    client = MongoClient(args.db_host, args.db_port)
    db = client[args.db_name]
    collection = db[args.db_coll]

    do_operation(collection, args.op_type, args.data)


if __name__ == "__main__":
    main()