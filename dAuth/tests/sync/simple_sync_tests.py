
from dAuth.managers import SyncManager, TestDatabaseManager, TestDistributedManager
from dAuth.proto.database_entry import DatabaseEntry
from dAuth.config import SyncManagerConfig

# Returns true if the entry has the listed 
def _check_entry(entry:DatabaseEntry, imsi, max_known_sqn, vectors):
    return entry.key() == imsi and\
        int(entry.get_max_current_sqn()) == int(max_known_sqn) and\
        entry.get_vectors() == vectors

# Tests basic key propagation
def test_simple_sync():
    conf = SyncManagerConfig()
    manager = SyncManager(conf)
    dist = TestDistributedManager()
    db = TestDatabaseManager()
    manager.set_managers(dist, db)
    # manager.set_logger(print)

    db.update_entry(DatabaseEntry({"imsi":'2', 'max_known_sqn':"1", "vectors": "[]"}))
    dist.update_entry(DatabaseEntry({"imsi":'1', 'max_known_sqn':"1", "vectors": "[]"}))

    assert db.get_all_keys() == {"2"}
    assert dist.get_all_keys() == {"1"}

    manager.report_all()  # sets all keys to reported
    manager.sync_reported()  # does the actual syncing

    assert db.get_all_keys() == {"1", "2"}
    assert dist.get_all_keys() == {"1", "2"}

    db.update_entry(DatabaseEntry({"imsi":'3', 'max_known_sqn':"1", "vectors": "[]"}))
    db.update_entry(DatabaseEntry({"imsi":'4', 'max_known_sqn':"1", "vectors": "[]"}))
    db.update_entry(DatabaseEntry({"imsi":'5', 'max_known_sqn':"1", "vectors": "[]"}))

    assert db.get_all_keys() == {"1", "2", "3", "4", "5"}
    assert dist.get_all_keys() == {"1", "2"}

    manager.report_update("4")
    manager.sync_reported()

    assert db.get_all_keys() == {"1", "2", "3", "4", "5"}
    assert dist.get_all_keys() == {"1", "2", "4"}

    manager.report_all()
    manager.sync_reported()

    assert db.get_all_keys() == {"1", "2", "3", "4", "5"}
    assert dist.get_all_keys() == {"1", "2", "3", "4", "5"}

# Tests a full overwrite given 
def test_overwrite_max_full():
    conf = SyncManagerConfig()
    manager = SyncManager(conf)
    dist = TestDistributedManager()
    db = TestDatabaseManager()
    manager.set_managers(dist, db)
    # manager.set_logger(print)

    db.update_entry(DatabaseEntry({"imsi":'1', 'max_known_sqn':"1", "vectors": '[{"sqn":"1"}]'}))
    db.update_entry(DatabaseEntry({"imsi":'2', 'max_known_sqn':"1", "vectors": '[{"sqn":"1"}]'}))
    db.update_entry(DatabaseEntry({"imsi":'3', 'max_known_sqn':"1", "vectors": '[{"sqn":"1"}]'}))

    dist.update_entry(DatabaseEntry({"imsi":'1', 'max_known_sqn':"2", "vectors": '[{"sqn":"2"}]'}))
    dist.update_entry(DatabaseEntry({"imsi":'2', 'max_known_sqn':"2", "vectors": '[{"sqn":"2"}]'}))
    dist.update_entry(DatabaseEntry({"imsi":'3', 'max_known_sqn':"2", "vectors": '[{"sqn":"2"}]'}))

    assert db.get_all_keys() == {"1", "2", "3"}
    assert dist.get_all_keys() == {"1", "2", "3"}

    for imsi in db.get_all_keys():
        assert _check_entry(db.get_entry(imsi), imsi, "1", [{'sqn':'1'}])
        assert _check_entry(dist.get_entry(imsi), imsi, "2", [{'sqn':'2'}])

    manager.report_all()
    manager.sync_reported()

    for imsi in db.get_all_keys():
        assert _check_entry(db.get_entry(imsi), imsi, "2", [{'sqn':'2'}])
        assert _check_entry(dist.get_entry(imsi), imsi, "2", [{'sqn':'2'}])

