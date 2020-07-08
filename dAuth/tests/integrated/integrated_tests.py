import time
import threading

from dAuth.proto.database_entry import DatabaseEntry
from dAuth.central_manager import CentralManager
from dAuth.config import CentralManagerConfig,\
                         NetworkManagerConfig,\
                         DatabaseManagerConfig,\
                         DistributedManagerConfig,\
                         SyncManagerConfig

def integrated_tests():
    num_nodes = 5
    nodes = []

    for i in range(num_nodes):
        cm_config = CentralManagerConfig()
        dbm_config = DatabaseManagerConfig()
        dstm_config = DistributedManagerConfig()
        sync_config = SyncManagerConfig()

        sync_config.SYNC_REPORTED_INTERVAL = 1
        sync_config.SYNC_REPORTED_MAX = 100
        sync_config.SYNC_ALL_INTERVAL = 100

        cm_config.OUTPUT_DIR = "./output/testing/integrated_tests/node_" + str(i)
        cm_config.LOGGING_ENABLED = False

        dbm_config.DATABASE_NAME = "test_db"
        dbm_config.COLLECTION_NAME = "integrated_test_collection_" + str(i)

        dstm_config.BATCH_TIMEOUT = 10
        dstm_config.BATCH_SIZE = 100
        dstm_config.VALIDATOR_URL = 'tcp://localhost:' + str(4004 + i)
        dstm_config.CLIENT_URL = 'localhost:' + str(8008 + i)

        cm = CentralManager(cm_config)
        cm.init_managers(dbm_config, dstm_config, sync_config, None)
        cm.database_manager.collection.drop()

        nodes.append(cm)

    for node in nodes:
        threading.Thread(target=node.start, daemon=True).start()

    print("Starting integration tests in 3 seconds")
    time.sleep(3)

    try:
        num_inserts = 200
        rate = 0.01
        start = time.time()
        check_time = time.time()

        for i in range(num_inserts):
            nodes[0].database_manager.update_entry(DatabaseEntry({'imsi':str(i), 'sqn':'1'}))
            time.sleep(rate)

            if time.time() - check_time >= 1:
                check_time = time.time()
                time_passed = time.time() - start

                print("Current state (during operations):")
                for node in nodes:
                    count = node.database_manager.collection.count()
                    print(" total:", count, "rate: {0:.3f}".format(count/time_passed))
                print()

        print("Operations finished")

        # Wait for propagations to finish
        done = False
        while not done:
            done = True
            time.sleep(2)
            time_passed = time.time() - start

            # check the current status of the other dbs
            print("Current state")
            for node in nodes:
                count = node.database_manager.collection.estimated_document_count()
                done &= count >= num_inserts
                print(" total:", count, "rate: {0:.3f}".format(count/time_passed))
            print()
        
        print("Test finished successfully")
    
    except KeyboardInterrupt:
        print("Skipping test...")

    print("Stopping and cleaning up")

    for node in nodes:
        node.stop()
        node.database_manager.collection.drop()

    time.sleep(2)
    print("Done")
    exit(0)

if __name__ == "__main__":
    integrated_tests()