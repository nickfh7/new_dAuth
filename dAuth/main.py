import signal
import sys
import threading

from dAuth.ccellular import CCellular
from dAuth.managers import NetworkManager, TestManager, DistributedManager, DatabaseManager
from network.services import LoggingClient
from dAuth.config import CCellularConfig, NetworkManagerConfig, DatabaseManagerConfig, DistributedManagerConfig
from dAuth.parser import parse_args


# Sets up a dAuth node to run indefinitely
def main():
    # Set up config objects and parsing
    cc_config = CCellularConfig()
    nwm_config = None # NetworkManagerConfig()
    dbm_config = DatabaseManagerConfig()
    dstm_config = DistributedManagerConfig()
    parse_args(cc_config=cc_config, nwm_config=nwm_config, dbm_config=dbm_config, dstm_config=dstm_config)

    # Create the central manager
    cc = CCellular(cc_config)

    # Add the network manager and grab logging function
    # nwm = NetworkManager(nwm_config)
    # cc.logger = nwm.get_service(LoggingClient.name).log
    # cc.add_manager(nwm)

    # Add database manager
    dbm = DatabaseManager(dbm_config)
    cc.add_manager(dbm)

    # Add distributed manager
    dstm = DistributedManager(dstm_config)
    cc.add_manager(dstm)

    # Set the run function
    cc_config.RUN_FUNCTION = dstm.run_main

    # Start running CCellular
    cc.start()  # Should block until ctrl-c
    cc.stop()
