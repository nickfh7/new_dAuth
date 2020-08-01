import copy

from dAuth.proto.database_entry import DatabaseEntry


# Test manager that emulates a basic database setup
# Can effectively be used as both distributed and database managers
class TestDatabaseManager:
    name = "Test DB Manager"

    def __init__(self):
        self.db = {}
        self.report_callback = None

    def start(self):
        pass

    def stop(self):
        pass

    def set_report_callback(self, callback):
        self.report_callback = callback

    # Get the entry from system state
    def get_entry(self, key):
        if key in self.db:
            return DatabaseEntry(self.db.get(key))
        return None

    # Update the entry in the system state
    def update_entry(self, entry:DatabaseEntry):
        self.db[entry.key()] = entry.get_serialized_message()
        self.report_update(entry.key())

    # Returns all key values from the system state
    def get_all_keys(self):
        return set(self.db.keys())

    def report_update(self, key):
        self.report_callback(key)

    def count(self):
        return len(self.db.keys())

class TestDistributedManager(TestDatabaseManager):
    name = "Test Dist Manager"

    def __init__(self):
        super().__init__()
        self.report_callback = []

    def set_report_callback(self, callback):
        self.report_callback.append(callback)

    def report_update(self, key):
        for callback in self.report_callback:
            callback(key)

    def run_main(self):
        pass