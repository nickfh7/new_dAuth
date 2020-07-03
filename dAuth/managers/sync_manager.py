from dAuth.managers.interface import ManagerInterface
from dAuth.managers import DistributedManager, DatabaseManager
from dAuth.proto.database_entry import DatabaseEntry

# TODO: Add a periodic syncer

# Sync Manager is responsible for syncing the
# Distributed and Database managers
class SyncManager(ManagerInterface):
    name = "Sync Manager"

    def __init__(self, conf):
        super().__init__(conf)
        self.distributed_manager = None
        self.database_manager = None

    # Syncs a single entry
    def sync_entry(self, key):
        database_entry = self.database_manager.get_entry(key)
        distributed_entry = self.distributed_manager.get_entry(key)

        # Distributed entry is more up to date
        if self._needs_update(database_entry, distributed_entry):
            self.database_manager.update_entry(distributed_entry)

        # Database entry is more up to data
        elif self._needs_update(distributed_entry, database_entry):
            self.distributed_manager.update_entry(database_entry)

    def report_update(self, key):
        pass

    # Goes through the union of all keys bewteen managers
    # and syncs the corresponding entries
    def sync_all(self):
        self.log("Syncing all keys")

        all_keys = set()
        all_keys.update(self.distributed_manager.get_all_keys())
        all_keys.update(self.database_manager.get_all_keys())

        for key in all_keys:
            self.sync_entry

    # Checks if the operation
    def _needs_update(self, entry:DatabaseEntry, compare_to:DatabaseEntry):
        pass # TODO