from mongotriggers import MongoTrigger

# Creates triggers on a mongo database and reports any new operations
class TriggerHandler:
    # Takes in client, db name, and collection name
    # Optional logger function to capture logs
    def __init__(self, client, db_name, collection_name, logger=None):
        self.client = client
        self.database = client[db_name]
        self.triggers = MongoTrigger(client)
        self.logger = logger  # used to send logs back to manager

        self.db_name = db_name
        self.collection_name = collection_name

        # Set trigger on collection
        self.triggers.register_insert_trigger(self._handle_insert, db_name=db_name, collection_name=collection_name)
        self.triggers.register_update_trigger(self._handle_update, db_name=db_name, collection_name=collection_name)
        self.triggers.register_delete_trigger(self._handle_delete, db_name=db_name, collection_name=collection_name)

        # Trigger callbacks
        self.insert_callback = None
        self.update_callback = None
        self.delete_callback = None


    # Start watching for new operations
    def start_triggers(self):
        self.log("Setting triggers on " + str(self.db_name) + " -> " + str(self.collection_name))
        self.triggers.tail_oplog()

    # Stop watching and release triggers
    def stop_triggers(self):
        self.log("Stopping triggers")
        self.triggers.stop_tail()


    def set_insert_callback(self, insert_callback):
        self.log("Setting insert callback")
        self.insert_callback = insert_callback

    def set_update_callback(self, update_callback):
        self.log("Setting update callback")
        self.update_callback = update_callback

    def set_delete_callback(self, delete_callback):
        self.log("Setting delete callback")
        self.delete_callback = delete_callback


    # --- Trigger functions ---
    # Build operation based on op type, called by mongo triggers
    def _handle_insert(self, op_document):
        self.log("Triggered on insert")
        self.insert_callback(op_document['o']['_id'], op_document['o'].get('imsi'))
        
    def _handle_update(self, op_document):
        self.log("Triggered on update")
        self.update_callback(op_document['o2']['_id'])

    def _handle_delete(self, op_document):
        self.log("Triggered on delete <!!! NOT SUPPORTED !!!>")
        self.delete_callback(op_document['o']['_id'])

    def log(self, message):
        if self.logger:
            self.logger("(TriggerHandler) " + message)