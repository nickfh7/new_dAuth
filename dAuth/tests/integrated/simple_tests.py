
from dAuth.proto.database_entry import DatabaseEntry
from dAuth.central_manager import CentralManager
from dAuth.config import CentralManagerConfig,\
                         NetworkManagerConfig,\
                         DatabaseManagerConfig,\
                         DistributedManagerConfig,\
                         SyncManagerConfig

def simple_tests():
    cm_config = CentralManagerConfig()
    dbm_config = DatabaseManagerConfig()
    dstm_config = DistributedManagerConfig()
    sync_config = SyncManagerConfig()

    sync_config.SYNC_INTERVAL = 15

    cm_config.OUTPUT_DIR = "./output/testing/integrated_tests/simple"
    cm_config.LOGGING_ENABLED = True

    dbm_config.DATABASE_NAME = "test_db"
    dbm_config.COLLECTION_NAME = "simple_test_collection"

    dstm_config.BATCH_TIMEOUT = 0.5
    dstm_config.BATCH_SIZE = 10

    cm = CentralManager(cm_config)
    cm.init_managers(dbm_config, dstm_config, sync_config, None)
    cm.database_manager.collection.drop()

    cm.start()
    cm.stop()

if __name__ == "__main__":
    simple_tests()