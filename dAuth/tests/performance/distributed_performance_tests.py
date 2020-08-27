from dAuth.tests.performance.performance_tests import run_performance_tests
from dAuth.central_manager import CentralManager
from dAuth.proto.database_entry import DatabaseEntry
from dAuth.managers import DistributedManager, TestDatabaseManager, SyncManager
from dAuth.config import CentralManagerConfig,\
                         NetworkManagerConfig,\
                         DatabaseManagerConfig,\
                         DistributedManagerConfig,\
                         SyncManagerConfig

def run_distributed_tests():
    print("Running distributed performance tests")
    num_nodes = 5
    cm_list = []

    for i in range(num_nodes):
        cm_config = CentralManagerConfig()
        sync_config = SyncManagerConfig()
        dstm_config = DistributedManagerConfig()

        sync_config.SYNC_REPORTED_INTERVAL = 2.5
        sync_config.SYNC_REPORTED_MAX = 100
        sync_config.SYNC_ALL_INTERVAL = 1000

        dstm_config.BATCH_TIMEOUT = 5
        dstm_config.BATCH_SIZE = 20
        dstm_config.VALIDATOR_URL = 'tcp://localhost:' + str(4004 + i)
        dstm_config.CLIENT_URL = 'localhost:' + str(8008 + i)

        cm_config.OUTPUT_DIR = "./output/testing/performance_tests/baseline/node_" + str(i)
        cm_config.LOGGING_ENABLED = False

        cm = CentralManager(cm_config)
        cm.database_manager = TestDatabaseManager()
        cm.distributed_manager = DistributedManager(dstm_config)
        cm.distributed_manager.set_logger(cm._double_log)
        cm.sync_manager = SyncManager(sync_config)
        cm.sync_manager.set_logger(cm._double_log)
        cm.sync_manager.set_managers(cm.distributed_manager, cm.database_manager)

        cm_list.append(cm)

    results = run_performance_tests(cm_list)
    print("Results:", results)


if __name__ == "__main__":
    run_distributed_tests()