def test_overwrite_max_partial():
    conf = SyncManagerConfig()
    manager = SyncManager(conf)
    dist = TestDistributedManager()
    db = TestDatabaseManager()
    manager.set_managers(dist, db)
    # manager.set_logger(print)

    db.update_entry(DatabaseEntry({"imsi":'1', 'max_known_sqn':"2", "vectors": '[{"sqn":"2"}]'}))
    db.update_entry(DatabaseEntry({"imsi":'2', 'max_known_sqn':"1", "vectors": '[{"sqn":"1"}]'}))
    db.update_entry(DatabaseEntry({"imsi":'3', 'max_known_sqn':"1", "vectors": '[{"sqn":"1"}]'}))

    dist.update_entry(DatabaseEntry({"imsi":'1', 'max_known_sqn':"2", "vectors": '[{"sqn":"2"}]'}))
    dist.update_entry(DatabaseEntry({"imsi":'2', 'max_known_sqn':"2", "vectors": '[{"sqn":"2"}]'}))
    dist.update_entry(DatabaseEntry({"imsi":'3', 'max_known_sqn':"2", "vectors": '[{"sqn":"2"}]'}))

    assert db.get_all_keys() == {"1", "2", "3"}
    assert dist.get_all_keys() == {"1", "2", "3"}

    assert _check_entry(db.get_entry("1"), "1", "2", [{'sqn':'2'}])
    assert _check_entry(db.get_entry("2"), "2", "1", [{'sqn':'1'}])
    assert _check_entry(db.get_entry("3"), "3", "1", [{'sqn':'1'}])

    for imsi in db.get_all_keys():
        assert _check_entry(dist.get_entry(imsi), imsi, "2", [{'sqn':'2'}])

    manager.report_all()
    manager.sync_reported()

    for imsi in db.get_all_keys():
        assert _check_entry(db.get_entry(imsi), imsi, "2", [{'sqn':'2'}])
        assert _check_entry(dist.get_entry(imsi), imsi, "2", [{'sqn':'2'}])

def test_overwrite_vectors_full():
    conf = SyncManagerConfig()
    manager = SyncManager(conf)
    dist = TestDistributedManager()
    db = TestDatabaseManager()
    manager.set_managers(dist, db)
    # manager.set_logger(print)

    db.update_entry(DatabaseEntry({"imsi":'1', 'max_known_sqn':"2", "vectors": '[{"sqn":"1"}, {"sqn":"2"}]'}))
    db.update_entry(DatabaseEntry({"imsi":'2', 'max_known_sqn':"2", "vectors": '[{"sqn":"1"}, {"sqn":"2"}]'}))
    db.update_entry(DatabaseEntry({"imsi":'3', 'max_known_sqn':"2", "vectors": '[{"sqn":"1"}, {"sqn":"2"}]'}))

    dist.update_entry(DatabaseEntry({"imsi":'1', 'max_known_sqn':"2", "vectors": '[{"sqn":"2"}]'}))
    dist.update_entry(DatabaseEntry({"imsi":'2', 'max_known_sqn':"2", "vectors": '[{"sqn":"2"}]'}))
    dist.update_entry(DatabaseEntry({"imsi":'3', 'max_known_sqn':"2", "vectors": '[{"sqn":"2"}]'}))

    assert db.get_all_keys() == {"1", "2", "3"}
    assert dist.get_all_keys() == {"1", "2", "3"}

    for imsi in db.get_all_keys():
        assert _check_entry(db.get_entry(imsi), imsi, "2", [{'sqn':'1'}, {'sqn':'2'}])
        assert _check_entry(dist.get_entry(imsi), imsi, "2", [{'sqn':'2'}])

    manager.report_all()
    manager.sync_reported()

    for imsi in db.get_all_keys():
        assert _check_entry(db.get_entry(imsi), imsi, "2", [{'sqn':'2'}])
        assert _check_entry(dist.get_entry(imsi), imsi, "2", [{'sqn':'2'}])

