from mongotriggers import MongoTrigger

from dAuth.proto.database import DatabaseOperation
from dAuth.proto.database_pb2 import OldDatabaseData

# Creates triggers on a mongo database and reports any new operations
class NextEPCHandler:
    # Takes in client, db and collection names, and a trigger callback
    # Trigger callback should be used AFTER the data has been processed into a DatabaseOperation
    # Optional logger function to capture logs
    def __init__(self, client, db_name, collection_name, trigger_callback, ownership, logger=None):
        self.client = client
        self.database = client[db_name]
        self.triggers = MongoTrigger(client)
        self.trigger_callback = trigger_callback
        self.ownership = ownership
        self.logger = logger  # used to send logs back to manager

        self.db_name = db_name
        self.collection_name = collection_name

        # Set trigger on collection
        self.triggers.register_insert_trigger(self._handle_insert, db_name=db_name, collection_name=collection_name)
        self.triggers.register_update_trigger(self._handle_update, db_name=db_name, collection_name=collection_name)
        self.triggers.register_delete_trigger(self._handle_delete, db_name=db_name, collection_name=collection_name)

        # These are used because ownership and remote cannot be determined via triggers for updates and deletes
        self.pending_updates = {}
        self.pending_deletes = {}


    # Start watching for new operations
    def start_triggers(self):
        self.log("Setting triggers on " + str(self.db_name) + " -> " + str(self.collection_name))
        self.triggers.tail_oplog()

    # Stop watching and release triggers
    def stop_triggers(self):
        self.log("Stopping triggers")
        self.triggers.stop_tail()


    # Add the key, owner, and update data of a pending delete from remote origin
    def add_pending_update(self, operation:DatabaseOperation):
        if operation.key() in self.pending_updates:
            found_owner, found_data = self.pending_updates[operation.key()]

            # Check for existing pending updates
            if operation.ownership() == found_owner and operation.get_data() == found_data:
                self.log("!!! An existing pending update is pending again")
            else:
                self.log("!!! New update for the same key is pending")

        self.pending_updates[operation.key()] = operation.ownership(), operation.get_data()

    # Add the key and owner of a pending delete from remote origin
    def add_pending_delete(self, operation:DatabaseOperation):
        if operation.key() in self.pending_deletes:
            self.log("!!! An existing pending delete is pending again, from same owner: " +\
                 str(self.pending_deletes[operation.key()] == operation.ownership()))

        self.pending_deletes[operation.key()] = operation.ownership()


    # --- Trigger functions ---
    # Build operation based on op type, called by mongo triggers
    def _handle_insert(self, op_document):
        self.log("Triggered on insert: " + str(op_document))

        operation = DatabaseOperation(protobuf_data=op_document, op_type=DatabaseOperation.INSERT)

        self._handle_operation(operation)
        
    def _handle_update(self, op_document):
        self.log("Triggered on update: " + str(op_document))

        operation = DatabaseOperation(protobuf_data=op_document, op_type=DatabaseOperation.UPDATE)

        # See if this was a pending remote update, set ownership as necessary
        if operation.key() in self.pending_updates:

            ownership, data = self.pending_updates[operation.key()]

            # Check for exact match of update data
            if data == operation.get_data():
                operation.set_ownership(ownership)
                operation.set_remote(True)
                del self.pending_updates[operation.key()]

        self._handle_operation(operation)

    def _handle_delete(self, op_document):
        self.log("Triggered on delete: " + str(op_document))
    
        operation = DatabaseOperation(protobuf_data=op_document, op_type=DatabaseOperation.DELETE)
    
        # See if this was a pending remote delete, set ownership as necessary
        if operation.key() in self.pending_deletes:
            ownership = self.pending_deletes[operation.key()]
            operation.set_ownership(ownership)
            operation.set_remote(True)
            del self.pending_deletes[operation.key()]

        self._handle_operation(operation)

    # Called by all triggers, determines if operation should be propagated
    def _handle_operation(self, operation:DatabaseOperation):
        # check if this is a local operation
        if not operation.remote():
            # set ownership and remote
            operation.set_ownership(self.ownership)
            operation.set_remote(True)

            # pass this up to the manager
            self.trigger_callback(operation)
        
        # if not, don't propagate
        else:
            self.log(" Remote operation, ignoring")


    def log(self, message):
        if self.logger:
            self.logger("(NextEPCHandler) " + message)