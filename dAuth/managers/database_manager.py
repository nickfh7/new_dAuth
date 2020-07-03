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


    def _start(self):
        # Set up triggers
        self.trigger_handler = TriggerHandler(self.client, self.conf.DATABASE_NAME, self.conf.COLLECTION_NAME, logger=self.log)
        self.trigger_handler.set_insert_callback(self._trigger_callback)
        self.trigger_handler.set_update_callback(self._trigger_callback)
        self.trigger_handler.set_delete_callback(self._trigger_callback)
        self.trigger_handler.start_triggers()

    def _stop(self):
        self.trigger_handler.stop_triggers()
        self.client.close()

    # Get the entry from system state
    def get_entry(self, key):
        return DatabaseEntry(self.collection.find_one({"imsi":key}))

    # Update the entry in the system state
    def update_entry(self, entry:DatabaseEntry):
        MongoDBOperations.insert(self.collection, entry)

    # Returns all key values from the system state
    def get_all_keys(self):
        return self.collection.distinct('imsi')

    def report_update(self, entry:DatabaseEntry):
        self.log("New update reported: " + str(entry.key()))

    def _trigger_callback(self, mongo_id):
        if mongo_id in self.id_map:
            data = self.collection.find_one({'imsi':self.id_map[mongo_id]})
            if data != None:
                self.report_update(DatabaseEntry(data))