def test_overwrite_vectors_partial():
    conf = SyncManagerConfig()
    manager = SyncManager(conf)
    dist = TestDistributedManager()
    db = TestDatabaseManager()
    manager.set_managers(dist, db)
    # manager.set_logger(print)

    db.update_entry(DatabaseEntry({"imsi":'1', 'max_known_sqn':"2", "vectors": '[{"sqn":"2"}]'}))
    db.update_entry(DatabaseEntry({"imsi":'2', 'max_known_sqn':"2", "vectors": '[{"sqn":"1"}, {"sqn":"2"}]'}))
    db.update_entry(DatabaseEntry({"imsi":'3', 'max_known_sqn':"2", "vectors": '[{"sqn":"1"}, {"sqn":"2"}]'}))

    dist.update_entry(DatabaseEntry({"imsi":'1', 'max_known_sqn':"2", "vectors": '[{"sqn":"2"}]'}))
    dist.update_entry(DatabaseEntry({"imsi":'2', 'max_known_sqn':"2", "vectors": '[{"sqn":"2"}]'}))
    dist.update_entry(DatabaseEntry({"imsi":'3', 'max_known_sqn':"2", "vectors": '[{"sqn":"2"}]'}))

    assert db.get_all_keys() == {"1", "2", "3"}
    assert dist.get_all_keys() == {"1", "2", "3"}

    db.update_entry(DatabaseEntry({"imsi":'1', 'max_known_sqn':"2", "vectors": '[{"sqn":"2"}]'}))
    db.update_entry(DatabaseEntry({"imsi":'2', 'max_known_sqn':"1", "vectors": '[{"sqn":"1"}, {"sqn":"2"}]'}))
    db.update_entry(DatabaseEntry({"imsi":'3', 'max_known_sqn':"1", "vectors": '[{"sqn":"1"}, {"sqn":"2"}]'}))

    for imsi in db.get_all_keys():
        assert _check_entry(dist.get_entry(imsi), imsi, "2", [{'sqn':'2'}])

    manager.report_all()
    manager.sync_reported()

    for imsi in db.get_all_keys():
        assert _check_entry(db.get_entry(imsi), imsi, "2", [{'sqn':'2'}])
        assert _check_entry(dist.get_entry(imsi), imsi, "2", [{'sqn':'2'}])

def test_mixed_max_full():
    conf = SyncManagerConfig()
    manager = SyncManager(conf)
    dist = TestDistributedManager()
    db = TestDatabaseManager()
    manager.set_managers(dist, db)
    # manager.set_logger(print)

    db.update_entry(DatabaseEntry({"imsi":'1', 'max_known_sqn':"2", "vectors": '[{"sqn":"2"}]'}))
    db.update_entry(DatabaseEntry({"imsi":'2', 'max_known_sqn':"1", "vectors": '[{"sqn":"1"}]'}))
    db.update_entry(DatabaseEntry({"imsi":'3', 'max_known_sqn':"2", "vectors": '[{"sqn":"2"}]'}))

    dist.update_entry(DatabaseEntry({"imsi":'1', 'max_known_sqn':"1", "vectors": '[{"sqn":"1"}]'}))
    dist.update_entry(DatabaseEntry({"imsi":'2', 'max_known_sqn':"2", "vectors": '[{"sqn":"2"}]'}))
    dist.update_entry(DatabaseEntry({"imsi":'3', 'max_known_sqn':"1", "vectors": '[{"sqn":"1"}]'}))

    assert db.get_all_keys() == {"1", "2", "3"}
    assert dist.get_all_keys() == {"1", "2", "3"}

    assert _check_entry(db.get_entry("1"), "1", "2", [{'sqn':'2'}])
    assert _check_entry(db.get_entry("2"), "2", "1", [{'sqn':'1'}])
    assert _check_entry(db.get_entry("3"), "3", "2", [{'sqn':'2'}])

    assert _check_entry(dist.get_entry("1"), "1", "1", [{'sqn':'1'}])
    assert _check_entry(dist.get_entry("2"), "2", "2", [{'sqn':'2'}])
    assert _check_entry(dist.get_entry("3"), "3", "1", [{'sqn':'1'}])

    manager.report_all()
    manager.sync_reported()

    for imsi in db.get_all_keys():
        assert _check_entry(db.get_entry(imsi), imsi, "2", [{'sqn':'2'}])
        assert _check_entry(dist.get_entry(imsi), imsi, "2", [{'sqn':'2'}])

