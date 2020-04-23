from mongotriggers import MongoTrigger

from dAuth.proto.database_proto import DatabaseOperation

# Creates triggers on a mongo database and reports any new operations
class NextEPCHandler:
    # Takes in client, db and collection names, and a trigger callback
    # Trigger callback should be used AFTER the data has been processed into a DatabaseOperation
    def __init__(self, client, db_name, collection_name, trigger_callback, logger=None):
        self.client = client
        self.database = client[db_name]
        self.triggers = MongoTrigger(client)
        self.logger = logger

        # Set trigger on collection
        self.log("Setting triggers on " + str(db_name) + " -> " + str(collection_name))
        self.triggers.register_insert_trigger(self._handle_insert, db_name=db_name, collection_name=collection_name)
        self.triggers.register_update_trigger(self._handle_update, db_name=db_name, collection_name=collection_name)
        self.triggers.register_delete_trigger(self._handle_delete, db_name=db_name, collection_name=collection_name)


    # Start watching for new operations
    def start_triggers(self):
        self.triggers.tail_oplog()

    # Stop watching and release triggers
    def stop_triggers(self):
        self.triggers.stop_tail()


    # --- Trigger functions ---

    def _handle_insert(self):
        self.log("Triggered on insert")

    def _handle_update(self):
        self.log("Triggered on update")

    def _handle_delete(self):
        self.log("Triggered on delete")


    def log(self, message):
        if self.logger:
            self.logger("(NextEPCHandler) " + message)