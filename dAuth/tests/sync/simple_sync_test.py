
from dAuth.managers import SyncManager, TestDatabaseManager, TestDistributedManager
from dAuth.proto.database_entry import DatabaseEntry
from dAuth.config import SyncManagerConfig

def simple_sync_test():
    print
    conf = SyncManagerConfig()
    manager = SyncManager(conf)
    dist = TestDistributedManager()
    db = TestDatabaseManager()
    manager.set_managers(dist, db)

    try:
        db.update_entry(DatabaseEntry({"imsi":'2', 'sqn':"1"}))
        dist.update_entry(DatabaseEntry({"imsi":'1', 'sqn':"1"}))

        assert db.get_all_keys() == {"2"}
        assert dist.get_all_keys() == {"1"}

        manager.sync_all()

        assert db.get_all_keys() == {"1", "2"}
        assert dist.get_all_keys() == {"1", "2"}

        db.update_entry(DatabaseEntry({"imsi":'3', 'sqn':"1"}))
        db.update_entry(DatabaseEntry({"imsi":'4', 'sqn':"1"}))
        db.update_entry(DatabaseEntry({"imsi":'5', 'sqn':"1"}))

        assert db.get_all_keys() == {"1", "2", "3", "4", "5"}
        assert dist.get_all_keys() == {"1", "2"}

        db.report_update("4")

        assert db.get_all_keys() == {"1", "2", "3", "4", "5"}
        assert dist.get_all_keys() == {"1", "2", "4"}

        manager.sync_all()

        assert db.get_all_keys() == {"1", "2", "3", "4", "5"}
        assert dist.get_all_keys() == {"1", "2", "3", "4", "5"}
    
        print("Test Success")
    except Exception as e:
        print("Test Failed:", e)

if __name__ == "__main__":
    simple_sync_test()