import time

from dAuth.config import DatabaseManagerConfig
from dAuth.managers import DatabaseManager
from dAuth.proto.database_entry import DatabaseEntry

# Tests that that inserts into a real MongoDB are successful
# Also checks that all existing keys can be found and are accurate

def _insert_check(manager:DatabaseManager, entry:DatabaseEntry):
    manager.update_entry(entry)
    assert manager.get_entry(entry.key()).to_dict() == entry.to_dict()

def insert_test():
    print("Running insert tests")
    conf = DatabaseManagerConfig()
    conf.COLLECTION_NAME = "test_insert_collection"
    manager = DatabaseManager(conf)
    manager.collection.drop()
    manager.id_map = {}

    print(" Testing same key inserts")
    _insert_check(manager, DatabaseEntry({'imsi': '1', 'sqn':'1'}))
    _insert_check(manager, DatabaseEntry({'imsi': '1', 'sqn':'2'}))
    _insert_check(manager, DatabaseEntry({'imsi': '1', 'sqn':'3'}))
    _insert_check(manager, DatabaseEntry({'imsi': '1', 'sqn':'2'}))
    _insert_check(manager, DatabaseEntry({'imsi': '1', 'sqn':'1'}))
    _insert_check(manager, DatabaseEntry({'imsi': '1', 'sqn':'100'}))
    assert manager.get_all_keys() == ['1']
    
    print(" Testing multiple key inserts")
    _insert_check(manager, DatabaseEntry({'imsi': '1', 'sqn':'1'}))
    _insert_check(manager, DatabaseEntry({'imsi': '2', 'sqn':'2'}))
    _insert_check(manager, DatabaseEntry({'imsi': '3', 'sqn':'3'}))
    _insert_check(manager, DatabaseEntry({'imsi': '4', 'sqn':'2'}))
    _insert_check(manager, DatabaseEntry({'imsi': '5', 'sqn':'1'}))
    _insert_check(manager, DatabaseEntry({'imsi': '6', 'sqn':'100'}))
    assert set(manager.get_all_keys()) == set(['1', '2', '3', '4', '5', '6'])

    manager.collection.drop()
    print("Test Success")

def run_tests():
    try:
        insert_test()
    except Exception as e:
        print("Test Failed:", e)

if __name__ == "__main__":
    run_tests()