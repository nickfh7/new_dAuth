import copy

from dAuth.managers.interface import DistributedManagerInterface, DatabaseManagerInterface, ManagerInterface
from dAuth.proto.database_entry import DatabaseEntry
from dAuth.config import DatabaseManagerConfig, DistributedManagerConfig


# Test manager that emulates a basic database setup
# Can effectively be used as both distributed and database managers
class TestDatabaseManager(ManagerInterface):
    name = "Test DB Manager"

    def _init__(self):
        self.db = {}
        self.report_callback = None

    def set_report_callback(self, callback):
        self.report_callback = callback

    # Get the entry from system state
    def get_entry(self, key):
        return self.db.get(key)

    # Update the entry in the system state
    def update_entry(self, entry:DatabaseEntry):
        self.db[operation.key()] = entry.get_serialized_message()

    # Returns all key values from the system state
    def get_all_keys(self):
        return self.db.keys()

    def report_update(self, entry:DatabaseEntry):
        self.report_callback(entry)


class TestDistributedManager(TestDatabaseManager):
    name = "Test Dist Manager"
