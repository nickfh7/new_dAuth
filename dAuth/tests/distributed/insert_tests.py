import threading
import time

from dAuth.managers.distributed_manager import DistributedManager
from dAuth.config import DistributedManagerConfig
from dAuth.proto.database_entry import DatabaseEntry

# Tests basic functionality on a single node
def test_inserts():
    conf = DistributedManagerConfig()
    conf.BATCH_SIZE = 10
    conf.BATCH_TIMEOUT = 1
    manager = DistributedManager(conf)
    iterations = 10

    # Spawn a thread to do a series of inserts
    thread = threading.Thread(target=periodic_insert, args=(manager, iterations), daemon=True)

    manager.start()
    thread.start()
    manager.run_main()
    manager.stop()

def periodic_insert(manager:DistributedManager, iterations):
    time.sleep(1)
    print("Running insert tests")
    try:
        print(" Testing inserts and reads")
        for i in range(iterations):
            manager.update_entry(DatabaseEntry({"imsi": str(i), "sqn": str(i) }))

        time.sleep(2)

        for i in range(iterations):
            entry = manager.get_entry(str(i))
            assert entry != None
            assert entry.key() == str(i) and entry.to_dict()['sqn'] == str(i)

        print(" Testing updates and reads")
        for i in range(iterations):
            manager.update_entry(DatabaseEntry({"imsi": str(i), "sqn": str(i+10) }))

        time.sleep(2)

        for i in range(iterations):
            entry =  manager.get_entry(str(i))
            assert entry != None
            assert entry.key() == str(i) and entry.to_dict()['sqn'] == str(i+10)

        assert manager.get_all_keys() == set([str(i) for i in range(iterations)])
        
        print("Test Success")
            
    except AssertionError as e:
        print("Failed Test:", e)

    print("(^c to end)")
    
    
if __name__ == "__main__":
    test_inserts()