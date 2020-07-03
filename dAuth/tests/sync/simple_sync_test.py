
from dAuth.managers import SyncManager, TestDatabaseManager, TestDistributedManager
from dAuth.proto.database_entry import DatabaseEntry
from dAuth.config import SyncManagerConfig

def simple_sync_test():
    conf = SyncManagerConfig()
    manager = SyncManager(conf)
    dist = TestDistributedManager()
    db = TestDatabaseManager()
    manager.set_managers(dist, db)

    db.update_entry(DatabaseEntry({"imsi":'2', 'sqn':"1"}))
    dist.update_entry(DatabaseEntry({"imsi":'1', 'sqn':"1"}))
    dist.update_entry(DatabaseEntry({"imsi":'2', 'sqn':"2"}))
    db.update_entry(DatabaseEntry({"imsi":'1', 'sqn':"2"}))

    print(dist.name, '-', dist.get_all_keys())
    print(dist.name, '-', dist.get_entry('1').to_dict())
    print(dist.name, '-', dist.get_entry('2').to_dict())

    print(db.name, '-', db.get_all_keys())
    print(db.name, '-', db.get_entry('1').to_dict())
    print(db.name, '-', db.get_entry('2').to_dict())

    print("--- Syncing ---")
    manager.sync_all()

    print(dist.name, '-', dist.get_all_keys())
    print(dist.name, '-', dist.get_entry('1').to_dict())
    print(dist.name, '-', dist.get_entry('2').to_dict())

    print(db.name, '-', db.get_all_keys())
    print(db.name, '-', db.get_entry('1').to_dict())
    print(db.name, '-', db.get_entry('2').to_dict())

if __name__ == "__main__":
    simple_sync_test()