def test_mixed_max_partial():
    conf = SyncManagerConfig()
    manager = SyncManager(conf)
    dist = TestDistributedManager()
    db = TestDatabaseManager()
    manager.set_managers(dist, db)
    # manager.set_logger(print)

    db.update_entry(DatabaseEntry({"imsi":'1', 'max_known_sqn':"2", "vectors": '[{"sqn":"2"}]'}))
    db.update_entry(DatabaseEntry({"imsi":'2', 'max_known_sqn':"1", "vectors": '[{"sqn":"1"}]'}))
    db.update_entry(DatabaseEntry({"imsi":'3', 'max_known_sqn':"2", "vectors": '[{"sqn":"2"}]'}))

    dist.update_entry(DatabaseEntry({"imsi":'1', 'max_known_sqn':"2", "vectors": '[{"sqn":"2"}]'}))
    dist.update_entry(DatabaseEntry({"imsi":'2', 'max_known_sqn':"2", "vectors": '[{"sqn":"2"}]'}))
    dist.update_entry(DatabaseEntry({"imsi":'3', 'max_known_sqn':"1", "vectors": '[{"sqn":"1"}]'}))

    assert db.get_all_keys() == {"1", "2", "3"}
    assert dist.get_all_keys() == {"1", "2", "3"}

    assert _check_entry(db.get_entry("1"), "1", "2", [{'sqn':'2'}])
    assert _check_entry(db.get_entry("2"), "2", "1", [{'sqn':'1'}])
    assert _check_entry(db.get_entry("3"), "3", "2", [{'sqn':'2'}])

    assert _check_entry(dist.get_entry("1"), "1", "2", [{'sqn':'2'}])
    assert _check_entry(dist.get_entry("2"), "2", "2", [{'sqn':'2'}])
    assert _check_entry(dist.get_entry("3"), "3", "1", [{'sqn':'1'}])

    manager.report_all()
    manager.sync_reported()

    for imsi in db.get_all_keys():
        assert _check_entry(db.get_entry(imsi), imsi, "2", [{'sqn':'2'}])
        assert _check_entry(dist.get_entry(imsi), imsi, "2", [{'sqn':'2'}])

def test_mixed_vectors_full():
    conf = SyncManagerConfig()
    manager = SyncManager(conf)
    dist = TestDistributedManager()
    db = TestDatabaseManager()
    manager.set_managers(dist, db)
    # manager.set_logger(print)

    db.update_entry(DatabaseEntry({"imsi":'1', 'max_known_sqn':"2", "vectors": '[{"sqn":"2"}]'}))
    db.update_entry(DatabaseEntry({"imsi":'2', 'max_known_sqn':"2", "vectors": '[{"sqn":"1", "sqn":"2"}]'}))
    db.update_entry(DatabaseEntry({"imsi":'3', 'max_known_sqn':"2", "vectors": '[{"sqn":"2"}]'}))

    dist.update_entry(DatabaseEntry({"imsi":'1', 'max_known_sqn':"2", "vectors": '[{"sqn":"1", "sqn":"2"}]'}))
    dist.update_entry(DatabaseEntry({"imsi":'2', 'max_known_sqn':"2", "vectors": '[{"sqn":"2"}]'}))
    dist.update_entry(DatabaseEntry({"imsi":'3', 'max_known_sqn':"2", "vectors": '[{"sqn":"1", "sqn":"2"}]'}))

    assert db.get_all_keys() == {"1", "2", "3"}
    assert dist.get_all_keys() == {"1", "2", "3"}

    assert _check_entry(db.get_entry("1"), "1", "2", [{'sqn':'2'}])
    assert _check_entry(db.get_entry("2"), "2", "2", [{'sqn':'1', "sqn":"2"}])
    assert _check_entry(db.get_entry("3"), "3", "2", [{'sqn':'2'}])

    assert _check_entry(dist.get_entry("1"), "1", "2", [{'sqn':'1', "sqn":"2"}])
    assert _check_entry(dist.get_entry("2"), "2", "2", [{'sqn':'2'}])
    assert _check_entry(dist.get_entry("3"), "3", "2", [{'sqn':'1', "sqn":"2"}])

    manager.report_all()
    manager.sync_reported()

    for imsi in db.get_all_keys():
        assert _check_entry(db.get_entry(imsi), imsi, "2", [{'sqn':'2'}])
        assert _check_entry(dist.get_entry(imsi), imsi, "2", [{'sqn':'2'}])

