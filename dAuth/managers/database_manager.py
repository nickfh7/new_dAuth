from pymongo import MongoClient

from dAuth.managers.interface import DatabaseManagerInterface
from dAuth.proto.database import DatabaseOperation
from dAuth.config import DatabaseManagerConfig
from dAuth.database.operations import MongoDBOperations
from dAuth.database.nextepc_handler import NextEPCHandler


# Manages all database operations
# - Triggers on local changes and propagates to remote nodes
# - Executes operations from remote nodes
class DatabaseManager(DatabaseManagerInterface):
    client = None
    database = None

    def __init__(self, conf:DatabaseManagerConfig, name=None):
        super().__init__(conf, name=name)

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
        if operation.ownership() is self.id:
            self.log("!!! Attempting to re-execute local operation, ignoring")
            return

        self.log("Executing operation from " + str(operation.ownership()))

        if operation.is_insert():
            self.log(" Doing insert operation with key: " + str(operation.key()))
            MongoDBOperations.insert(self.collection, operation)

        elif operation.is_update():
            self.log(" Doing update operation with key: " + str(operation.key()))
            MongoDBOperations.update(self.collection, operation)

        elif operation.is_delete():
            self.log(" Doing delete operation with key: " + str(operation.key()))
            MongoDBOperations.delete(self.collection, operation)

        else:
            self.log(" Bad operation type: " + str(operation.operation()))

    # Propagate an operation out via the distributed manager
    def new_local_operation(self, operation:DatabaseOperation):
        self.log("New local operation, sending to distributed manager")
        if self.distributed_manager:
            self.distributed_manager.propagate_operation(operation)
        else:
            self.log(" No distributed manager found, unable to propagate")

