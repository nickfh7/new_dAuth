import threading

from dAuth.central_manager import CentralManager
from dAuth.config import CentralManagerConfig,\
                         NetworkManagerConfig,\
                         DatabaseManagerConfig,\
                         DistributedManagerConfig,\
                         SyncManagerConfig
from dAuth.parser import parse_args


# Sets up a dAuth node to run indefinitely
def main():
    # Set up config objects and parsing
    cm_config = CentralManagerConfig()
    nwm_config = NetworkManagerConfig()
    dbm_config = DatabaseManagerConfig()
    dstm_config = DistributedManagerConfig()
    sync_config = SyncManagerConfig()
    parse_args(cm_config=cm_config, nwm_config=nwm_config, dbm_config=dbm_config, dstm_config=dstm_config)

    # Create the central manager
    cm = CentralManager(cm_config)
    cm.init_managers(dbm_config, dstm_config, sync_config, nwm_config)

    # Start running dAuth
    cm.start()  # Should block until ctrl-c
    cm.stop()


# Should not use this, use the installed command instead
if __name__ == "__main__":
    main()