def test_mixed_vectors_partial():
    conf = SyncManagerConfig()
    manager = SyncManager(conf)
    dist = TestDistributedManager()
    db = TestDatabaseManager()
    manager.set_managers(dist, db)
    # manager.set_logger(print)

    db.update_entry(DatabaseEntry({"imsi":'1', 'max_known_sqn':"2", "vectors": '[{"sqn":"2"}]'}))
    db.update_entry(DatabaseEntry({"imsi":'2', 'max_known_sqn':"2", "vectors": '[{"sqn":"1", "sqn":"2"}]'}))
    db.update_entry(DatabaseEntry({"imsi":'3', 'max_known_sqn':"2", "vectors": '[{"sqn":"2"}]'}))

    dist.update_entry(DatabaseEntry({"imsi":'1', 'max_known_sqn':"2", "vectors": '[{"sqn":"2"}]'}))
    dist.update_entry(DatabaseEntry({"imsi":'2', 'max_known_sqn':"2", "vectors": '[{"sqn":"2"}]'}))
    dist.update_entry(DatabaseEntry({"imsi":'3', 'max_known_sqn':"2", "vectors": '[{"sqn":"1", "sqn":"2"}]'}))

    assert db.get_all_keys() == {"1", "2", "3"}
    assert dist.get_all_keys() == {"1", "2", "3"}

    assert _check_entry(db.get_entry("1"), "1", "2", [{'sqn':'2'}])
    assert _check_entry(db.get_entry("2"), "2", "2", [{'sqn':'1', "sqn":"2"}])
    assert _check_entry(db.get_entry("3"), "3", "2", [{'sqn':'2'}])

    assert _check_entry(dist.get_entry("1"), "1", "2", [{"sqn":"2"}])
    assert _check_entry(dist.get_entry("2"), "2", "2", [{'sqn':'2'}])
    assert _check_entry(dist.get_entry("3"), "3", "2", [{'sqn':'1', "sqn":"2"}])

    manager.report_all()
    manager.sync_reported()

    for imsi in db.get_all_keys():
        assert _check_entry(db.get_entry(imsi), imsi, "2", [{'sqn':'2'}])
        assert _check_entry(dist.get_entry(imsi), imsi, "2", [{'sqn':'2'}])

def run_test(test, test_name):
    try:
        print("Running", test_name)
        test()
        print("Test Success")
        print()
        return 1
    except Exception as e:
        print("Test Failed:", e)
        print()
        return 0

def run_all_tests():
    passed = 0
    passed += run_test(test_simple_sync, "test_simple_sync")
    passed += run_test(test_overwrite_max_full, "test_overwrite_max_full")
    passed += run_test(test_overwrite_max_partial, "test_overwrite_max_partial")
    passed += run_test(test_overwrite_vectors_full, "test_overwrite_vectors_full")
    passed += run_test(test_overwrite_vectors_partial, "test_overwrite_vectors_partial")
    passed += run_test(test_mixed_max_full, "test_mixed_max_full")
    passed += run_test(test_mixed_max_partial, "test_mixed_max_partial")
    passed += run_test(test_mixed_vectors_full, "test_mixed_vectors_full")
    passed += run_test(test_mixed_vectors_partial, "test_mixed_vectors_partial")

    print("Test passed: {}/{}".format(passed, 9))
    
if __name__ == "__main__":
    run_all_tests()