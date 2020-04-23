import signal
import sys
import threading

from dAuth.ccellular import CCellular
from dAuth.managers import NetworkManager, TestManager, TestDatabaseManager, TestDistributedManager
from network.services import LoggingClient
from dAuth.config import CCellularConfig, NetworkManagerConfig, DatabaseManagerConfig, DistributedManagerConfig
from dAuth.parser import parse_args

def main():
    # Set up config objects and parsing
    cc_config = CCellularConfig()
    nwm_config = NetworkManagerConfig()
    dbm_config = DatabaseManagerConfig()
    dstm_config = DistributedManagerConfig()
    parse_args(cc_config=cc_config, nwm_config=nwm_config, dbm_config=dbm_config, dstm_config=dstm_config)

    # Create the central manager
    cc = CCellular(cc_config)

    # Add the network manager and grab logging function
    nwm = NetworkManager(nwm_config)
    cc.logger = nwm.get_service(LoggingClient.name).log
    cc.add_manager(nwm)

    # Add database manager
    dbm = TestDatabaseManager(dbm_config)
    cc.add_manager(dbm)

    # Add distributed manager
    dstm = TestDistributedManager(dstm_config)
    cc.add_manager(dstm)

    # Start running CCellular
    print("Starting dAuth")
    cc.start()

    # Create end function
    def stop_server(signal, frame):
        print('\nStopping...')
        cc.stop()
        sys.exit(0)

    # Wait until interrupt
    signal.signal(signal.SIGINT, stop_server)
    print("Ctr-c to stop")
    forever = threading.Event()
    forever.wait()