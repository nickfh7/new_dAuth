import time
import threading
import sys

from dAuth.utils import random_string
from dAuth.proto.database_entry import DatabaseEntry
from dAuth.central_manager import CentralManager
from dAuth.config import CentralManagerConfig,\
                         NetworkManagerConfig,\
                         DatabaseManagerConfig,\
                         DistributedManagerConfig,\
                         SyncManagerConfig


def transaction_poll(tps:float):
    num_nodes = 5
    nodes = []

    for i in range(num_nodes):
        cm_config = CentralManagerConfig()
        dbm_config = DatabaseManagerConfig()
        dstm_config = DistributedManagerConfig()
        sync_config = SyncManagerConfig()
        nwkm_config = NetworkManagerConfig()

        nwkm_config.GRPC_HOST = "test_node_" + str(i)
        nwkm_config.GRPC_PORT = str(13127 + i)

        sync_config.SYNC_REPORTED_INTERVAL = 1
        sync_config.SYNC_REPORTED_MAX = 100
        sync_config.SYNC_ALL_INTERVAL = 100000
        sync_config.SYNC_INITIAL = False

        cm_config.OUTPUT_DIR = "./output/testing/exp/node_" + str(i)
        cm_config.LOGGING_ENABLED = True
        cm_config.REMOTE_LOGGING_ENABLED = True

        dbm_config.DATABASE_NAME = "test_db"
        dbm_config.COLLECTION_NAME = "exp_test_collection_" + str(i)

        dstm_config.BATCH_TIMEOUT = 5
        dstm_config.BATCH_SIZE = 10
        dstm_config.VALIDATOR_URL = 'tcp://localhost:' + str(4004 + i)
        dstm_config.CLIENT_URL = 'localhost:' + str(8008 + i)

        cm = CentralManager(cm_config)
        cm.init_managers(dbm_config, dstm_config, sync_config, nwkm_config)
        cm.database_manager.collection.drop()

        nodes.append(cm)

    for node in nodes:
        threading.Thread(target=node.start, daemon=True).start()

    print("Starting transaction polling in 3 seconds")
    time.sleep(3)

    try:
        rate = 1/tps
        start = time.time()

        while True:
            entry = DatabaseEntry({"imsi": random_string(15), 'max_known_sqn': "1", "vectors": '[{"sqn":"1"}]'})
            nodes[0].database_manager.update_entry(entry)
            time.sleep(rate)

    except KeyboardInterrupt:
        pass


    print("Stopping and cleaning up")

    for node in nodes:
        node.stop()
        node.database_manager.collection.drop()

    time.sleep(2)
    print("Done")
    exit(0)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        transaction_poll(float(sys.argv[1]))
    else:
        print("Specify transactions per second (as int or float)")