from pymongo import MongoClient
from pymongo.errors import PyMongoError

from dAuth.managers.interface import DatabaseManagerInterface
from dAuth.proto.database import DatabaseOperation
from dAuth.config import DatabaseManagerConfig
from dAuth.database.operations import MongoDBOperations
from dAuth.database.operations_cli import do_insert, do_update, do_delete
from dAuth.database.nextepc_handler import NextEPCHandler


# Manages all database operations
# - Triggers on local changes and propagates to remote nodes
# - Executes operations from remote nodes
class DatabaseManager(DatabaseManagerInterface):
    client = None
    database = None

    def __init__(self, conf:DatabaseManagerConfig):
        super().__init__(conf)

    def _start(self):
        conf = self.conf

        # Connect to database
        self.client = MongoClient(conf.HOST, conf.PORT)
        self.database = self.client[conf.DATABASE_NAME]
        self.collection = self.database[conf.COLLECTION_NAME]
        self.log("Connected to database: " + self.conf.DATABASE_NAME)

        # Create trigger handler and start triggers
        self.trigger_handler = NextEPCHandler(client=self.client, 
                                              db_name=conf.DATABASE_NAME,
                                              collection_name=conf.COLLECTION_NAME, 
                                              ownership=self.id,
                                              trigger_callback=self.new_local_operation,
                                              logger=self.log)
        self.trigger_handler.start_triggers()

        # Get the distributed manager
        self.distributed_manager = self.get_manager(conf.DISTRIBUTED_MANAGER_NAME)

    def _stop(self):
        self.trigger_handler.stop_triggers()
        self.client.close()

    # Execute an operation, presumably from another dAuth node
    def execute_operation(self, operation:DatabaseOperation):
        if operation.ownership() == self.id:
            self.log("!!! Attempting to re-execute local operation, ignoring")
            return

        self.log("Executing operation from " + str(operation.ownership()))

        try:
            if operation.is_insert():
                self.log(" Doing insert operation with key: " + str(operation.key()))

                MongoDBOperations.insert(self.collection, operation)

            elif operation.is_update():
                # Add to pending updates
                self.trigger_handler.add_pending_update(operation)

                self.log(" Doing update operation with key: " + str(operation.key()))
                MongoDBOperations.update(self.collection, operation)

            elif operation.is_delete():
                # Add to pending deletes
                self.trigger_handler.add_pending_delete(operation)

                self.log(" Doing delete operation with key: " + str(operation.key()))
                MongoDBOperations.delete(self.collection, operation)

            else:
                self.log(" Bad operation type: " + str(operation.operation()))
        except PyMongoError as e:
            self.log(" Error during operation: " + str(e))

    # Propagate an operation out via the distributed manager
    def new_local_operation(self, operation:DatabaseOperation):
        self.log("New local operation ({}), sending to distributed manager"\
            .format("insert" if operation.is_insert() else\
                    "update" if operation.is_update() else\
                    "delete"))

        # Log a size comparison with the old message size
        if operation.old_op:
            self.log(" Size comparison in bytes (new/old): {0}/{1}, old is {2:.3f}x larger"\
                .format(str(operation.size()), str(operation.old_op.ByteSize()), operation.old_op.ByteSize() / operation.size()))

        if self.distributed_manager:
            self.distributed_manager.propagate_operation(operation)
        else:
            self.log(" No distributed manager found, unable to propagate")


    # Debug / test functions (ignore normal checks and logs)
    # Meant to simulate outside operations
    def database_insert(self, key:str, data:dict):
        try:
            do_insert(self.collection, key, data)
        except Exception as e:
            self.log("database_insert failed: " + str(e))

    def database_update(self, key:str, data:dict):
        try:
            do_update(self.collection, key, data)
        except Exception as e:
            self.log("database_update failed: " + str(e))
        
    def database_delete(self, key:str):
        try:
            do_delete(self.collection, key)
        except Exception as e:
            self.log("database_delete failed: " + str(e))

    def database_get(self, key:str):
        try:
            # Try to get op document, return only relevant data
            res = self.collection.find({"_id":key})
            if res is not None:
                try:
                    return res[0]
                except IndexError:
                    return None
        except Exception as e:
            self.log("database_get failed: " + str(e))
        

