import time
import threading

from dAuth.managers.interface import ManagerInterface
from dAuth.managers import DistributedManager, DatabaseManager
from dAuth.proto.database_entry import DatabaseEntry

# Sync Manager is responsible for syncing the
# Distributed and Database managers
class SyncManager(ManagerInterface):
    name = "Sync Manager"

    def __init__(self, conf):
        super().__init__(conf)
        self.distributed_manager = None
        self.database_manager = None
        self.sync_thread = None
        self.reported_updates = {}  # Used as an ordered set

    def set_managers(self, distributed_manager:DistributedManager,
                           database_manager:DatabaseManager):
        self.distributed_manager = distributed_manager
        self.database_manager = database_manager
        distributed_manager.set_report_callback(self.report_update)
        database_manager.set_report_callback(self.report_update)

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
        self.reported_updates[key] = None

    def sync(self, keys:set):
        for key in keys:
            self.sync_entry(key)

    def sync_reported(self):
        self.log("Syncing reported keys")
        reported_key_list = list(self.reported_updates.keys())
        keys_subset = set()

        for key in reported_key_list:
            if len(keys_subset) >= self.conf.SYNC_REPORTED_MAX:
                break

            self.reported_updates.pop(key)
            keys_subset.add(key)

        # debug
        self.log("Sync reported set size: " + str(len(keys_subset)))
        self.log("Sync reported set: " + str(keys_subset))

        self.sync(keys_subset)

    # Goes through the union of all keys bewteen managers
    # and syncs the corresponding entries
    def sync_all(self):
        self.log("Syncing all keys")

        all_keys = set()
        all_keys.update(self.distributed_manager.get_all_keys())
        all_keys.update(self.database_manager.get_all_keys())

        # debug
        l = list(all_keys)
        l.sort()
        self.log("Sync set size: " + str(len(l)))
        self.log("Sync set: " + str(l))

        # Add all available keys to the reported updates, to check them all
        self.reported_updates.update({}.fromkeys(all_keys, None))

    # Checks if the entry needs to be updated to the compare_to value
    # DOES NOT CHECK THE OTHER WAY AROUND
    def _needs_update(self, entry:DatabaseEntry, compare_to:DatabaseEntry):
        if entry == None:
            if compare_to == None:
                self.log("Both entries are None")
            else:
                self.log("Entry is None")
            return compare_to != None

        if entry != None and compare_to != None:
            self.log("Neither entry is None")
            return int(entry.to_dict()['sqn']) < int(compare_to.to_dict()['sqn'])

        self.log("Compare To entry is None")
        return False

    def _start(self):
        if not self.sync_thread:
            self.sync_thread = threading.Thread(target=self._sync_check)
            self.sync_thread.start()
    
    def _stop(self):
        self.sync_thread.join()

    def _sync_check(self):
        self.log("Sync checker entering")

        last_sync_all = time.time()
        last_sync_reported = time.time()
        while self._running:
            # update all keys
            if time.time() - last_sync_all > self.conf.SYNC_ALL_INTERVAL:
                self.reported_updates.clear()
                self.sync_all()
                last_sync_all = time.time()
                last_sync_reported = time.time()

            # update reported keys
            elif time.time() - last_sync_reported > self.conf.SYNC_REPORTED_INTERVAL:
                self.sync_reported()
                last_sync_reported = time.time()

            time.sleep(self.conf.SYNC_CHECK_DELAY)

        self.log("Sync checker exiting")