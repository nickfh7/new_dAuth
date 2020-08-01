
from dAuth.tests.performance.performance_tests import run_performance_tests
from dAuth.central_manager import CentralManager
from dAuth.proto.database_entry import DatabaseEntry
from dAuth.managers import TestDistributedManager, DatabaseManager, SyncManager
from dAuth.config import CentralManagerConfig,\
                         NetworkManagerConfig,\
                         DatabaseManagerConfig,\
                         DistributedManagerConfig,\
                         SyncManagerConfig


def run_database_tests():
    print("Running database performance tests")
    num_nodes = 5
    cm_list = []

    tdm = TestDistributedManager()

    for i in range(num_nodes):
        print("Running database performance test")
        cm_config = CentralManagerConfig()
        sync_config = SyncManagerConfig()
        dbm_config = DatabaseManagerConfig()

        sync_config.SYNC_REPORTED_INTERVAL = 5
        sync_config.SYNC_REPORTED_MAX = 1000
        sync_config.SYNC_ALL_INTERVAL = 1000

        dbm_config.COLLECTION_NAME = "test_insert_" + str(i)

        cm_config.OUTPUT_DIR = "./output/testing/performance_tests/baseline/node_" + str(i)
        cm_config.LOGGING_ENABLED = False

        cm = CentralManager(cm_config)

        cm.database_manager = DatabaseManager(dbm_config)
        cm.database_manager.set_logger(cm._double_log)
        cm.database_manager.collection.drop()
        
        cm.distributed_manager = tdm

        cm.sync_manager = SyncManager(sync_config)
        cm.sync_manager.set_logger(cm._double_log)
        cm.sync_manager.set_managers(cm.distributed_manager, cm.database_manager)

        cm_list.append(cm)

    results = run_performance_tests(cm_list)
    print("Results:", results)

    for cm in cm_list:
        cm.stop()

if __name__ == "__main__":
    run_database_tests()