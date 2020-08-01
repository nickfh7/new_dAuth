from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.database import Collection

from dAuth.managers.interface import DatabaseManagerInterface
from dAuth.proto.database_entry import DatabaseEntry
from dAuth.config import DatabaseManagerConfig
from dAuth.database.trigger_handler import TriggerHandler
from dAuth.database.operations import MongoDBOperations


# Manages all database operations
# - Triggers on local changes and propagates to remote nodes
# - Executes operations from remote nodes
class DatabaseManager(DatabaseManagerInterface):
    client = None
    database = None
    collection = None

    def __init__(self, conf:DatabaseManagerConfig):
        super().__init__(conf)

        # Connect to database
        self.client = MongoClient(self.conf.HOST, self.conf.PORT)
        self.database = self.client[self.conf.DATABASE_NAME]
        self.collection = self.database[self.conf.COLLECTION_NAME]

        # Set index for imsi
        self.collection.create_index("imsi")

        # Map ids to imsis
        self.id_map = {}
        for doc in self.collection.find():
            self.id_map[doc['_id']] = doc.get('imsi')

        self.trigger_callback_func = None


    def _start(self):
        # Set up triggers
        self.trigger_handler = TriggerHandler(self.client, self.conf.DATABASE_NAME, self.conf.COLLECTION_NAME, logger=self.log)
        self.trigger_handler.set_insert_callback(self._trigger_callback_key)
        self.trigger_handler.set_update_callback(self._trigger_callback_id)
        self.trigger_handler.set_delete_callback(self._trigger_callback_id)
        self.trigger_handler.start_triggers()

    def _stop(self):
        self.trigger_handler.stop_triggers()
        self.client.close()

    # Get the entry from system state
    def get_entry(self, key):
        self.log("Getting entry with key: " + str(key))
        data = self.collection.find_one({"imsi":key})
        if data != None:
            return DatabaseEntry(data)
        return None

    # Update the entry in the system state
    def update_entry(self, entry:DatabaseEntry):
        self.log("Updating entry: " + str(entry.to_dict()))
        result_id = MongoDBOperations.insert(self.collection, entry)
        if result_id != None:
            self.id_map[result_id] = entry.key()

    # Returns all key values from the system state
    def get_all_keys(self):
        self.log("Retrieving all keys")
        return self.collection.distinct('imsi')

    def set_report_callback(self, callback_func):
        self.log("Report callback set")
        self.trigger_callback_func = callback_func

    def report_update(self, key):
        self.log("New update reported: " + str(key))
        if self.trigger_callback_func:
            self.trigger_callback_func(key)

    def _trigger_callback_key(self, mongo_id, key):
        self.log("Triggered on id: " + str(mongo_id) + " With key: " + str(key))
        if mongo_id in self.id_map:
            self.log(" Updating key")

        self.id_map[mongo_id] = key
        self.report_update(key)
            

    def _trigger_callback_id(self, mongo_id):
        self.log("Triggered on id: " + str(mongo_id))
        if mongo_id in self.id_map:
            self.report_update(self.id_map[mongo_id])

    def count(self):
        return self.collection.estimated_document_count()