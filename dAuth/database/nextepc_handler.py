from mongotriggers import MongoTrigger

from dAuth.proto.database import DatabaseOperation

# Creates triggers on a mongo database and reports any new operations
class NextEPCHandler:
    # Takes in client, db and collection names, and a trigger callback
    # Trigger callback should be used AFTER the data has been processed into a DatabaseOperation
    def __init__(self, client, db_name, collection_name, trigger_callback, ownership, logger=None):
        self.client = client
        self.database = client[db_name]
        self.triggers = MongoTrigger(client)
        self.trigger_callback = trigger_callback
        self.ownership = ownership
        self.logger = logger

        self.db_name = db_name
        self.collection_name = collection_name

        # Set trigger on collection
        self.triggers.register_insert_trigger(self._handle_insert, db_name=db_name, collection_name=collection_name)
        self.triggers.register_update_trigger(self._handle_update, db_name=db_name, collection_name=collection_name)
        self.triggers.register_delete_trigger(self._handle_delete, db_name=db_name, collection_name=collection_name)


    # Start watching for new operations
    def start_triggers(self):
        self.log("Setting triggers on " + str(self.db_name) + " -> " + str(self.collection_name))
        self.triggers.tail_oplog()

    # Stop watching and release triggers
    def stop_triggers(self):
        self.log("Stopping triggers")
        self.triggers.stop_tail()


    # --- Trigger functions ---
    # Build operation based on op type, pass up to manager if not remote
    def _handle_insert(self, op_document):
        self.log("Triggered on insert: " + str(op_document))

        operation = DatabaseOperation(protobuf_data=op_document, op_type=DatabaseOperation.INSERT)
        self._handle_operation(operation)
        
    def _handle_update(self, op_document):
        self.log("Triggered on update: " + str(op_document))

        operation = DatabaseOperation(protobuf_data=op_document, op_type=DatabaseOperation.UPDATE)
        self._handle_operation(operation)

    def _handle_delete(self, op_document):
        self.log("Triggered on delete: " + str(op_document))
    
        operation = DatabaseOperation(protobuf_data=op_document, op_type=DatabaseOperation.DELETE)
        self._handle_operation(operation)

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