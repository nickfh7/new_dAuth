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
    thread = threading.Thread(target=periodic_insert, args=(manager, iterations))

    manager.start()
    thread.start()
    manager.run_main()
    manager.stop()

def periodic_insert(manager:DistributedManager, iterations):
    for i in range(iterations):
        manager.update_entry(DatabaseEntry({'o': {"imsi": str(i), "rand": str(i*100) }}))

    time.sleep(3)

    for i in range(iterations):
        operation =  manager.get_entry(str(i))
        print("CHECKING:", operation.get_data())

    # Update data
    for i in range(iterations):
        manager.update_entry(DatabaseEntry({'o': {"imsi": str(i), "rand": str(i*101) }}))

    time.sleep(3)

    for i in range(iterations+2):
        operation =  manager.get_entry(str(i))
        print("CHECKING:", operation.get_data())



if __name__ == "__main__":
    test_inserts()