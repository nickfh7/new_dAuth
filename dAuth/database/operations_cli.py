import argparse
import json
import copy
from pymongo import MongoClient

from dAuth.config import DatabaseManagerConfig
from dAuth.database.operations import MongoDBOperations
from dAuth.proto.database_entry import DatabaseEntry


# Command line utility for executing operations on the Mongo database
# Uses the same operation functions as the database manager


# Simple wrapper functions for producing and executing operations
def do_insert(collection, entry:DatabaseEntry):
    MongoDBOperations.insert(collection, entry)

def do_delete(collection, entry:DatabaseEntry):
    MongoDBOperations.delete(collection, entry)


# Read args from command line and run on database collection
def main(args_in=None):
    op_choices = ['i', 'd']
    parser = argparse.ArgumentParser(description="Small utility to perform a database operation on a MongoDB."
                                                 " Optional args will use insert and config defaults")
    parser.add_argument("--op-type", default="i", choices=op_choices, help="operation type to perform")
    parser.add_argument("--db-host", default="localhost", help="MongoDB host")
    parser.add_argument("--db-port", default=DatabaseManagerConfig.PORT, type=int, help="MongoDB port")
    parser.add_argument("--db-name", default=DatabaseManagerConfig.DATABASE_NAME, help="Database name to get collection from")
    parser.add_argument("--db-coll", default=DatabaseManagerConfig.COLLECTION_NAME, help="Collection name to operate on")
    parser.add_argument("data", type=json.loads, help="Data to use in the operation in the form of a dictionary")

    args = parser.parse_args(args_in)

    if type(args.data) is not dict:
        raise ValueError("Data must be in the form of dictionary")

    # Create a client for the db and get the collection
    client = MongoClient(args.db_host, args.db_port)
    db = client[args.db_name]
    collection = db[args.db_coll]

    data = args.data
    entry = DatabaseEntry(args.data)
    if args.op_type == 'i':
        do_insert(collection, entry)
    elif args.op_type == 'd':
        do_delete(collection, entry)


if __name__ == "__main__":
    main()